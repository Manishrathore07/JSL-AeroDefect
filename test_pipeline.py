"""
Automated Verification & Pipeline Test Suite for JSL-AeroDefect
Tests detector, periodicity analyzer, grade disposition, and coil digital twin.
"""

import os
import sys
import numpy as np
import cv2

# Add backend directory
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from detector import SteelDefectDetector, DEFECT_CLASSES, generate_synthetic_defect_sample
from periodicity import RollMarkPeriodicityAnalyzer
from grades import GradeDispositionEngine, GRADE_MATRIX
from coil_twin import CoilDigitalTwin

def test_detector_inference():
    print("Testing SteelDefectDetector inference...")
    detector = SteelDefectDetector()
    
    # Test on Scratch sample
    sample_sc = generate_synthetic_defect_sample("SC", 512, 512)
    res = detector.detect(sample_sc, confidence_threshold=0.25, grade="304")
    
    assert "defect_count" in res, "Result must contain defect_count"
    assert res["defect_count"] > 0, "Must detect at least one scratch defect"
    assert res["max_dsi"] > 0, "DSI must be greater than 0"
    print(f" -> PASS: Detected {res['defect_count']} defects, Max DSI: {res['max_dsi']}")

def test_periodicity_fft():
    print("Testing RollMarkPeriodicityAnalyzer (FFT & Stand Identification)...")
    analyzer = RollMarkPeriodicityAnalyzer()
    
    # Simulate roll mark sequence from Stand F3 (nominal period ~1068mm)
    simulated_positions = [100.0, 1168.0, 2236.0, 3304.0, 4372.0]
    res = analyzer.analyze_periodicity(simulated_positions)
    
    assert res["periodic"] == True, "Should be recognized as periodic"
    assert "Stand F3" in res["identified_stand"], f"Expected Stand F3, got {res['identified_stand']}"
    assert res["estimated_roll_diameter_mm"] > 300, "Estimated diameter should be ~340mm"
    print(f" -> PASS: Identified Stand: {res['identified_stand']} (Period: {res['dominant_period_mm']}mm, Dia: {res['estimated_roll_diameter_mm']}mm, Conf: {res['confidence_pct']}%)")

def test_grade_disposition():
    print("Testing GradeDispositionEngine...")
    engine = GradeDispositionEngine()
    
    # Test 316L (Zero tolerance for pitting)
    pitting_det = [{"class_id": "PS", "class_name": "Pitted Surface", "id": "DEF-001", "dsi": 35.0}]
    res_316 = engine.evaluate(pitting_det, grade_key="316L")
    assert res_316["overall_disposition"] == "SCRAP", f"Expected SCRAP for severe pitting in 316L, got {res_316['overall_disposition']}"
    
    # Test 201 (Permissive on minor defects)
    res_201 = engine.evaluate(pitting_det, grade_key="201")
    assert res_201["overall_disposition"] == "PRIME_QUALITY" or "CONCESSION" in res_201["overall_disposition"], "201 should tolerate DSI 35 pitting"
    print(f" -> PASS: 316L gave {res_316['overall_disposition']}, 201 gave {res_201['overall_disposition']}")

def test_coil_digital_twin():
    print("Testing CoilDigitalTwin & Smart Slitting Optimizer...")
    twin = CoilDigitalTwin(coil_id="JSL-TEST-01", grade="304")
    defects = twin.generate_simulated_coil_run()
    assert len(defects) > 10, "Should generate defects across 1500m coil"
    
    grade_prices = GRADE_MATRIX["304"]
    plan = twin.compute_smart_slitting_plan(defects, grade_prices)
    
    assert plan["yield_impact"]["prime_yield_pct"] > 75.0, "Smart slitting should preserve >75% prime yield"
    assert plan["economic_roi"]["money_saved_per_coil_inr"] > 100000, "ROI savings should be substantial"
    print(f" -> PASS: Prime Yield Salvaged: {plan['yield_impact']['prime_yield_pct']}% | INR Saved per Coil: INR {plan['economic_roi']['money_saved_per_coil_inr']:,.0f}")

if __name__ == "__main__":
    print("=== Running JSL-AeroDefect Automated Test Suite ===")
    test_detector_inference()
    test_periodicity_fft()
    test_grade_disposition()
    test_coil_digital_twin()
    print("=== ALL 4 BACKEND PIPELINE TESTS PASSED SUCCESSFULLY! ===")
