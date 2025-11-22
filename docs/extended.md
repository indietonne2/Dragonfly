PART B – 1-WEEK EXTENDED DESIGN
The 1-week plan builds on the MVP and adds:
Multiple regions with a rotation schedule.
A fire-zone mask (precomputed elsewhere) to reduce compute & storage.
Lightweight monitoring & health checks.
Better client UX (legend, coverage shading, metadata).
Cleaner configuration and separation of responsibilities.
B1. Extended Goals
After one week of focused development, aim for:
Support N regions (e.g. California, Mediterranean, SE Australia, Amazon fringe) with precomputed low-res dNBR tiles.
Rotation scheduler:
Each night, update 1–2 regions according to priority and age.
Use a fire-zone mask (imported as a raster) to limit where dNBR is computed.
A minimal health system:
Last run per region
Disk usage checks
Simple API or static JSON metadata per region
Client:
Visual indication of which regions have coverage.
Simple legend for dNBR severity.
Small “info popup” for current region (date windows, update age).
B2. Architecture Overview (1-Week)
B2.1 Extended System Diagram
flowchart TD
    subgraph VPS["VPS 500"]
        subgraph Config["Config & Metadata"]
            C1[regions.json<br>(multi-region list)]
            C2[fire_zone_mask.tif<br>(imported offline)]
        end

        subgraph Batch["Batch & Scheduler"]
            S1[rotation_scheduler.py<br>(which regions tonight?)]
            S2[low_res_nbr.py<br>(multi-region aware)]
            S3[generate_tiles.py<br>(per region)]
        end

        subgraph Storage["Storage"]
            R1[/var/dragonfly/raster/<region>_lowres_dnbr.tif/]
            T1[/var/dragonfly/tiles/<region>/dnbr/{z}/{x}/{y}.png/]
            M1[/var/dragonfly/meta/<region>.json/]
        end

        subgraph Server["HTTP Server"]
            N1[nginx static /tiles]
            A1[lightweight API /meta/<region>.json]
        end
    end

    subgraph Client["Dragonfly Client"]
        L1[TileLayer: /tiles/<region>/dnbr/{z}/{x}/{y}.png]
        L2[Coverage overlay from /meta/<region>.json]
        L3[High-res NBR/dNBR compute]
    end

    C1 --> S1
    C2 --> S2
    S1 --> S2
    S2 --> R1
    R1 --> S3
    S3 --> T1
    S3 --> M1
    T1 --> N1
    M1 --> A1

    N1 --> L1
    A1 --> L2
    L3 --> Client
B3. Extended Configuration
B3.1 Multi-Region Config: config/regions.json
Example structure:
Top-level list of region objects:
name: "california", "mediterranean", "se_australia", etc.
bbox: region bounding box.
priority: 1, 2 (Tier 1/2).
update_interval_days: e.g. 7, 14, etc.
pre_window_days, post_window_days: fallback windows.
fire_mask_path: path to fire-zone mask for this region (optional).
zoom_min, zoom_max for tiles.
Design Choices:
Keep regions.json simple and human-editable.
Use strongly opinionated defaults to reduce per-region config.
B4. Rotation Scheduler
B4.1 New Script: scripts/rotation_scheduler.py
Responsibility:
Determine which regions should be processed on a given night based on:
update_interval_days
last successful run per region (stored in metadata JSON).
Persistent metadata per region:
meta/<region>.json contains:
last_run_at
last_status (success / failed)
tile_count
disk_usage_estimate
pre_window / post_window actually used.
High-level behavior:
Read regions.json.
Read all meta/<region>.json (if present).
For each region:
Compute days since last_run_at.
Compare with update_interval_days.
Choose 1–2 regions (e.g. highest priority, longest since last run) to update tonight.
Call low_res_nbr.py and generate_tiles.py for each selected region in sequence.
B5. Low-Res NBR/dNBR with Fire-Zone Mask
B5.1 Fire-Zone Raster
Provided as fire_zone_mask.tif (global or region-specific), where:
1 = “in fire-prone zone”
0 = non-fire area
Precomputed offline on a bigger machine and copied to VPS.
B5.2 Integration in low_res_nbr.py (Extended Mode)
Behavior:
For each region:
Clip fire_zone_mask.tif to the region bbox.
When computing NBR_pre/post and dNBR, set NBR/dNBR to nodata outside fire zones.
This reduces:
Processing time (skip non-fire pixels early).
Tile storage (optional: skip tiles with no fire-zone pixels).
B6. Tiling & Metadata (Extended)
B6.1 Enhanced Tile Generation
In generate_tiles.py extended version:
For each tile {z, x, y}:
If tile’s dNBR data is all nodata or all “unburned”:
Optionally skip writing file (save disk).
Summarize for the region:
tile_count
disk_usage (approx or measured).
B6.2 Region Metadata: /var/dragonfly/meta/<region>.json
Fields:
region_name
bbox
pre_start, pre_end, post_start, post_end
generated_at (ISO timestamp)
tile_url_template
zoom_min, zoom_max
tile_count, disk_usage_mb
last_status
This is served via a very light API or static file:
GET /meta/<region>.json → metadata JSON.
B7. Minimal Health & Monitoring
B7.1 Health Script: scripts/health_check.py
Responsibility:
Perform a few simple checks:
Disk space in /var/dragonfly above some threshold (e.g. 5 GB free).
For each region:
last_status == "success" and generated_at not too old (e.g. < 30 days).
Try reading one well-known tile per region:
/tiles/<region>/dnbr/<zoom>/<x>/<y>.png
Outputs:
One JSON summary to meta/health.json:
disk_ok, regions_ok, per-region statuses.
Optionally used by external monitoring (e.g. UptimeRobot hitting /meta/health.json).
B8. Client Enhancements
B8.1 Coverage Overlay
Use the metadata endpoints:
At client load:
Fetch /meta/index.json – a list of known regions, their bbox, and last update.
Draw light polygon outlines for coverage regions on the map.
Shade regions differently if generated_at is older than e.g. 30 days.
B8.2 dNBR Legend
Add a small legend component in the map:
Colors reflect dNBR severity thresholds (USGS-like):
enhanced regrowth
unburned
low
moderate-low
moderate-high
high
This legend applies both to low-res tiles and high-res client results (same thresholds).
B8.3 Region Info Tooltip
On click inside a region:
Find the region whose bbox contains the click.
Show small panel with:
Region name
Last update date
Pre/Post date windows
Note “low-res preview; high-res computed on demand.”
B9. Extended Sequence: One Week System
sequenceDiagram
    participant Cron
    participant Scheduler as rotation_scheduler.py
    participant Precalc as low_res_nbr.py
    participant Tiler as generate_tiles.py
    participant Meta as meta/*.json
    participant FS as /var/dragonfly/tiles
    participant Health as health_check.py

    Cron->>Scheduler: Run daily at 03:00
    Scheduler->>Meta: Read per-region metadata
    Scheduler->>Scheduler: Select 1-2 regions to update
    loop For each selected region
        Scheduler->>Precalc: Run with region config
        Precalc->>Precalc: Apply fire-zone mask
        Precalc->>FS: Write regional lowres_dnbr.tif
        Precalc->>Tiler: Invoke tiler for region
        Tiler->>FS: Write new tiles
        Tiler->>Meta: Update <region>.json (last_run, tile_count)
    end

    Cron->>Health: Run after precomputation
    Health->>FS: Sanity-check one tile per region
    Health->>Meta: Write health.json
B10. 1-Week Work Plan (Indicative)
Day 1–2 – MVP (from Part A)
Implement one-region MVP fully.
Confirm tiles visible and high-res integration working.
Day 3 – Multi-Region Config & Refactor
Introduce regions.json.
Refactor low_res_nbr.py and generate_tiles.py to:
Accept region as a parameter.
Loop over 1..N regions.
Day 4 – Rotation Scheduler & Metadata
Implement rotation_scheduler.py.
Implement per-region metadata JSON writing and reading.
Day 5 – Fire-Zone Mask & Tile Skipping
Integrate fire_zone_mask.tif into low-res processing.
Skip tiles for regions with no meaningful data.
Adjust tile-count and disk-usage calculations.
Day 6 – Client Enhancements
Fetch /meta/index.json and /meta/<region>.json.
Draw coverage overlays and legend.
Show region info on click / map interaction.
Day 7 – Health Check & Hardening
Implement health_check.py and meta/health.json.
Add a simple external ping (if available).
Do manual stress testing and refine zoom thresholds.
B11. Future Extensions (Beyond 1 Week)
Cloud-native storage (S3/Backblaze) instead of local disk.
COG pyramids instead of ad-hoc TIFF + tiler.
Automatic fire detection (dynamic pre/post windows).
Multi-user region selection and per-user AOI caching.

