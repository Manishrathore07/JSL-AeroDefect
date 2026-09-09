"""
JSL-AeroDefect: 2D Coil Digital Twin & Smart Slitting Yield Optimizer
Models a full 1,500-meter x 1,250-millimeter stainless steel coil (20-25 MT) in real-time,
aggregates defect spatial distribution, and computes mathematical shearing/slitting
coordinates to salvage prime steel yield and eliminate massive downgrade losses.
"""

import random
import numpy as np

class CoilDigitalTwin:
    """
    Maintains a 2D spatial coordinate map of the full production coil:
    Length: 0 to 1,500 meters
    Width: 0 to 1,250 mm (Drive Side, Center Lane, Work Side)
    """
    def __init__(self, coil_id="JSL-CR-2026-9842", grade="304", total_length_m=1500.0, strip_width_mm=1250.0, thickness_mm=1.5):
        self.coil_id = coil_id
        self.grade = grade
        self.total_length_m = total_length_m
        self.strip_width_mm = strip_width_mm
        self.thickness_mm = thickness_mm
        
        # Steel density: 7.93 g/cm^3 for stainless steel 304/316
        volume_m3 = (total_length_m) * (strip_width_mm / 1000.0) * (thickness_mm / 1000.0)
        self.total_weight_mt = round(volume_m3 * 7.93, 2)  # Metric tons

    def generate_simulated_coil_run(self, defect_density="MODERATE"):
        """
        Generates a realistic spatial defect map for an entire cold-rolling coil run.
        Simulates realistic industrial defect clustering:
        - Head and tail defects (threading tension instabilities)
        - Periodic roll marks
        - Edge cracking on drive or work side
        """
        np.random.seed(101)
        defects = []
        
        # 1. Head end threading defects (first 40m)
        num_head_defects = np.random.randint(5, 12)
        for _ in range(num_head_defects):
            defects.append({
                "id": f"COIL-DEF-{len(defects)+1:04d}",
                "class_id": "RS" if np.random.rand() > 0.5 else "SC",
                "class_name": "Rolled-in Scale" if np.random.rand() > 0.5 else "Scratch",
                "length_pos_m": round(float(np.random.uniform(2.0, 38.0)), 2),
                "width_pos_mm": round(float(np.random.uniform(50.0, self.strip_width_mm - 50.0)), 1),
                "dsi": round(float(np.random.uniform(45.0, 75.0)), 1),
                "lane": "Head Crop Zone"
            })

        # 2. Periodic roll mark sequence from Stand F3 (period ~1.07 meters)
        start_rm_m = 320.0
        rm_period_m = 1.068
        for i in range(18):
            defects.append({
                "id": f"COIL-DEF-{len(defects)+1:04d}",
                "class_id": "RM",
                "class_name": "Roll Mark",
                "length_pos_m": round(start_rm_m + (i * rm_period_m) + np.random.normal(0, 0.02), 3),
                "width_pos_mm": round(float(620.0 + np.random.normal(0, 5.0)), 1),
                "dsi": round(float(np.random.uniform(55.0, 70.0)), 1),
                "lane": "Center Lane"
            })

        # 3. Edge cracks along Drive Side (0-60mm from edge)
        for _ in range(14):
            pos_m = float(np.random.uniform(400.0, 1100.0))
            defects.append({
                "id": f"COIL-DEF-{len(defects)+1:04d}",
                "class_id": "EC",
                "class_name": "Edge Crack",
                "length_pos_m": round(pos_m, 2),
                "width_pos_mm": round(float(np.random.uniform(5.0, 45.0)), 1),
                "dsi": round(float(np.random.uniform(60.0, 85.0)), 1),
                "lane": "Drive Side Edge"
            })

        # 4. Sporadic inclusions or pits
        for _ in range(8):
            defects.append({
                "id": f"COIL-DEF-{len(defects)+1:04d}",
                "class_id": "IN" if np.random.rand() > 0.5 else "PS",
                "class_name": "Inclusion" if np.random.rand() > 0.5 else "Pitted Surface",
                "length_pos_m": round(float(np.random.uniform(100.0, 1450.0)), 2),
                "width_pos_mm": round(float(np.random.uniform(150.0, self.strip_width_mm - 150.0)), 1),
                "dsi": round(float(np.random.uniform(30.0, 65.0)), 1),
                "lane": "Body Center"
            })

        defects.sort(key=lambda x: x["length_pos_m"])
        return defects

    def compute_smart_slitting_plan(self, defects, grade_prices):
        """
        Evaluates defect clusters and calculates mathematical slitting & trimming recommendations:
        - Head & tail crop shear points
        - Longitudinal edge trimming (e.g. side-trim Drive Side by 60mm)
        - Computes prime yield recovered vs full coil downgrade
        """
        market_price = grade_prices["market_price_per_ton_inr"]
        scrap_price = grade_prices["scrap_price_per_ton_inr"]
        price_diff = market_price - scrap_price

        # Check edge crack density
        drive_side_cracks = [d for d in defects if d["class_id"] == "EC" and d["width_pos_mm"] < 100]
        work_side_cracks = [d for d in defects if d["class_id"] == "EC" and d["width_pos_mm"] > (self.strip_width_mm - 100)]

        # Slitting decisions
        head_crop_m = 42.0  # Cut off first 42m containing threading defects
        tail_crop_m = 18.0  # Cut off last 18m
        
        drive_side_trim_mm = 65.0 if len(drive_side_cracks) >= 3 else 25.0
        work_side_trim_mm = 65.0 if len(work_side_cracks) >= 3 else 25.0

        effective_length_m = self.total_length_m - head_crop_m - tail_crop_m
        effective_width_mm = self.strip_width_mm - drive_side_trim_mm - work_side_trim_mm

        # Salvaged Prime Volume & Weight
        prime_volume_m3 = effective_length_m * (effective_width_mm / 1000.0) * (self.thickness_mm / 1000.0)
        prime_weight_mt = round(prime_volume_m3 * 7.93, 2)
        scrap_weight_mt = round(self.total_weight_mt - prime_weight_mt, 2)
        
        prime_yield_pct = round((prime_weight_mt / self.total_weight_mt) * 100.0, 1)

        # Economic calculation
        # If no smart slitting: entire coil downgraded to Secondary or Scrap
        without_slitting_loss_inr = self.total_weight_mt * price_diff
        with_slitting_loss_inr = scrap_weight_mt * price_diff
        money_saved_inr = round(without_slitting_loss_inr - with_slitting_loss_inr, 0)

        # 2D Heatmap Grid for visual representation (50 longitudinal bins x 20 width bins)
        grid_l = 50
        grid_w = 20
        heatmap_matrix = np.zeros((grid_w, grid_l), dtype=int)
        
        for d in defects:
            l_idx = min(grid_l - 1, int((d["length_pos_m"] / self.total_length_m) * grid_l))
            w_idx = min(grid_w - 1, int((d["width_pos_mm"] / self.strip_width_mm) * grid_w))
            heatmap_matrix[w_idx, l_idx] += 1

        heatmap_list = heatmap_matrix.tolist()

        return {
            "coil_metadata": {
                "coil_id": self.coil_id,
                "grade": self.grade,
                "total_length_m": self.total_length_m,
                "strip_width_mm": self.strip_width_mm,
                "thickness_mm": self.thickness_mm,
                "total_weight_mt": self.total_weight_mt,
                "total_defects_count": len(defects)
            },
            "smart_slitting_recommendation": {
                "head_crop_shear_m": head_crop_m,
                "tail_crop_shear_m": tail_crop_m,
                "drive_side_trim_mm": drive_side_trim_mm,
                "work_side_trim_mm": work_side_trim_mm,
                "resultant_prime_width_mm": effective_width_mm,
                "slitting_pattern": f"Shear head 0-{head_crop_m}m + Slit {drive_side_trim_mm}mm drive-side edge -> Salvages {effective_width_mm}mm Prime Master Strip"
            },
            "yield_impact": {
                "prime_weight_salvaged_mt": prime_weight_mt,
                "scrap_weight_mt": scrap_weight_mt,
                "prime_yield_pct": prime_yield_pct,
                "without_optimization_yield_pct": 0.0,  # Entire coil would be downgraded
            },
            "economic_roi": {
                "currency": "INR",
                "money_saved_per_coil_inr": money_saved_inr,
                "money_saved_per_coil_lakhs": round(money_saved_inr / 100000.0, 2),
                "market_ton_rate_inr": market_price,
                "annual_savings_potential_crores": round((money_saved_inr * 2500) / 10000000.0, 2)  # Based on 2,500 coils/year line capacity
            },
            "heatmap_grid": {
                "length_bins": grid_l,
                "width_bins": grid_w,
                "matrix": heatmap_list
            },
            "defects_sample": defects[:25]
        }
