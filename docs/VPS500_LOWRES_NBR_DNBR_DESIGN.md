# Dragonfly – VPS 500 Low-Res NBR/dNBR Design

Author: Thomas Fischer  
Repo: `indietonne2/Dragonfly`  
Target Deployment: Netcup VPS 500 (2 vCPU, 2 GB RAM, 40 GB SSD)  
Document Version: 1.0  

This document describes:

1. A **1-day MVP**: smallest change set to get precomputed **low-res NBR/dNBR tiles** + client-side high-res NBR/dNBR.  
2. A **1-week extended design**: multi-region, basic rotation, simple monitoring, and better client integration.

---

## 0. Background & Constraints

- VPS: Netcup VPS 500
  - 2 vCPU, 2 GB RAM, 40 GB SSD.
- Data model:
  - **Low-res** (≈ 300 m) NBR/dNBR computed on the server, stored as XYZ tiles.
  - **High-res** (10–20 m) NBR/dNBR computed in the client from Sentinel-2 (or equivalent) scenes.
- Focus:
  - First, **one region** (e.g. California), then extend to more fire-prone regions.
- Hard constraints:
  - No full global, no big in-memory mosaics, no heavy parallelism / Dask cluster.

---

# PART A – 1-DAY MVP DESIGN (HIGHEST IMPACT, MINIMAL WORK)

## A1. Goals

In one effective dev day, deliver:

1. **Nightly precomputation** of low-res NBR + dNBR tiles for a **single region**.
2. A **static tile server** on the VPS (`/tiles/...`).
3. A **client tile layer** that:
   - Uses low-res tiles for overview zooms.
   - Still performs **high-res NBR/dNBR** on-demand above a zoom threshold.

No complex automation, monitoring, or multiple-region management in this phase.

---

## A2. High-Level Architecture (MVP)

### A2.1 System Diagram

```mermaid
flowchart TD
    subgraph VPS["VPS 500"]
        A1[region.json<br>(AOI + dates + paths)] --> B1
        B1[low_res_nbr.py<br>(batch pre/post NBR)] --> C1[low_res_nbr.tif<br>(GeoTIFF)]
        C1 --> D1[generate_tiles.py<br>(XYZ, PNG, z4-9)]
        D1 --> E1[/var/dragonfly/tiles]
        E1 --> F1[nginx<br>static tile server]
    end

    subgraph Client["Dragonfly Client"]
        G1[User pans & zooms map] --> H1[TileLayer<br>/tiles/{z}/{x}/{y}.png]
        G1 --> I1[If zoom >= threshold:<br>fetch S2 + compute hi-res NBR/dNBR]
    end

    F1 --> H1

