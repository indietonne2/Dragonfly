# Earth Observation System Architecture Diagrams
# Author: Thomas Fischer (TFITConsult)
# Version: 1.0
# Filename: eo_diagrams.md
# Pathname: /home/claude/eo_diagrams.md
# Purpose: Complete system architecture visualization for EO change detection workflow

## System Architecture Diagram

```mermaid
graph TB
    subgraph "User Environment"
        A[Jupyter Notebook] 
        B[Python Environment<br/>tilebox, xarray, rasterio]
    end
    
    subgraph "Tilebox Platform"
        C[Tilebox API Client]
        D[Metadata Catalog<br/>open_data.copernicus.sentinel2_msi]
        E[Query Engine]
    end
    
    subgraph "Copernicus Infrastructure"
        F[Copernicus Data Space]
        G[S3 Storage<br/>eodata bucket]
        H[Sentinel-2 L2A Products]
    end
    
    subgraph "Processing Pipeline"
        I[Filter by Cloud Cover]
        J[Download Manager]
        K[Rasterio Band Reader]
        L[NumPy Array Processing]
        M[Change Detection Algorithm]
        N[Visualization Engine]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> I
    I --> J
    J --> F
    F --> G
    G --> H
    H --> K
    K --> L
    L --> M
    M --> N
    N --> A
    
    style A fill:#e1f5ff
    style M fill:#ffe1e1
    style H fill:#e1ffe1
```

## Data Flow Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Notebook
    participant TileboxAPI
    participant CopernicusS3
    participant Rasterio
    participant NumPy
    
    User->>Notebook: Execute cell: query Sentinel-2
    Notebook->>TileboxAPI: query(temporal, spatial, collections)
    TileboxAPI->>TileboxAPI: Filter metadata catalog
    TileboxAPI-->>Notebook: Return xarray.Dataset (metadata)
    
    Notebook->>Notebook: Filter by cloud_cover <= 1%
    
    User->>Notebook: Download products
    Notebook->>CopernicusS3: list_objects(product)
    CopernicusS3-->>Notebook: Return file list
    
    Notebook->>Notebook: Filter for 20m resolution bands
    Notebook->>CopernicusS3: download_objects([B04, B03, B02])
    CopernicusS3-->>Notebook: Download GeoTIFF files
    
    Notebook->>Rasterio: open(band_file)
    Rasterio->>Rasterio: Read georeferenced raster
    Rasterio-->>NumPy: Return numpy array (uint16)
    
    NumPy->>NumPy: Normalize: reflectance = value / 10000
    NumPy->>NumPy: Stack RGB bands
    NumPy->>NumPy: Calculate change: L2 norm
    
    NumPy-->>Notebook: Return change map
    Notebook->>User: Display visualization
```

## Component Interaction Diagram

```mermaid
graph LR
    subgraph "Data Acquisition"
        A1[Tilebox Client]
        A2[Metadata Query]
        A3[S3 Downloader]
    end
    
    subgraph "Data Processing"
        B1[Raster I/O]
        B2[Array Operations]
        B3[Change Detection]
    end
    
    subgraph "Data Products"
        C1[Before RGB]
        C2[After RGB]
        C3[Change Map]
    end
    
    subgraph "Visualization"
        D1[Matplotlib]
        D2[Interactive Display]
    end
    
    A1 --> A2
    A2 --> A3
    A3 --> B1
    B1 --> B2
    B2 --> C1
    B2 --> C2
    C1 --> B3
    C2 --> B3
    B3 --> C3
    C3 --> D1
    D1 --> D2
    
    style B3 fill:#ffcccc
    style C3 fill:#ccffcc
```

## Processing Pipeline State Machine

```mermaid
stateDiagram-v2
    [*] --> QueryMetadata
    QueryMetadata --> CloudFilter: Granules found
    QueryMetadata --> [*]: No data found
    
    CloudFilter --> SelectProduct: Filtered granules
    CloudFilter --> [*]: All cloudy
    
    SelectProduct --> DownloadBands: Product selected
    
    DownloadBands --> ReadRaster: Files downloaded
    DownloadBands --> Error: Download failed
    
    ReadRaster --> NormalizeReflectance: Arrays loaded
    ReadRaster --> Error: Read failed
    
    NormalizeReflectance --> CreateComposite: Scaled to [0,1]
    
    CreateComposite --> CalculateChange: Before + After ready
    
    CalculateChange --> Visualize: Change map computed
    
    Visualize --> [*]: Complete
    
    Error --> [*]: Abort
```

## Data Model Class Diagram

```mermaid
classDiagram
    class TileboxClient {
        +String token
        +dataset(name: str)
        +query()
    }
    
    class Dataset {
        +String name
        +collection(name: str)
        +query(temporal, spatial)
    }
    
    class Collection {
        +String collection_id
        +query(filters)
        +XArray results
    }
    
    class XArrayDataset {
        +DataArray time
        +DataArray cloud_cover
        +DataArray geometry
        +isel()
        +sizes
    }
    
    class CopernicusClient {
        +String access_key
        +String secret_key
        +list_objects()
        +download_objects()
        +quicklook()
    }
    
    class RasterBand {
        +String filepath
        +int width
        +int height
        +ndarray data
        +CRS crs
        +read()
    }
    
    class ChangeDetector {
        +ndarray before_rgb
        +ndarray after_rgb
        +compute_change()
        +ndarray change_map
    }
    
    TileboxClient --> Dataset
    Dataset --> Collection
    Collection --> XArrayDataset
    XArrayDataset --> CopernicusClient
    CopernicusClient --> RasterBand
    RasterBand --> ChangeDetector
```

## Spatial Query Visualization

```mermaid
graph TD
    A[Bounding Box Query] --> B{Intersection Mode}
    B -->|Intersects| C[Return all tiles<br/>touching bbox]
    B -->|Contains| D[Return only tiles<br/>fully inside bbox]
    B -->|Within| E[Return tiles<br/>containing bbox]
    
    C --> F[Spatial Filter Applied]
    D --> F
    E --> F
    
    F --> G{Temporal Filter}
    G -->|Pre-fire| H[2021-06-01 to 2021-07-01]
    G -->|Post-fire| I[2022-06-01 to 2022-07-01]
    
    H --> J[Cloud Cover Filter <= 1%]
    I --> J
    
    J --> K[Final Granule Selection]
```

## Band Processing Workflow

```mermaid
flowchart TD
    A[Sentinel-2 L2A Product] --> B[List All Bands]
    B --> C{Resolution Filter}
    C -->|10m| D[B02, B03, B04, B08]
    C -->|20m| E[B05, B06, B07, B8A, B11, B12]
    C -->|60m| F[B01, B09, B10]
    
    E --> G[Select RGB Bands]
    G --> H[B04_20m - Red]
    G --> I[B03_20m - Green]
    G --> J[B02_20m - Blue]
    
    H --> K[Download from S3]
    I --> K
    J --> K
    
    K --> L[Rasterio Read]
    L --> M[Convert uint16 to float64]
    M --> N[Divide by 10000]
    N --> O[Reflectance Range: 0.0-1.0]
    
    O --> P[Stack to 3D Array<br/>shape: height, width, 3]
```

## Error Handling Flow

```mermaid
flowchart TD
    A[Start Process] --> B{API Key Valid?}
    B -->|No| C[Raise AuthenticationError]
    B -->|Yes| D{Granules Found?}
    
    D -->|No| E[Log: No data available]
    D -->|Yes| F{Cloud Filter Pass?}
    
    F -->|No| G[Warning: High cloud cover]
    F -->|Yes| H{Download Success?}
    
    H -->|No| I[Retry with exponential backoff]
    H -->|Yes| J{Files Readable?}
    
    I --> K{Max Retries?}
    K -->|Yes| L[Raise DownloadError]
    K -->|No| H
    
    J -->|No| M[Raise RasterIOError]
    J -->|Yes| N[Process Successfully]
    
    C --> Z[Exit]
    E --> Z
    G --> Z
    L --> Z
    M --> Z
    N --> O[Return Results]
```
