#!/usr/bin/env python3
"""
Setup Live Basketball Score Detection

This script helps users set up and configure the live detection system.
"""

import os
import sys
import cv2
import subprocess

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    try:
        import cv2
        print("✓ OpenCV installed")
    except ImportError:
        print("✗ OpenCV not found. Install with: pip install opencv-python")
        return False
    
    try:
        import numpy
        print("✓ NumPy installed")
    except ImportError:
        print("✗ NumPy not found. Install with: pip install numpy")
        return False
    
    try:
        from ultralytics import YOLO
        print("✓ Ultralytics installed")
    except ImportError:
        print("✗ Ultralytics not found. Install with: pip install ultralytics")
        return False
    
    try:
        import supervision
        print("✓ Supervision installed")
    except ImportError:
        print("✗ Supervision not found. Install with: pip install supervision")
        return False
    
    return True

def check_models():
    """Check if required models are available."""
    print("\nChecking models...")
    
    models_dir = "models"
    if not os.path.exists(models_dir):
        print(f"✗ Models directory not found: {models_dir}")
        return False
    
    ball_model_path = os.path.join(models_dir, "ball_detector_model.pt")
    if not os.path.exists(ball_model_path):
        print(f"✗ Ball detection model not found: {ball_model_path}")
        print("Please ensure the ball detection model is available.")
        return False
    
    print("✓ Ball detection model found")
    return True

def test_camera():
    """Test camera access."""
    print("\nTesting camera access...")
    
    # Try different camera indices
    for camera_index in range(3):
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✓ Camera {camera_index} is available")
                print(f"  Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
                print(f"  FPS: {int(cap.get(cv2.CAP_PROP_FPS))}")
                cap.release()
                return camera_index
            cap.release()
    
    print("✗ No camera found. Please check camera connection and permissions.")
    return None

def create_directories():
    """Create necessary directories."""
    print("\nCreating directories...")
    
    directories = [
        "output_videos",
        "stubs",
        "models"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory exists: {directory}")

def run_test():
    """Run a quick test of the system."""
    print("\nRunning system test...")
    
    try:
        # Import and test the live detector
        from live_score_detector import LiveScoreDetector
        
        # Create detector instance
        detector = LiveScoreDetector()
        print("✓ LiveScoreDetector initialized successfully")
        
        # Test with a simple frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        processed_frame, score_detected = detector.process_frame(test_frame)
        print("✓ Frame processing test passed")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("Basketball Live Detection Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies and run setup again.")
        return False
    
    # Check models
    if not check_models():
        print("\nPlease ensure required models are available.")
        return False
    
    # Create directories
    create_directories()
    
    # Test camera
    camera_index = test_camera()
    if camera_index is None:
        print("\nCamera test failed. You can still use the system with a different camera index.")
    else:
        print(f"\nRecommended camera index: {camera_index}")
    
    # Run system test
    if run_test():
        print("\n✓ Setup completed successfully!")
        print("\nYou can now run the live detection system:")
        print(f"  python live_main.py --camera {camera_index if camera_index is not None else 0}")
        print("\nOr test with a video file:")
        print("  python test_live_detection.py")
        return True
    else:
        print("\n✗ Setup failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    import numpy as np
    success = main()
    sys.exit(0 if success else 1) 