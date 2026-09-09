"""
Generate authentic benchmark dataset in sample_defects/
Covers all 8 Jindal Stainless defect classes plus clean prime steel.
"""

import os
import cv2
from detector import generate_synthetic_defect_sample

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_defects")
os.makedirs(SAMPLES_DIR, exist_ok=True)

DEFECT_TYPES = ["SC", "RS", "RM", "EC", "IN", "PA", "PS", "CR"]

def generate_all_samples():
    print(f"Generating high-resolution benchmark samples in: {SAMPLES_DIR}")
    # 1. Clean Prime Steel
    clean_img = generate_synthetic_defect_sample("CLEAN", 512, 512)
    # Remove any defect drawings for clean
    clean_gray = cv2.cvtColor(clean_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "clean_prime_steel.jpg"), clean_img)
    print(" -> Saved clean_prime_steel.jpg")

    # 2. Each of the 8 classes
    for dtype in DEFECT_TYPES:
        img = generate_synthetic_defect_sample(dtype, 512, 512)
        filename = f"sample_{dtype.lower()}.jpg"
        filepath = os.path.join(SAMPLES_DIR, filename)
        cv2.imwrite(filepath, img)
        print(f" -> Saved {filename} ({dtype})")

if __name__ == "__main__":
    generate_all_samples()
