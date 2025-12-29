#!/usr/bin/env python3
"""
Quick test script to verify all models can be loaded.
"""

import os
from ultralytics import YOLO

def test_model(model_path, model_name):
    """Test if a model can be loaded."""
    print(f"\nTesting {model_name}...")
    if not os.path.exists(model_path):
        print(f"  ✗ Model file not found: {model_path}")
        return False
    
    try:
        model = YOLO(model_path)
        print(f"  ✓ {model_name} loaded successfully")
        print(f"    Model type: {type(model)}")
        return True
    except Exception as e:
        print(f"  ✗ Error loading {model_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Testing model loading...")
    
    models = [
        ("models/player_detector.pt", "Player Detector"),
        ("models/ball_detector_model.pt", "Ball Detector"),
        ("models/court_keypoint_detector.pt", "Court Keypoint Detector")
    ]
    
    all_ok = True
    for model_path, model_name in models:
        if not test_model(model_path, model_name):
            all_ok = False
    
    if all_ok:
        print("\n✓ All models loaded successfully!")
    else:
        print("\n✗ Some models failed to load. Check errors above.")


