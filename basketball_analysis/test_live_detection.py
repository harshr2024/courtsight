#!/usr/bin/env python3
"""
Test Live Basketball Score Detection

This script tests the live detection system using a test video file
instead of a live camera feed.
"""

import cv2
import numpy as np
import os
import sys
from live_score_detector import LiveScoreDetector

def create_test_video():
    """Create a simple test video for testing."""
    test_video_path = "test_live_video.mp4"
    
    # Create a simple video with moving circles (simulating ball and hoops)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(test_video_path, fourcc, 30, (640, 480))
    
    for frame_num in range(300):  # 10 seconds at 30fps
        # Create frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Draw "hoops" (circles)
        cv2.circle(frame, (100, 240), 30, (0, 255, 0), 2)  # Left hoop
        cv2.circle(frame, (540, 240), 30, (0, 255, 0), 2)  # Right hoop
        
        # Draw "ball" (moving circle)
        ball_x = 320 + int(100 * np.sin(frame_num * 0.1))
        ball_y = 240 + int(50 * np.cos(frame_num * 0.15))
        cv2.circle(frame, (ball_x, ball_y), 15, (255, 0, 0), -1)
        
        # Add some "scores" by moving ball near hoops
        if frame_num in [50, 150, 250]:  # Simulate scores
            ball_x = 100  # Near left hoop
            ball_y = 240
            cv2.circle(frame, (ball_x, ball_y), 15, (255, 0, 0), -1)
        
        out.write(frame)
    
    out.release()
    return test_video_path

def test_live_detection_with_video(video_path):
    """Test live detection using a video file instead of camera."""
    detector = LiveScoreDetector()
    
    # Open video file instead of camera
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Could not open video file: {video_path}")
        return
    
    detector.cap = cap
    detector.is_running = True
    
    print("Testing live detection with video file...")
    print("Press 'q' to quit, 'r' to reset score")
    
    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            processed_frame, score_detected = detector.process_frame(frame)
            
            # Display frame
            cv2.imshow('Test Live Detection', processed_frame)
            
            if score_detected:
                print(f"SCORE DETECTED! Frame {frame_count}")
                print(f"Current Score - Team 1: {detector.score_team1}, Team 2: {detector.score_team2}")
            
            frame_count += 1
            
            # Handle key presses
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                detector.reset_score()
                print("Score reset!")
    
    except KeyboardInterrupt:
        print("Stopping test...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        # Print final results
        final_score = detector.get_current_score()
        print(f"\nTest completed!")
        print(f"Final Score - Team 1: {final_score['team1']}, Team 2: {final_score['team2']}")
        print(f"Total frames processed: {frame_count}")

def main():
    """Main test function."""
    print("Basketball Live Detection Test")
    print("=" * 40)
    
    # Check if test video exists, create if not
    test_video_path = "test_live_video.mp4"
    if not os.path.exists(test_video_path):
        print("Creating test video...")
        test_video_path = create_test_video()
        print(f"Test video created: {test_video_path}")
    
    # Test the live detection system
    test_live_detection_with_video(test_video_path)
    
    # Clean up test video
    if os.path.exists(test_video_path):
        os.remove(test_video_path)
        print("Test video cleaned up")

if __name__ == '__main__':
    main() 