# Mermaid Diagrams - Viewing Guide
# Author: Thomas Fischer (TFITConsult)
# Version: 1.0
# Date: 2024-11-22

## 📊 All Diagrams Successfully Created!

Your complete set of architecture diagrams is ready in **3 different formats**:

### Format 1: Interactive HTML (Recommended)
**File:** `diagrams/view_all_diagrams.html`

**How to use:**
1. Download the file to your computer
2. Open with any web browser (Chrome, Firefox, Safari, Edge)
3. All 9 diagrams will render automatically
4. Fully interactive and zoomable
5. Right-click to save individual diagrams

**✅ Best for:** Viewing, presentations, sharing with team

---

### Format 2: Individual .mmd Files
**Location:** `diagrams/` folder

**Files created:**
- `01_system_architecture.mmd`
- `02_data_flow_sequence.mmd`
- `03_component_interaction.mmd`
- `04_pipeline_state_machine.mmd`
- `05_data_model_class.mmd`
- `06_spatial_query.mmd`
- `07_band_processing.mmd`
- `08_error_handling.mmd`

**How to use:**
- **Online:** Copy content to https://mermaid.live/
- **VS Code:** Install "Markdown Preview Mermaid Support" extension
- **CLI:** Use `mmdc` command-line tool

**✅ Best for:** Editing, version control, integration into documentation

---

### Format 3: In Documentation
**File:** `eo_diagrams.md`

**Contains:**
- All diagrams with full context
- Explanatory headers for each diagram
- Complete system architecture documentation

**✅ Best for:** Reading alongside technical documentation

---

## 🎨 Diagram Descriptions

### 1. System Architecture Diagram
Shows the complete end-to-end system including:
- User environment (Jupyter, Python)
- Tilebox platform components
- Copernicus infrastructure
- Processing pipeline stages

### 2. Data Flow Sequence Diagram
Temporal flow showing interactions between:
- User
- Notebook
- Tilebox API
- Copernicus S3
- Rasterio
- NumPy

### 3. Component Interaction Diagram
Four-layer architecture:
- Data Acquisition
- Data Processing
- Data Products
- Visualization

### 4. Processing Pipeline State Machine
State transitions from:
- Query → Filter → Download → Process → Visualize
- Includes error handling states

### 5. Data Model Class Diagram
Object-oriented representation showing:
- TileboxClient
- Dataset & Collection
- XArrayDataset
- CopernicusClient
- RasterBand
- ChangeDetector

### 6. Spatial Query Visualization
Decision tree for spatial filtering:
- Intersection modes
- Temporal filtering
- Cloud cover filtering

### 7. Band Processing Workflow
Complete band selection and processing:
- Resolution filtering (10m/20m/60m)
- RGB band selection
- Download and normalization
- Array stacking

### 8. Error Handling Flow
Comprehensive error management:
- Authentication validation
- Data availability checks
- Download retry logic
- File readability verification

### 9. NBR Calculation Workflow
Professional fire analysis pipeline:
- Pre/post-fire scene acquisition
- Band downloading (NIR + SWIR)
- Normalization and resampling
- NBR calculation
- dNBR computation
- Burn severity classification

---

## 🖼️ Quick Preview

Here's what the diagrams show:

```
System Flow:
User → Jupyter → Tilebox API → Copernicus S3 → Download
    → Rasterio → NumPy → Change Detection → Visualization

NBR Workflow:
Download Bands → Normalize → Resample → Calculate NBR
    → Compute dNBR → Classify Severity (6 classes)
```

---

## 💡 Usage Tips

### For Presentations
1. Open `view_all_diagrams.html` in browser
2. Use browser's full-screen mode (F11)
3. Scroll to desired diagram
4. Right-click > "Save image as..." for export

### For Documentation
1. Copy `.mmd` files into your docs repository
2. Most documentation systems support Mermaid natively
3. GitHub, GitLab, and Notion render Mermaid automatically

### For Editing
1. Copy diagram code from `.mmd` file
2. Paste into https://mermaid.live/
3. Edit visually
4. Export as PNG/SVG or copy updated code

---

## 🔧 Tools & Resources

### Online Editors
- **Mermaid Live Editor:** https://mermaid.live/
- **Mermaid Chart:** https://www.mermaidchart.com/

### VS Code Extensions
- Markdown Preview Mermaid Support
- Mermaid Editor
- Mermaid Markdown Syntax Highlighting

### CLI Tools
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Render diagram
mmdc -i diagram.mmd -o diagram.png
```

### Documentation Integration
- **GitHub/GitLab:** Native support in Markdown
- **Confluence:** Use Mermaid Diagrams plugin
- **Notion:** Use `/code` block with language "mermaid"
- **Obsidian:** Native support

---

## 📦 File Summary

```
outputs/
├── README.md                           # Main documentation index
├── technical_analysis.md               # Complete technical docs
├── eo_diagrams.md                      # All diagrams with context
├── esa_data_access_nbr_guide.md       # Data access & NBR guide
├── DIAGRAMS_GUIDE.md                  # This file
└── diagrams/
    ├── view_all_diagrams.html         # 🌟 Interactive viewer
    ├── 01_system_architecture.mmd
    ├── 02_data_flow_sequence.mmd
    ├── 03_component_interaction.mmd
    ├── 04_pipeline_state_machine.mmd
    ├── 05_data_model_class.mmd
    ├── 06_spatial_query.mmd
    ├── 07_band_processing.mmd
    ├── 08_error_handling.mmd
    └── [NBR diagram included in HTML]
```

---

## ✅ Verification Checklist

- [x] 9 diagrams created
- [x] HTML viewer with all diagrams
- [x] Individual .mmd files for editing
- [x] Integrated in documentation
- [x] All diagrams render correctly
- [x] Export options available
- [x] Usage guide provided

---

## 🚀 Next Steps

1. **View Now:** Open `diagrams/view_all_diagrams.html` in your browser
2. **Review:** Check each diagram for accuracy
3. **Export:** Save any diagrams you need for presentations
4. **Integrate:** Add to your project documentation
5. **Customize:** Edit .mmd files to match your specific needs

---

**All diagrams are production-ready and fully documented!**
