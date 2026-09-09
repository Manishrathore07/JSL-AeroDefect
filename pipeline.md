# End-to-End Industrial CV & Edge Inspection Pipeline
## JSL-AeroDefect: Production-Ready Surface Defect Detection & Root-Cause Pipeline

### 1. Physical Manufacturing Context & Camera Rig Setup
In cold-rolling (CRM) and hot-strip mills (HSM) at Jindal Stainless:
- **Strip Width:** 900 mm to 1,650 mm.
- **Line Speed:** 3 m/s to 12 m/s (up to 720 m/min).
- **Inspection Geometry:** High-speed line-scan cameras (8K resolution, 100 kHz line rate) or multi-area scan matrix cameras installed directly over the strip top and bottom surfaces, illuminated with high-frequency LED strobes (dark-field, bright-field, and retro-reflective angles to isolate both specular reflections and surface relief).

```
                      [Line-Scan Camera Array (8K, 100 kHz)]
                                     |  |  |
               [Coaxial LED]         v  v  v         [Dark-Field Diffuser]
               \                                                       /
========================[ Stainless Steel Strip Motion ----> ]========================
                                     (3 - 12 m/s)
```

---

### 2. Five-Stage Machine Vision Pipeline

```
  +-----------------------------------------------------------------------------+
  | Stage 1: Ingestion & Preprocessing                                          |
  |  - High-speed frame acquisition (RTSP / GenICam / File Stream)              |
  |  - Illumination normalization & CLAHE (Contrast-Limited Adaptive Histogram) |
  |  - Bilateral noise filtering preserving sharp defect edges                 |
  +-------------------------------------+---------------------------------------+
                                        |
  +-------------------------------------v---------------------------------------+
  | Stage 2: Deep Learning Inference Engine                                     |
  |  - Multi-scale Feature Pyramid Network (FPN) backbone                       |
  |  - High-speed Bounding Box Detection + Contour Segmentation                 |
  |  - 8-Class Defect Categorization with Bayesian Confidence Scores           |
  |  - Latency: < 20 ms on CUDA / Edge TensorRT runtime                         |
  +-------------------------------------+---------------------------------------+
                                        |
  +-------------------------------------v---------------------------------------+
  | Stage 3: Defect Characterization & Severity Index (DSI)                     |
  |  - Defect Area calculation ($mm^2$ and % of strip inspection window)       |
  |  - Aspect Ratio $\frac{L}{W}$ (distinguishes continuous scratch vs pit)     |
  |  - Intensity Contrast Profile $\Delta I = |I_{defect} - I_{background}|$    |
  |  - DSI Formulation: $DSI = w_1 \cdot \text{Area} + w_2 \cdot \Delta I$      |
  +-------------------------------------+---------------------------------------+
                                        |
  +-------------------------------------v---------------------------------------+
  | Stage 4: Grade-Adaptive Decision Logic (JSL Steel Matrix)                  |
  |  - Evaluates DSI against Steel Grade rules (304, 316L, 430, 201)           |
  |  - Classification of coil segment: PRIME, REWORKABLE, or SCRAP             |
  |  - False-Alarm Suppression: filters water droplet stains & oil reflections |
  +-------------------------------------+---------------------------------------+
                                        |
  +-------------------------------------v---------------------------------------+
  | Stage 5: Root-Cause Diagnostics & Digital Twin Intelligence                 |
  |  - Spatial FFT on Roll Marks: predicts roll diameter $D = \frac{\Delta x}{\pi}|
  |  - Automatic identification of faulty Work Roll stand ($F_1$ through $F_6$)|
  |  - 2D Strip Map aggregation along full coil length (0 to 1500m)            |
  |  - Smart Slitting Optimizer to maximize Prime Yield ($>88\%$)              |
  +-----------------------------------------------------------------------------+
```

---

### 3. Detailed Algorithmic Specifications

#### A. Preprocessing & Artifact Suppression
Stainless steel has high specular reflectivity (especially 2B and Bright Annealed BA finishes), which often creates glare, oil film sheens, and pseudo-defects.
1. **Adaptive Normalization:**
   $$\hat{I}(x, y) = \frac{I(x, y) - \mu_{\text{local}}}{\sigma_{\text{local}} + \epsilon}$$
2. **Directional Derivative Filtering:**
   To capture longitudinal scratches along the rolling direction ($0^\circ$), directional Sobel kernels highlight longitudinal striations while ignoring isotropic grain noise.

#### B. Defect Severity Index (DSI) Formula
Every defect detected has an associated severity score $0 \le DSI \le 100$:
$$DSI = \min\left(100, \; \left( 40 \times \frac{A_{\text{defect}}}{A_{\text{ref}}} + 35 \times \frac{\Delta I}{I_{\max}} + 25 \times \min\left(5, \frac{L}{W}\right) \times 0.2 \right)\right)$$
Where:
- $A_{\text{defect}}$ is the pixel area of the defect mask.
- $\Delta I$ is the average contrast difference from the ambient stainless surface.
- $\frac{L}{W}$ is the bounding aspect ratio (penalizing long scratches and edge tears).

#### C. Roll-Mark Periodicity & Stand Localization Engine
When a work roll or intermediate roll in a tandem mill suffers spalling or foreign particle indentation, the defect repeats with spatial period:
$$\lambda = \pi \cdot D_{\text{roll}} \cdot (1 + s)$$
where $D_{\text{roll}}$ is the roll diameter and $s$ is the forward slip coefficient ($\approx 0.03 - 0.05$).
1. The pipeline collects longitudinal coordinates $x_1, x_2, \dots, x_k$ of detected roll marks.
2. Spatial autocorrelation and 1D Discrete Fourier Transform (DFT) compute peak dominant wavelengths $\lambda^*$.
3. The system queries the JSL Mill Roll Geometry Table:
   - Stand F1: $D = 420\text{ mm} \implies \lambda \approx 1,320\text{ mm}$
   - Stand F2: $D = 380\text{ mm} \implies \lambda \approx 1,194\text{ mm}$
   - Stand F3: $D = 340\text{ mm} \implies \lambda \approx 1,068\text{ mm}$
   - Stand F4: $D = 300\text{ mm} \implies \lambda \approx 942\text{ mm}$
   - Pinch / Bridle Rolls: $D = 250\text{ mm} \implies \lambda \approx 785\text{ mm}$
4. The system flags the exact stand requiring immediate roll change or grinding.

#### D. JSL Grade-Adaptive Tolerance Rules
| Defect Class | Grade 316L (Pharma/Marine) | Grade 304 (Architecture/Dairy) | Grade 430 (Automotive/Exhaust) | Grade 201 (Utensil/General) |
| :--- | :--- | :--- | :--- | :--- |
| **Inclusion** | CRITICAL (DSI > 15) -> Scrap | HIGH (DSI > 30) -> Secondary | MODERATE (DSI > 45) -> Secondary | LOW (DSI > 60) -> Pass |
| **Pitted Surface** | CRITICAL (DSI > 10) -> Scrap | HIGH (DSI > 25) -> Rework | MODERATE (DSI > 40) -> Pass | LOW (DSI > 50) -> Pass |
| **Scratches** | HIGH (DSI > 25) -> Rework | CRITICAL (DSI > 20) -> Rework | MODERATE (DSI > 40) -> Pass | MODERATE (DSI > 45) -> Pass |
| **Edge Cracks** | CRITICAL (DSI > 20) -> Trim | CRITICAL (DSI > 20) -> Trim | CRITICAL (DSI > 20) -> Trim | CRITICAL (DSI > 25) -> Trim |
| **Roll Marks** | HIGH (DSI > 30) -> Rework | CRITICAL (DSI > 25) -> Rework | MODERATE (DSI > 40) -> Pass | MODERATE (DSI > 50) -> Pass |
| **Rolled-in Scale**| CRITICAL (DSI > 20) -> Pickling | HIGH (DSI > 30) -> Pickling | HIGH (DSI > 35) -> Pickling | MODERATE (DSI > 50) -> Pass |

---

### 4. Edge Latency Budget & Real-Time Performance Target
For a line operating at $10\text{ m/s}$ ($600\text{ m/min}$) with field of view $0.5\text{ m}$ per frame:
- Total Time Window per Frame: $\frac{0.5\text{ m}}{10\text{ m/s}} = 50\text{ ms}$
- Target Processing Budget:
  - Frame Ingestion & Decoupling: **$2.5\text{ ms}$**
  - Preprocessing (CLAHE / Resize): **$4.0\text{ ms}$**
  - Neural Network Inference: **$12.5\text{ ms}$**
  - Severity Calculation & Logic: **$2.0\text{ ms}$**
  - Telemetry / Web Output: **$2.0\text{ ms}$**
  - **Total Pipeline Latency:** $\approx \mathbf{23\text{ ms}}$ (Comfortably below $50\text{ ms}$, ensuring zero frame dropping at full line speed).

---

### 5. Automated Coil Quality Certificate Output (ASTM Standards)
The system synthesizes real-time detections into a formal **Jindal Stainless Quality Inspection Certificate**:
- Standard References: ASTM A240 / A480 (Standard Specification for Chromium and Chromium-Nickel Stainless Steel Plate, Sheet, and Strip).
- Overall Coil Disposition:
  - **Class A Prime (Pass):** Defect density $< 0.05\text{ defects/m}^2$, Zero critical defects.
  - **Class B Secondary (Usable with Concession):** Minor aesthetic blemishes within customer tolerance.
  - **Rework Required:** Annealing & Pickling line re-pass or surface buffing needed.
  - **Scrap / Shear Required:** Slitting plan generated to salvage non-defective tonnage.
