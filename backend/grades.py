"""
JSL-AeroDefect: Stainless Steel Grade-Adaptive Quality Tolerancing Matrix
Defines metallurgical quality criteria, critical defect limits, and automated disposition
for Jindal Stainless grades: Austenitic 304/316L, Ferritic 430, Utensil 201, and Duplex 2205.
"""

GRADE_MATRIX = {
    "316L": {
        "name": "Austenitic 316L (Marine / Pharma / Cleanroom)",
        "series": "300 Series (Mo-alloyed)",
        "surface_finish": "No. 4 / 2B High Purity",
        "description": "High-end molybdenum-alloyed steel for pharmaceutical tanks, chemical reactors, and marine environments. Strict zero-tolerance for pitting or slag inclusions.",
        "max_allowable_dsi": 30.0,
        "critical_classes": ["IN", "PS", "EC"],  # Inclusion, Pitting, Edge Crack are automatic rejections
        "tolerances": {
            "IN": {"max_dsi": 15.0, "disposition_if_exceeded": "SCRAP"},
            "PS": {"max_dsi": 10.0, "disposition_if_exceeded": "SCRAP"},
            "SC": {"max_dsi": 25.0, "disposition_if_exceeded": "REWORK"},
            "EC": {"max_dsi": 20.0, "disposition_if_exceeded": "SLIT_TRIM"},
            "RM": {"max_dsi": 25.0, "disposition_if_exceeded": "REWORK"},
            "RS": {"max_dsi": 20.0, "disposition_if_exceeded": "REWORK"},
            "PA": {"max_dsi": 30.0, "disposition_if_exceeded": "REWORK"},
            "CR": {"max_dsi": 20.0, "disposition_if_exceeded": "SCRAP"}
        },
        "market_price_per_ton_inr": 285000,
        "scrap_price_per_ton_inr": 135000,
    },
    "304": {
        "name": "Austenitic 304 (Architecture / Dairy / Food Service)",
        "series": "300 Series (18/8 Chrome-Nickel)",
        "surface_finish": "Bright Annealed (BA) / 2B",
        "description": "The most widely produced stainless steel. Highly sensitive to visual aesthetics (scratches, roll marks) and hygienic cleanability in food processing.",
        "max_allowable_dsi": 40.0,
        "critical_classes": ["SC", "RM", "EC"],
        "tolerances": {
            "IN": {"max_dsi": 30.0, "disposition_if_exceeded": "SECONDARY"},
            "PS": {"max_dsi": 25.0, "disposition_if_exceeded": "REWORK"},
            "SC": {"max_dsi": 20.0, "disposition_if_exceeded": "REWORK"},
            "EC": {"max_dsi": 20.0, "disposition_if_exceeded": "SLIT_TRIM"},
            "RM": {"max_dsi": 25.0, "disposition_if_exceeded": "REWORK"},
            "RS": {"max_dsi": 30.0, "disposition_if_exceeded": "REWORK"},
            "PA": {"max_dsi": 35.0, "disposition_if_exceeded": "SECONDARY"},
            "CR": {"max_dsi": 30.0, "disposition_if_exceeded": "SECONDARY"}
        },
        "market_price_per_ton_inr": 210000,
        "scrap_price_per_ton_inr": 115000,
    },
    "430": {
        "name": "Ferritic 430 (Automotive Trim / Exhaust / Appliances)",
        "series": "400 Series (Straight Chromium, Nickel-Free)",
        "surface_finish": "2B / No. 1",
        "description": "Magnetic ferritic steel used in automotive exhaust tubing and home appliances. Tolerant to mild surface blemishes, but highly vulnerable to edge cracking during cold deep-drawing.",
        "max_allowable_dsi": 55.0,
        "critical_classes": ["EC", "CR"],
        "tolerances": {
            "IN": {"max_dsi": 45.0, "disposition_if_exceeded": "SECONDARY"},
            "PS": {"max_dsi": 40.0, "disposition_if_exceeded": "CONCESSION"},
            "SC": {"max_dsi": 40.0, "disposition_if_exceeded": "CONCESSION"},
            "EC": {"max_dsi": 20.0, "disposition_if_exceeded": "SLIT_TRIM"},
            "RM": {"max_dsi": 40.0, "disposition_if_exceeded": "CONCESSION"},
            "RS": {"max_dsi": 35.0, "disposition_if_exceeded": "REWORK"},
            "PA": {"max_dsi": 50.0, "disposition_if_exceeded": "CONCESSION"},
            "CR": {"max_dsi": 35.0, "disposition_if_exceeded": "SECONDARY"}
        },
        "market_price_per_ton_inr": 140000,
        "scrap_price_per_ton_inr": 72000,
    },
    "201": {
        "name": "Austenitic 201 (Utensils / Consumer Hollowware)",
        "series": "200 Series (Manganese-substituted)",
        "surface_finish": "2B / No. 4",
        "description": "Cost-effective stainless grade for kitchen cookware, hollowware, and decorative tubing. High mechanical formability; moderate tolerance for cosmetic anomalies.",
        "max_allowable_dsi": 65.0,
        "critical_classes": ["EC"],
        "tolerances": {
            "IN": {"max_dsi": 60.0, "disposition_if_exceeded": "CONCESSION"},
            "PS": {"max_dsi": 50.0, "disposition_if_exceeded": "CONCESSION"},
            "SC": {"max_dsi": 45.0, "disposition_if_exceeded": "CONCESSION"},
            "EC": {"max_dsi": 25.0, "disposition_if_exceeded": "SLIT_TRIM"},
            "RM": {"max_dsi": 50.0, "disposition_if_exceeded": "CONCESSION"},
            "RS": {"max_dsi": 50.0, "disposition_if_exceeded": "CONCESSION"},
            "PA": {"max_dsi": 60.0, "disposition_if_exceeded": "CONCESSION"},
            "CR": {"max_dsi": 45.0, "disposition_if_exceeded": "CONCESSION"}
        },
        "market_price_per_ton_inr": 125000,
        "scrap_price_per_ton_inr": 68000,
    }
}

class GradeDispositionEngine:
    """
    Evaluates detected defects against specific JSL grade tolerance rules
    and computes overall disposition: PRIME, CONCESSION, REWORK, SLIT_TRIM, or SCRAP.
    """
    def evaluate(self, detections, grade_key="304"):
        grade_info = GRADE_MATRIX.get(grade_key, GRADE_MATRIX["304"])
        tolerances = grade_info["tolerances"]
        
        reasons = []
        severity_verdicts = []
        
        for det in detections:
            cid = det["class_id"]
            dsi = det["dsi"]
            
            rule = tolerances.get(cid, {"max_dsi": 40.0, "disposition_if_exceeded": "SECONDARY"})
            
            if dsi > rule["max_dsi"]:
                disposition = rule["disposition_if_exceeded"]
                severity_verdicts.append(disposition)
                reasons.append(
                    f"{det['class_name']} ({det['id']}) with DSI {dsi} exceeded Grade {grade_key} tolerance ({rule['max_dsi']}) -> Action: {disposition}"
                )
        
        # Priority order of overall coil status: SCRAP > SLIT_TRIM > REWORK > SECONDARY > CONCESSION > PRIME
        if "SCRAP" in severity_verdicts:
            overall_disposition = "SCRAP"
            badge_color = "#ef4444"
            summary = "COIL REJECTED: Critical metallurgical flaws exceed structural tolerance."
        elif "SLIT_TRIM" in severity_verdicts:
            overall_disposition = "SLIT_TRIM_REQUIRED"
            badge_color = "#f97316"
            summary = "EDGE TRIMMING MANDATED: Edge tears detected; side-slitting required to preserve prime center strip."
        elif "REWORK" in severity_verdicts:
            overall_disposition = "REWORK_REQUIRED"
            badge_color = "#eab308"
            summary = "SURFACE REWORK REQUIRED: Route to Annealing & Pickling or buffing line."
        elif "SECONDARY" in severity_verdicts:
            overall_disposition = "SECONDARY_DOWNGRADE"
            badge_color = "#a855f7"
            summary = "DOWNGRADE TO SECONDARY: Minor defects disqualify from prime export, acceptable for domestic secondary market."
        elif "CONCESSION" in severity_verdicts:
            overall_disposition = "CONCESSION_ACCEPTABLE"
            badge_color = "#3b82f6"
            summary = "PASS WITH CONCESSION: Blemishes within customer-negotiated non-critical tolerance."
        else:
            overall_disposition = "PRIME_QUALITY"
            badge_color = "#10b981"
            summary = f"PRIME GRADE APPROVED: Full compliance with ASTM A240 / A480 specifications for Grade {grade_key}."

        return {
            "grade_key": grade_key,
            "grade_name": grade_info["name"],
            "surface_finish": grade_info["surface_finish"],
            "overall_disposition": overall_disposition,
            "badge_color": badge_color,
            "summary": summary,
            "violations_count": len(reasons),
            "violation_details": reasons,
            "market_price_per_ton_inr": grade_info["market_price_per_ton_inr"],
            "scrap_price_per_ton_inr": grade_info["scrap_price_per_ton_inr"],
        }
