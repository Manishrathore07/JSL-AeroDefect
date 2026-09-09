# JSL-AeroDefect: AI-Powered Steel Surface Defect Detection & Quality Intelligence Platform
## Comprehensive Implementation Plan for Jindal Stainless SPARK Competition

### 1. Executive Summary & Problem Understanding
Surface quality is a mission-critical benchmark in stainless steel manufacturing at Jindal Stainless Limited (JSL). Defects such as scratches, rolled-in scale, roll marks, inclusions, and edge cracks incur severe business penalties:
- **Late Detection:** Defects formed during hot or cold rolling are often caught only at the final skin pass or slitting line, wasting downstream energy, annealing, and pickling costs.
- **Yield Degradation:** Downgrading prime 304/316L coils to secondary or scrap incurs direct losses of ₹40,000–₹1,20,000 per metric ton.
- **Human Inspection Limitations:** Manual visual inspection at typical strip speeds (300–600 m/min) has low capture rates (<65%) and high operator fatigue.

**Our Core Objective:**
Deliver an industrial-grade, edge-ready Computer Vision and Quality Intelligence System that:
1. Detects and classifies 8 primary steel defect classes with bounding boxes, segmentation masks, and confidence scores.
2. Achieves sub-25ms inference latency suitable for high-speed production lines.
3. Introduces groundbreaking industrial innovations: **Roll-Mark Periodicity Root-Cause Diagnostics**, **Grade-Adaptive Quality Tolerances (304 vs 316L vs 430)**, and **Coil Digital Twin with Smart Slitting Yield Optimizer**.
4. Provides a world-class, SCADA-grade interactive dashboard designed to impress both technical evaluators and plant operations managers.

---

### 2. Novel Ideas & Key Differentiators (Why This Wins)
| Feature | Standard Hackathon Submissions | JSL-AeroDefect Platform (Our Solution) |
| :--- | :--- | :--- |
| **Detection Scope** | Simple image classifier or generic YOLO demo | Multi-task bounding box detection + defect contour segmentation + severity index |
| **Root Cause Analysis** | None (just detects defect) | **Roll-Mark Periodicity FFT Engine**: identifies exact roll stand ($F_1$ to $F_6$) and roll diameter causing recurring marks |
| **Material Context** | Ignores steel grade | **JSL Grade-Adaptive Matrix**: Dynamic tolerance logic tailored for Austenitic (304/316L), Ferritic (430), and Martensitic grades |
| **Economic Intelligence**| Raw defect counts | **Scrap & Downgrade Loss Calculator**: Real-time ₹ financial impact, trimming recommendation to salvage prime steel |
| **Coil Digital Twin** | Single static image only | **Full Coil 2D Strip Map**: Visualizes defect distribution along length (0–1500m) and strip width (Drive side, Center, Work side) |
| **Production Speed** | Untimed slow web script | **Edge Production Line Simulator**: 60+ FPS live stream simulation, latency jitter monitor, line speed slider (2–15 m/s) |
| **Reporting** | None | **Automated Coil Quality Certificate**: ASTM/ISO compliant exportable inspection report |

---

### 3. Defect Taxonomy & Target Classes
Trained and calibrated on industrial steel defect datasets (NEU Surface Defect Database, Severstal Steel, GC10-DET):
1. **Scratches (SC):** Linear abrasions from guide shoes, tension reels, or uncoilers.
2. **Rolled-in Scale (RS):** Iron oxide scale pressed into strip surface during hot rolling.
3. **Roll Marks (RM):** Periodic impressions caused by spalled or dented work rolls.
4. **Edge Cracks (EC):** Transverse edge fissures caused by excessive edge reduction or uneven cooling.
5. **Inclusions (IN):** Non-metallic refractory or slag inclusions entrapped during continuous casting.
6. **Patches (PA):** Localized surface crusting or uneven pickling spots.
7. **Pitted Surface (PS):** Micro-cavities from acid over-pickling or chemical corrosion.
8. **Crazing (CR):** Network of fine surface cracks from thermal fatigue on roll surfaces.

---

### 4. Technical Architecture
```
+-----------------------------------------------------------------------------------+
|                           JSL Industrial Web Interface                            |
|  - SCADA Dark Theme (Tailored HSL, Jindal Brand Colors, Zero Lag UI)              |
|  - Real-Time Line Stream Simulator (2 - 15 m/s) with Defect Telemetry             |
|  - 2D Coil Strip Map Digital Twin & Smart Slitting Recommendation                 |
|  - Roll-Mark Periodicity Root-Cause Spectrum & Roll Stand Identification          |
|  - Grade Tolerance Matrix (304, 316L, 430, 201) & Economic Scrap Calculator       |
|  - Automated Coil Quality Certificate Generator (Print/PDF Ready)                 |
+------------------------------------------+----------------------------------------+
                                           | HTTP / WebSocket / REST
+------------------------------------------v----------------------------------------+
|                          FastAPI High-Performance Backend                          |
|  - /api/inspect: Single & Batch Image Inference                                   |
|  - /api/stream: Continuous Line-Scan Frame Generator (Edge Simulator)             |
|  - /api/root-cause: FFT Periodicity & Roll Diameter Estimator                      |
|  - /api/coil-twin: Coil Strip Heatmap & Slitting Optimizer                         |
|  - /api/certificate: ASTM Compliance & Grade Disposition Generator                |
+------------------------------------------+----------------------------------------+
                                           | In-Memory Engine / Tensor Runtime
+------------------------------------------v----------------------------------------+
|                    Core Computer Vision & Analytics Pipeline                       |
|  - Deep Learning Engine: PyTorch / TorchScript / ONNX Edge Runtime                |
|  - Defect Severity Calculator: DSI = f(Area%, Gradient Contrast, Aspect Ratio)    |
|  - Spatial Frequency Analyzer: Autocorrelation & Discrete Fourier Transform       |
|  - Synthetic Edge Defect Generator for Stress Testing & Validation                |
+-----------------------------------------------------------------------------------+
```

---

### 5. Implementation Milestones & Roadmap
- [x] **Phase 1: Problem Analysis & Strategic Ideation** (Understanding JSL criteria, drafting plan.md & pipeline.md)
- [ ] **Phase 2: Core CV & Detection Engine** (PyTorch/OpenCV pipeline, 8-class defect inference, bounding boxes, segmentation masks, DSI metrics)
- [ ] **Phase 3: Industrial Intelligence Modules**:
  - Roll-Mark FFT Periodicity & Roll Stand Root-Cause Analyzer
  - JSL Steel Grade Tolerancing Engine (Austenitic vs Ferritic rules)
  - Coil Digital Twin & Smart Slitting Yield Optimizer
- [ ] **Phase 4: High-Performance Backend Service** (FastAPI asynchronous endpoints, streaming simulation, image processing)
- [ ] **Phase 5: World-Class Industrial UI (Frontend)** (Dark glassmorphic SCADA design, dynamic inspection canvas, live speed feed, interactive strip map, exportable certificates)
- [ ] **Phase 6: Verification, Testing & Demonstration** (Real-time FPS benchmarking, test suite with sample steel defect images, end-to-end user experience audit)

---

### 6. Deliverables
1. `plan.md`: High-level strategic implementation plan (this document).
2. `pipeline.md`: In-depth end-to-end CV/AI and industrial manufacturing pipeline specification.
3. `backend/`: FastAPI server with clean modular structure (`detector.py`, `periodicity.py`, `grades.py`, `coil_twin.py`, `server.py`).
4. `frontend/`: Single-page industrial application with responsive layout, real-time telemetry, and Jindal Stainless branding.
5. `sample_defects/`: Curated repository of test images representing all 8 steel defect classes and benchmark scenarios.
6. `README.md`: Professional project documentation with setup guide, business value breakdown, and live demo instructions.
