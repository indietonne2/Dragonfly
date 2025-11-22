# Technical Analysis: Earth Observation Change Detection Notebook
# Author: Thomas Fischer (TFITConsult)
# Version: 1.0
# Purpose: Comprehensive technical documentation for Dixie Fire change detection workflow
# Date: 2024-11-22

## Executive Summary

This Jupyter notebook implements a **change detection workflow** for analyzing wildfire impacts using multi-temporal Sentinel-2 satellite imagery. The case study focuses on the 2021 California Dixie Fire, demonstrating a complete pipeline from data acquisition to visual change analysis.

## Technical Architecture

### 1. Data Flow Architecture

The notebook follows a systematic ETL (Extract, Transform, Load) pattern:

```
Tilebox Metadata Catalog
         ↓
   Query & Filter
         ↓
Copernicus S3 Storage
         ↓
  Local Download
         ↓
 Rasterio Loading
         ↓
  NumPy Processing
         ↓
  Visualization
```

### 2. Core Components

#### A. Data Acquisition Layer
- **API**: Tilebox Datasets Client
- **Catalog**: `open_data.copernicus.sentinel2_msi`
- **Collections**: Sentinel-2 L2A products from satellites A, B, and C
- **Storage**: Copernicus Data Space S3 bucket

#### B. Query Parameters
- **Temporal Resolution**: 
  - Pre-fire: 2021-06-01 to 2021-07-01
  - Post-fire: 2022-06-01 to 2022-07-01 (1 year later for comparable sun angle)
- **Spatial Extent**: Bounding box around Dixie Fire area (California)
  - Coordinates: [-121.244, 40.045] to [-120.894, 40.349]
- **Cloud Cover Filter**: ≤1% maximum

#### C. Spectral Bands Utilized
- **B04 (Red)**: 665 nm, 20m resolution
- **B03 (Green)**: 560 nm, 20m resolution  
- **B02 (Blue)**: 490 nm, 20m resolution

### 3. Data Processing Pipeline

#### Stage 1: Metadata Query
```python
# Queries three Sentinel-2 satellite collections
sentinel2_l2_collections = ["S2A_S2MSI2A", "S2B_S2MSI2A", "S2C_S2MSI2A"]
```

**Output**: xarray Dataset containing metadata for matching granules

#### Stage 2: Cloud Filtering
```python
# Filters to <1% cloud cover using metadata
before = before.isel(time=before.cloud_cover <= max_cloud_cover)
```

**Result**: 3 granules before fire, 2 granules after fire

#### Stage 3: Data Download
- Uses Copernicus S3 API with access credentials
- Downloads only required bands at 20m resolution
- Sentinel-2 stores each band in separate GeoTIFF files

#### Stage 4: Raster Processing
```python
# Reads bands and normalizes reflectance values
# S2 stores as uint16 scaled by 10000
reflectance = pixel_value / 10000
```

#### Stage 5: RGB Composite Creation
```python
# Stacks bands into 3D array [height, width, channels]
rgb_composite = np.stack([red, green, blue], axis=-1)
```

#### Stage 6: Change Detection
```python
# Computes Euclidean distance in RGB color space
change = np.linalg.norm(before_rgb - after_rgb, axis=2)
```

## Algorithm Deep Dive

### Change Detection Metric

The notebook uses a **simple RGB difference** approach:

**Formula**: `Δ = ||RGB_after - RGB_before||₂`

Where:
- `||·||₂` is the L2 (Euclidean) norm
- Computed pixel-by-pixel across all three bands
- Results in a 2D change magnitude matrix

**Interpretation**:
- High values = Significant spectral change
- Low values = Minimal change
- Particularly effective for burn scars due to drastic reflectance changes

### Limitations of Current Approach

1. **Band Selection**: Only uses visible spectrum (RGB)
   - Misses NIR and SWIR bands critical for fire analysis
   
2. **No Spectral Indices**: Doesn't use NBR/dNBR which are standard for burn severity

3. **Simple Difference**: Doesn't account for:
   - Atmospheric conditions
   - Bidirectional reflectance effects
   - Seasonal vegetation changes

## Data Specifications

### Sentinel-2 MSI Level-2A Products

**Processing Level**: Bottom-of-Atmosphere reflectance  
**Geometric Correction**: Orthorectified  
**Atmospheric Correction**: Applied using Sen2Cor

**Band Configuration**:
```
Band 02 (Blue):  490 nm, 10m native → 20m used
Band 03 (Green): 560 nm, 10m native → 20m used
Band 04 (Red):   665 nm, 10m native → 20m used
```

**File Format**: JP2000 or GeoTIFF  
**Bit Depth**: 16-bit unsigned integer  
**Scaling Factor**: 10,000 (reflectance values 0-10000 = 0.0-1.0)

### Dixie Fire Event Details

- **Start Date**: July 13, 2021
- **Containment**: October 25, 2021
- **Area Burned**: 963,309 acres (3,898 km²)
- **Location**: Plumas, Butte, Lassen, Shasta, and Tehama Counties, California

## Dependencies & Environment

### Python Packages
```yaml
tilebox: ^latest          # Copernicus data catalog access
xarray: ^latest           # Multi-dimensional arrays
rasterio: ^latest         # Geospatial raster I/O
shapely: ^latest          # Geometric operations
numpy: ^latest            # Array operations
matplotlib: ^latest       # Visualization
scipy: ^latest            # Scientific computing
ipywidgets: ^latest       # Interactive widgets
```

### External Services Required

1. **Tilebox API**
   - Endpoint: `https://console.tilebox.com`
   - Authentication: API key required
   - Rate limits: As per service tier

2. **Copernicus Data Space**
   - Storage: S3-compatible object storage
   - Authentication: Access key + Secret key
   - Free tier: Available with registration

## Output Artifacts

### 1. Visual Products
- **Before Image**: RGB composite from June 2021
- **After Image**: RGB composite from June 2022
- **Change Map**: Heatmap showing magnitude of spectral change

### 2. Quantitative Metrics
- Granule counts (before/after filtering)
- Change magnitude statistics (min, max, percentiles)
- Spatial extent coverage

## Performance Characteristics

### Data Volume
- **Single granule size**: ~1 GB (full product)
- **Downloaded per image**: ~150-200 MB (3 bands at 20m)
- **Total download**: ~400-600 MB for analysis

### Processing Time (Estimates)
- Metadata query: 5-10 seconds
- Data download: 5-15 minutes (bandwidth dependent)
- Raster processing: <30 seconds
- Visualization: <5 seconds

## Known Issues & Considerations

1. **API Keys**: Placeholder values need replacement
2. **Temporal Offset**: 1-year gap may introduce seasonal bias
3. **Resolution Trade-off**: Using 20m instead of 10m native resolution
4. **Single Scene**: Uses one scene before/after, doesn't composite multiple dates

