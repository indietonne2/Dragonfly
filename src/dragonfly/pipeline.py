"""
Author: Thomas Fischer (TFITConsult)
Version: 2.0
What this file does: High-level pipeline for Sentinel-2 NBR and dNBR overlays.
Filename: pipeline.py
Pathname: /workspace/Dragonfly/src/dragonfly/pipeline.py
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import rasterio
from rasterio.enums import Resampling

from .data_access import SentinelStacConnector, StacItem
from .processing import calculate_dnbr, calculate_nbr, classify_dnbr
from .viz import raster_overlay


@dataclass
class RasterProduct:
    path: Path
    array: np.ndarray
    transform: rasterio.Affine
    crs: str


@dataclass
class NBRProducts:
    nir: RasterProduct
    swir: RasterProduct
    nbr: RasterProduct


@dataclass
class NBRRunResult:
    pre: NBRProducts
    post: NBRProducts
    dnbr: RasterProduct
    severity: RasterProduct | None = None


class NBRPipeline:
    """Pipeline that searches Sentinel-2, downloads bands, and produces OSM overlays."""

    def __init__(self, connector: SentinelStacConnector | None = None) -> None:
        self.connector = connector or SentinelStacConnector()

    def _load_raster(self, path: Path, *, scale_reflectance: bool = True) -> RasterProduct:
        with rasterio.open(path) as dataset:
            array = dataset.read(1, out_dtype="float32")
            if scale_reflectance:
                array = array / 10000.0
            return RasterProduct(
                path=path,
                array=array,
                transform=dataset.transform,
                crs=str(dataset.crs),
            )

    def _resample_to_match(self, source: RasterProduct, target: RasterProduct) -> RasterProduct:
        with rasterio.open(source.path) as dataset:
            data = dataset.read(
                1,
                out_shape=(
                    dataset.count,
                    target.array.shape[0],
                    target.array.shape[1],
                ),
                resampling=Resampling.bilinear,
            )[0]
            transform = dataset.transform * dataset.transform.scale(
                (dataset.width / data.shape[-1]), (dataset.height / data.shape[-2])
            )
        return RasterProduct(path=source.path, array=data, transform=transform, crs=source.crs)

    def _compute_nbr(self, nir: RasterProduct, swir: RasterProduct) -> RasterProduct:
        if nir.array.shape != swir.array.shape:
            swir = self._resample_to_match(swir, nir)
        nbr = calculate_nbr(nir.array, swir.array)
        return RasterProduct(path=swir.path, array=nbr, transform=nir.transform, crs=nir.crs)

    def _fetch_item(self, geometry: dict, window: tuple[str, str], cloud_cover: int) -> StacItem:
        items = self.connector.search(
            geometry=geometry,
            start=window[0],
            end=window[1],
            cloud_cover=cloud_cover,
            limit=1,
        )
        if not items:
            raise RuntimeError("No Sentinel-2 items found for requested window and AOI")
        return items[0]

    def _build_cloud_mask(
        self,
        scl: RasterProduct,
        target: RasterProduct,
        cloudy_classes: Iterable[int] = (8, 9, 10, 11),
    ) -> np.ndarray:
        if scl.array.shape != target.array.shape:
            scl = self._resample_to_match(scl, target)
        return np.isin(scl.array, cloudy_classes)

    def download_and_prepare(
        self,
        geometry: dict,
        pre_window: tuple[str, str],
        post_window: tuple[str, str],
        target_dir: Path,
        cloud_cover: int = 5,
        bands: Iterable[str] = ("B08", "B12", "SCL"),
        apply_cloud_mask: bool = True,
        cloudy_classes: Iterable[int] = (8, 9, 10, 11),
    ) -> NBRRunResult:
        target_dir.mkdir(parents=True, exist_ok=True)

        pre_item = self._fetch_item(geometry, pre_window, cloud_cover)
        post_item = self._fetch_item(geometry, post_window, cloud_cover)

        pre_paths = self.connector.download_bands(pre_item, bands, target_dir / "pre")
        post_paths = self.connector.download_bands(post_item, bands, target_dir / "post")

        pre_nir = self._load_raster(pre_paths["B08"])
        pre_swir = self._load_raster(pre_paths["B12"])
        post_nir = self._load_raster(post_paths["B08"])
        post_swir = self._load_raster(post_paths["B12"])

        if apply_cloud_mask and "SCL" in pre_paths and "SCL" in post_paths:
            pre_scl = self._load_raster(pre_paths["SCL"], scale_reflectance=False)
            post_scl = self._load_raster(post_paths["SCL"], scale_reflectance=False)

            pre_mask = self._build_cloud_mask(pre_scl, pre_nir, cloudy_classes)
            post_mask = self._build_cloud_mask(post_scl, post_nir, cloudy_classes)

            pre_nir.array[pre_mask] = np.nan
            pre_swir.array[pre_mask] = np.nan
            post_nir.array[post_mask] = np.nan
            post_swir.array[post_mask] = np.nan

        pre_nbr = self._compute_nbr(pre_nir, pre_swir)
        post_nbr = self._compute_nbr(post_nir, post_swir)
        dnbr_array = calculate_dnbr(pre_nbr.array, post_nbr.array)
        dnbr = RasterProduct(path=target_dir / "dnbr.tif", array=dnbr_array, transform=pre_nbr.transform, crs=pre_nbr.crs)

        severity_array = classify_dnbr(dnbr_array)
        severity = RasterProduct(
            path=target_dir / "severity.tif",
            array=severity_array,
            transform=pre_nbr.transform,
            crs=pre_nbr.crs,
        )

        return NBRRunResult(
            pre=NBRProducts(nir=pre_nir, swir=pre_swir, nbr=pre_nbr),
            post=NBRProducts(nir=post_nir, swir=post_swir, nbr=post_nbr),
            dnbr=dnbr,
            severity=severity,
        )

    def compute_statistics(self, result: NBRRunResult) -> dict[str, float]:
        """Compute burn area statistics from a dNBR result."""

        dnbr = result.dnbr.array
        valid_dnbr = dnbr[~np.isnan(dnbr)]

        total_pixels = valid_dnbr.size
        burned_pixels = np.sum(valid_dnbr > 0.10)
        high_severity = np.sum(valid_dnbr > 0.66)

        pixel_area_km2 = 100 / 1e6  # 10m resolution -> 100 m^2 per pixel

        return {
            "total_area_km2": total_pixels * pixel_area_km2,
            "burned_area_km2": burned_pixels * pixel_area_km2,
            "burned_percentage": 100 * burned_pixels / total_pixels if total_pixels > 0 else 0.0,
            "high_severity_km2": high_severity * pixel_area_km2,
            "high_severity_percentage": 100 * high_severity / total_pixels if total_pixels > 0 else 0.0,
        }

    def to_folium_map(self, dnbr: RasterProduct, bounds: tuple[float, float, float, float]):
        """Create a folium map ready for OpenStreetMap overlay."""

        return raster_overlay(dnbr.array, bounds=bounds, name="dNBR")
