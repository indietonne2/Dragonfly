"""Area-of-interest helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry


@dataclass
class AreaOfInterest:
    geometry: BaseGeometry

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return self.geometry.bounds

    def to_geojson(self) -> dict:
        return self.geometry.__geo_interface__


def from_geojson(geojson: dict) -> AreaOfInterest:
    return AreaOfInterest(geometry=shape(geojson))


def bounding_box(coordinates: Iterable[float]) -> AreaOfInterest:
    min_lon, min_lat, max_lon, max_lat = coordinates
    from shapely.geometry import box

    return AreaOfInterest(geometry=box(min_lon, min_lat, max_lon, max_lat))
