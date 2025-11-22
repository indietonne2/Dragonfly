"""
Author: Thomas Fischer (TFITConsult)
Version: 2.0
What this file does: Spectral index processing utilities for Sentinel-2 NBR/dNBR workflows.
Filename: processing.py
Pathname: /workspace/Dragonfly/src/dragonfly/processing.py
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass
class BurnSeverityClass:
    name: str
    dnbr_min: float
    dnbr_max: float
    color: tuple[int, int, int]


BURN_SEVERITY_CLASSES: list[BurnSeverityClass] = [
    BurnSeverityClass("Enhanced Regrowth", -0.500, -0.250, (26, 152, 80)),
    BurnSeverityClass("High Regrowth", -0.250, -0.100, (102, 189, 99)),
    BurnSeverityClass("Unburned", -0.100, 0.100, (255, 255, 190)),
    BurnSeverityClass("Low Severity", 0.100, 0.270, (253, 174, 97)),
    BurnSeverityClass("Moderate Severity", 0.270, 0.660, (244, 109, 67)),
    BurnSeverityClass("High Severity", 0.660, 1.300, (215, 48, 39)),
]


def _safe_divide(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.true_divide(numerator, denominator)
        result[~np.isfinite(result)] = np.nan
        return result


def calculate_nbr(nir: np.ndarray, swir: np.ndarray) -> np.ndarray:
    """Calculate Normalized Burn Ratio (NBR) using Sentinel-2 NIR (B08) and SWIR (B12).

    Args:
        nir: NIR band as a float array (reflectance).
        swir: SWIR band as a float array (reflectance).

    Returns:
        An array with values in the range [-1, 1], with NaNs for invalid divisions.
    """

    return _safe_divide(nir - swir, nir + swir)


def calculate_dnbr(pre_fire_nbr: np.ndarray, post_fire_nbr: np.ndarray) -> np.ndarray:
    """Calculate delta NBR (dNBR) from pre- and post-fire NBR arrays."""

    return pre_fire_nbr - post_fire_nbr


def classify_dnbr(dnbr: np.ndarray) -> np.ndarray:
    """Classify dNBR into USGS burn severity classes.

    Returns a uint8 raster where values map to ``BURN_SEVERITY_CLASSES`` order.
    """

    class_raster = np.full(dnbr.shape, fill_value=255, dtype=np.uint8)
    for idx, severity in enumerate(BURN_SEVERITY_CLASSES):
        mask = (dnbr >= severity.dnbr_min) & (dnbr < severity.dnbr_max)
        class_raster[mask] = idx
    return class_raster


def normalize_for_overlay(array: np.ndarray, min_val: float = -1.0, max_val: float = 1.0) -> np.ndarray:
    """Normalize an array to 0..1 for visualization."""

    clipped = np.clip(array, min_val, max_val)
    normalized = (clipped - min_val) / (max_val - min_val)
    return np.nan_to_num(normalized, nan=0.0, posinf=1.0, neginf=0.0)


def colorize(values: np.ndarray, colormap: Iterable[tuple[float, tuple[int, int, int]]]) -> np.ndarray:
    """Apply a simple linear colormap to a normalized (0..1) array.

    The colormap is an iterable of ``(stop, (r, g, b))`` values where stops are
    monotonically increasing floats between 0 and 1.
    """

    stops = np.array([stop for stop, _ in colormap])
    colors = np.array([rgb for _, rgb in colormap], dtype=np.float32)
    values_flat = values.ravel()
    rgba = np.zeros((values_flat.size, 4), dtype=np.uint8)

    indices = np.searchsorted(stops, values_flat, side="right")
    indices = np.clip(indices, 1, len(stops) - 1)
    lower = stops[indices - 1]
    upper = stops[indices]
    weight = (values_flat - lower) / (upper - lower + 1e-12)

    low_colors = colors[indices - 1]
    high_colors = colors[indices]
    interpolated = low_colors + (high_colors - low_colors) * weight[:, None]

    rgba[:, :3] = np.clip(interpolated, 0, 255).astype(np.uint8)
    rgba[:, 3] = (values_flat > 0).astype(np.uint8) * 180  # transparent for nodata
    return rgba.reshape((*values.shape, 4))


DEFAULT_DNBR_COLORMAP = [
    (0.0, (26, 152, 80)),
    (0.2, (102, 189, 99)),
    (0.35, (255, 255, 190)),
    (0.55, (253, 174, 97)),
    (0.8, (244, 109, 67)),
    (1.0, (215, 48, 39)),
]
