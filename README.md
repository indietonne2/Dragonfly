# Dragonfly Sentinel-2 NBR Toolkit

This repository now includes a lightweight Python engine for accessing Sentinel-2 data, computing the Normalized Burn Ratio (NBR) and delta NBR (dNBR), and rendering overlays on OpenStreetMap with Folium. The code is structured as a reusable library (`dragonfly`) plus an example pipeline script.

## Features
- Sentinel-2 STAC connector targeting Copernicus Data Space
- NBR / dNBR calculation helpers and USGS-aligned burn severity colormap
- AOI helpers for GeoJSON or bounding boxes
- Folium overlay generation for OpenStreetMap (or any Leaflet tile server)
- Example pipeline demonstrating end-to-end use
- Cloud masking that downloads the Sentinel-2 Scene Classification Layer (SCL) and masks clouds/snow

## Quickstart
1. Install the library in editable mode:
   ```bash
   pip install -e .
   ```

2. Run the example pipeline (requires valid network access to the STAC catalogue):
   ```bash
   python examples/pipeline_example.py
   ```

3. Open `artifacts/dnbr_overlay.html` in your browser to view the dNBR overlay on OpenStreetMap.

## Key Modules
- `dragonfly.data_access.SentinelStacConnector` – STAC search and band download
- `dragonfly.processing.calculate_nbr` / `calculate_dnbr` – spectral indices
- `dragonfly.viz.raster_overlay` – Folium/Leaflet overlay rendering
- `dragonfly.pipeline.NBRPipeline` – orchestrates search → download → NBR/dNBR → overlay

## Notes
- The STAC endpoint defaults to Copernicus Data Space; override `base_url` if you have a different catalogue.
- The pipeline expects Sentinel-2 L2A assets that expose `B08` (NIR), `B12` (SWIR), and `SCL` (scene classification) assets as GeoTIFFs.
- Raster reprojection and resampling are handled automatically when band resolutions differ.
- Reflectance bands are scaled to [0,1] from Sentinel's stored 0..10,000 range and clouds/snow (SCL classes 8, 9, 10, 11) are masked by default.
