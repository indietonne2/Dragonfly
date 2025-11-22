"""Example usage of the NBRPipeline for Sentinel-2 data."""
from pathlib import Path

from dragonfly.aoi import bounding_box
from dragonfly.pipeline import NBRPipeline


def main():
    # Example AOI over a small bounding box
    aoi = bounding_box((12.25, 45.45, 12.35, 45.55))

    pipeline = NBRPipeline()

    # Search windows can be tuned for your use case; these are illustrative
    result = pipeline.download_and_prepare(
        geometry=aoi.to_geojson(),
        pre_window=("2024-06-01", "2024-06-15"),
        post_window=("2024-07-01", "2024-07-15"),
        target_dir=Path("./artifacts"),
        cloud_cover=10,
    )

    # Use the AOI bounds to position the overlay on an OpenStreetMap basemap
    fmap = pipeline.to_folium_map(result.dnbr, bounds=aoi.bounds)
    fmap.save("./artifacts/dnbr_overlay.html")
    print("Saved overlay to ./artifacts/dnbr_overlay.html")


if __name__ == "__main__":
    main()
