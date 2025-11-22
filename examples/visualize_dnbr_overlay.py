"""Generate a Folium map from an in-memory dNBR array.

This example builds a synthetic dNBR raster so you can see how the
visualization pipeline works without downloading Sentinel-2 data.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from dragonfly.viz import raster_overlay


def synthetic_dnbr(size: int = 256) -> np.ndarray:
    """Create a smooth dNBR-like surface for testing visualization.

    The array values are clipped to the expected [-1, 1] range for dNBR,
    with a bright circular "burn" in the center and a small recovering
    patch to the west. The shape is square to simplify working with folium's
    image overlay helper.
    """

    y, x = np.mgrid[-1:1 : size * 1j, -1:1 : size * 1j]

    # Gentle background variation
    base = 0.05 * np.sin(3 * np.pi * x) * np.cos(2 * np.pi * y)

    # Burned area with high positive dNBR values near the center
    burn = 0.7 * np.exp(-6 * (x**2 + y**2))

    # A recovering / unburned patch to illustrate negative and low values
    recovery = -0.25 * np.exp(-10 * ((x + 0.5) ** 2 + (y + 0.2) ** 2))

    dnbr = base + burn + recovery
    return np.clip(dnbr, -1.0, 1.0)


def main() -> None:
    # Define the bounding box (min_lon, min_lat, max_lon, max_lat)
    bounds = (12.25, 45.45, 12.35, 45.55)

    # Create a synthetic dNBR raster
    dnbr_array = synthetic_dnbr(size=300)

    # Render an interactive folium map using the built-in USGS colormap
    fmap = raster_overlay(dnbr_array, bounds=bounds, name="Synthetic dNBR")

    artifacts_dir = Path("./artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    output_html = artifacts_dir / "synthetic_dnbr_overlay.html"

    fmap.save(output_html)
    print(f"Saved overlay to {output_html}")


if __name__ == "__main__":
    main()
