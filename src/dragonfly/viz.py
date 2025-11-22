"""Visualization helpers for folium / OpenStreetMap overlays."""
from __future__ import annotations

from typing import Iterable

import folium
import numpy as np

from .processing import DEFAULT_DNBR_COLORMAP, colorize, normalize_for_overlay


def raster_overlay(
    array: np.ndarray,
    bounds: tuple[float, float, float, float],
    tiles: str = "OpenStreetMap",
    opacity: float = 0.65,
    colormap: Iterable[tuple[float, tuple[int, int, int]]] = DEFAULT_DNBR_COLORMAP,
    name: str = "dNBR",
) -> folium.Map:
    """Render a folium map with a raster overlay.

    Args:
        array: 2D NBR or dNBR raster.
        bounds: Tuple of (min_lon, min_lat, max_lon, max_lat) in WGS84.
        tiles: Base map layer.
        opacity: Overlay opacity.
        colormap: Color stops for visualization.
        name: Layer name for the overlay.
    """

    min_lon, min_lat, max_lon, max_lat = bounds
    normalized = normalize_for_overlay(array)
    rgba = colorize(normalized, colormap)

    center = [(min_lat + max_lat) / 2, (min_lon + max_lon) / 2]
    fmap = folium.Map(location=center, tiles=tiles, zoom_start=10)

    folium.raster_layers.ImageOverlay(
        name=name,
        image=rgba,
        bounds=[(min_lat, min_lon), (max_lat, max_lon)],
        opacity=opacity,
        mercator_project=True,
    ).add_to(fmap)

    folium.LayerControl().add_to(fmap)
    return fmap
