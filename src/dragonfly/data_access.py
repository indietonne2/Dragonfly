"""
Author: Thomas Fischer (TFITConsult)
Version: 2.0
What this file does: Sentinel-2 STAC connector for retrieving NBR-ready bands.
Filename: data_access.py
Pathname: /workspace/Dragonfly/src/dragonfly/data_access.py
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests


@dataclass
class StacItem:
    id: str
    assets: dict
    geometry: dict


class SentinelStacConnector:
    """Minimal STAC connector for Copernicus Data Space."""

    def __init__(
        self,
        base_url: str = "https://catalogue.dataspace.copernicus.eu/stac",
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()

    def search(
        self,
        geometry: dict,
        start: str,
        end: str,
        collections: Iterable[str] = ("sentinel-2-l2a",),
        cloud_cover: int = 5,
        limit: int = 10,
    ) -> list[StacItem]:
        """Search STAC for Sentinel-2 items covering the AOI and date range."""

        payload = {
            "collections": list(collections),
            "intersects": geometry,
            "datetime": f"{start}/{end}",
            "limit": limit,
            "query": {"eo:cloud_cover": {"lt": cloud_cover}},
        }
        response = self.session.post(f"{self.base_url}/search", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return [StacItem(id=feat["id"], assets=feat["assets"], geometry=feat["geometry"]) for feat in data.get("features", [])]

    def download_asset(self, asset_href: str, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with self.session.get(asset_href, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            with destination.open("wb") as out:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    out.write(chunk)
        return destination

    def download_bands(self, item: StacItem, bands: Iterable[str], target_dir: Path) -> dict[str, Path]:
        downloaded: dict[str, Path] = {}
        for band in bands:
            asset_key = f"{band}" if band in item.assets else f"B{band}"
            if asset_key not in item.assets:
                raise KeyError(f"Asset {band} not found in item {item.id}")
            href = item.assets[asset_key]["href"]
            path = target_dir / f"{item.id}_{band}.tif"
            downloaded[band] = self.download_asset(href, path)
        return downloaded

    def export_search(self, items: list[StacItem], path: Path) -> Path:
        """Write a search result collection to disk for reproducibility."""

        path.write_text(json.dumps([item.__dict__ for item in items], indent=2))
        return path
