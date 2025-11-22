# 🔥 Dragonfly NBR Toolkit - START HERE

**A lightweight Python engine for Sentinel-2 fire analysis using NBR/dNBR**

## 🎯 What You Have

This repository provides a **production-ready toolkit** for analyzing wildfire impacts using Sentinel-2 satellite imagery. The code implements the industry-standard **Normalized Burn Ratio (NBR)** methodology recommended by USGS for burn severity mapping.

### Key Features
✅ Sentinel-2 STAC connector (Copernicus Data Space)  
✅ Automatic cloud masking using Scene Classification Layer  
✅ NBR/dNBR calculation with USGS-aligned severity classification  
✅ Band resampling (20m SWIR → 10m resolution)  
✅ Interactive Folium overlays on OpenStreetMap  
✅ Complete example pipeline  

---

## 🚀 Quick Start (3 Steps)

### 1. Install the Package
```bash
pip install -e .
```

### 2. Run the Example
```bash
python examples/pipeline_example.py
```

### 3. View Results
Open `artifacts/dnbr_overlay.html` in your browser to see the burn severity map overlaid on OpenStreetMap.

---

## 📊 View System Architecture

**👉 [Open Interactive Diagrams](diagrams/view_all_diagrams.html)**

Download and open this HTML file in your browser to see all 8 system architecture diagrams including:
- Complete data flow
- Processing pipeline states
- NBR calculation workflow
- Error handling
- Cloud masking logic

---

## 🔥 Understanding NBR vs RGB

### Why NBR for Fire Analysis?

| Aspect | RGB Change Detection | NBR/dNBR (This Toolkit) |
|--------|---------------------|------------------------|
| **Bands Used** | Visible only (R,G,B) | NIR + SWIR (fire-sensitive) |
| **Fire Sensitivity** | Moderate | Excellent |
| **Industry Standard** | No | Yes (USGS) |
| **Burn Severity** | No classification | 6-class severity mapping |
| **Scientific Validity** | Limited | Peer-reviewed methodology |

### NBR Formula
```
NBR = (NIR - SWIR) / (NIR + SWIR)
dNBR = NBR_pre - NBR_post
```

**For Sentinel-2:**
- NIR = Band 8 (842 nm, 10m)
- SWIR = Band 12 (2190 nm, 20m)

### Burn Severity Classification (USGS Standard)

| dNBR Range | Severity Level | What It Means |
|-----------|---------------|---------------|
| < -0.10 | Enhanced Regrowth | More vegetation after fire |
| -0.10 to 0.10 | Unburned | No significant change |
| 0.10 to 0.27 | Low Severity | Minor vegetation damage |
| 0.27 to 0.44 | Moderate-Low | Moderate damage |
| 0.44 to 0.66 | Moderate-High | Significant damage |
| > 0.66 | High Severity | Complete destruction |

---

## 📁 Project Structure

```
dragonfly/
├── src/dragonfly/
│   ├── __init__.py           # Package exports
│   ├── aoi.py                # Area of Interest helpers
│   ├── data_access.py        # STAC connector
│   ├── processing.py         # NBR/dNBR calculations
│   ├── pipeline.py           # High-level workflow
│   └── viz.py                # Folium visualization
├── examples/
│   └── pipeline_example.py   # Complete workflow example
├── diagrams/
│   ├── view_all_diagrams.html  # Interactive diagram viewer
│   └── *.mmd                   # Mermaid diagram sources
├── pyproject.toml            # Package configuration
├── README.md                 # This file
└── LICENSE                   # MIT License
```

---

## 🔧 Core Components

### 1. Data Access (`data_access.py`)
```python
from dragonfly.data_access import SentinelStacConnector

connector = SentinelStacConnector()
items = connector.search(
    geometry=aoi.to_geojson(),
    start="2024-06-01",
    end="2024-06-15",
    cloud_cover=10
)
```

### 2. Processing (`processing.py`)
```python
from dragonfly.processing import calculate_nbr, calculate_dnbr, classify_dnbr

nbr_pre = calculate_nbr(nir_array, swir_array)
nbr_post = calculate_nbr(nir_array_post, swir_array_post)
dnbr = calculate_dnbr(nbr_pre, nbr_post)
severity = classify_dnbr(dnbr)
```

### 3. Pipeline (`pipeline.py`)
```python
from dragonfly.pipeline import NBRPipeline

pipeline = NBRPipeline()
result = pipeline.download_and_prepare(
    geometry=aoi.to_geojson(),
    pre_window=("2024-06-01", "2024-06-15"),
    post_window=("2024-07-01", "2024-07-15"),
    target_dir=Path("./artifacts")
)
```

### 4. Visualization (`viz.py`)
```python
fmap = pipeline.to_folium_map(result.dnbr, bounds=aoi.bounds)
fmap.save("dnbr_overlay.html")
```

---

## 📖 Complete Example

```python
from pathlib import Path
from dragonfly.aoi import bounding_box
from dragonfly.pipeline import NBRPipeline

# Define area of interest
aoi = bounding_box((12.25, 45.45, 12.35, 45.55))

# Initialize pipeline
pipeline = NBRPipeline()

# Process pre/post fire data
result = pipeline.download_and_prepare(
    geometry=aoi.to_geojson(),
    pre_window=("2024-06-01", "2024-06-15"),
    post_window=("2024-07-01", "2024-07-15"),
    target_dir=Path("./artifacts"),
    cloud_cover=10
)

# Get statistics
stats = pipeline.compute_statistics(result)
print(f"Burned area: {stats['burned_area_km2']:.2f} km²")
print(f"High severity: {stats['high_severity_percentage']:.1f}%")

# Create interactive map
fmap = pipeline.to_folium_map(result.dnbr, bounds=aoi.bounds)
fmap.save("dnbr_overlay.html")
```

---

## 🌐 Data Access

### Default: Copernicus Data Space STAC

This toolkit connects to the **Copernicus Data Space** STAC catalog by default - no authentication required for searching. Downloads require a free account:

1. Create account: https://dataspace.copernicus.eu/
2. The toolkit handles everything else automatically

### Alternative Data Sources

The architecture supports multiple data sources:
- **Copernicus Data Space** (default, free)
- **Google Earth Engine** (free, requires account)
- **AWS Sentinel-2** (free, S3 access)
- **SentinelHub** (commercial, trial available)

See documentation for alternative implementations.

---

## 🎨 Cloud Masking

The toolkit automatically masks clouds using Sentinel-2's Scene Classification Layer (SCL):

```python
# Cloud masking is enabled by default
result = pipeline.download_and_prepare(
    ...,
    apply_cloud_mask=True,  # Default
    cloudy_classes=(8, 9, 10, 11)  # Medium/high clouds, cirrus, snow
)
```

**SCL Classes Masked:**
- 8: Cloud medium probability
- 9: Cloud high probability
- 10: Thin cirrus
- 11: Snow/ice

---

## 📊 Output Products

### 1. NBR Rasters
- `pre/nbr.tif` - Pre-fire NBR
- `post/nbr.tif` - Post-fire NBR

### 2. Change Detection
- `dnbr.tif` - Delta NBR (change magnitude)
- `severity.tif` - USGS 6-class severity map

### 3. Visualization
- `dnbr_overlay.html` - Interactive Folium map

### 4. Statistics
```python
{
    'total_area_km2': 150.23,
    'burned_area_km2': 45.67,
    'burned_percentage': 30.4,
    'high_severity_km2': 12.34,
    'high_severity_percentage': 8.2
}
```

---

## 🔬 Technical Details

### Band Resolution Handling

Sentinel-2 has mixed resolutions:
- **B08 (NIR)**: 10m native
- **B12 (SWIR)**: 20m native

The toolkit automatically resamples SWIR to 10m using bilinear interpolation for pixel-aligned NBR calculation.

### Reflectance Scaling

Sentinel-2 L2A stores reflectance as `uint16` scaled by 10,000:
```python
# Automatic scaling in the pipeline
reflectance = pixel_value / 10000.0  # 0..10000 → 0.0..1.0
```

### Coordinate Systems

- **Input AOI**: WGS84 (EPSG:4326)
- **Sentinel-2**: UTM zones (auto-detected)
- **Output Map**: WGS84 for Folium

All transformations handled automatically.

---

## 🎯 Use Cases

### Wildfire Assessment
```python
# Dixie Fire 2021 example
aoi = bounding_box((-121.244, 40.045, -120.894, 40.349))
pre = ("2021-06-01", "2021-07-01")
post = ("2021-11-01", "2021-12-01")
```

### Post-Fire Recovery Monitoring
```python
# Multi-temporal analysis
windows = [
    ("2021-11-01", "2021-12-01"),  # 0 months
    ("2022-05-01", "2022-06-01"),  # 6 months
    ("2022-11-01", "2022-12-01")   # 12 months
]
```

### Burn Severity Validation
```python
# Compare with field data
stats = pipeline.compute_statistics(result)
# Export severity raster for GIS analysis
```

---

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
ruff check src/
black src/ --check
```

### Building Package
```bash
python -m build
```

---

## 📚 Additional Resources

### Documentation
- **[Interactive Diagrams](diagrams/view_all_diagrams.html)** - System architecture
- **[MISSING_COMPONENTS.md](MISSING_COMPONENTS.md)** - Gap analysis vs comprehensive package

### External References
- **USGS FIREMON**: https://www.usgs.gov/landsat-missions/landsat-burned-area
- **Copernicus Docs**: https://documentation.dataspace.copernicus.eu/
- **Sentinel-2 User Guide**: https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Additional data source connectors
- [ ] Multi-temporal compositing
- [ ] Automated cloud-free scene selection
- [ ] Large-area processing optimization
- [ ] Additional spectral indices (NDVI, NDWI, etc.)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🚦 Next Steps

1. **Quick Test**: Run `python examples/pipeline_example.py`
2. **View Results**: Open `artifacts/dnbr_overlay.html`
3. **Understand System**: Open `diagrams/view_all_diagrams.html`
4. **Adapt for Your Use**: Modify AOI and dates in example
5. **Explore Advanced**: Check `MISSING_COMPONENTS.md` for additional features

---

**Ready to analyze fires? Let's go! 🔥**

