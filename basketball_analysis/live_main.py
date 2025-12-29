#!/usr/bin/env python3
"""
Live Basketball Score Detection

This script runs real-time basketball score detection from a live camera feed.
It detects basketball hoops, tracks ball movement, and counts scores in real-time.
"""

import argparse
import sys
import os
from live_score_detector import LiveScoreDetector

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Live Basketball Score Detection')
    parser.add_argument('--camera', type=int, default=0, 
                       help='Camera index (default: 0)')
    parser.add_argument('--model', type=str, default='models/ball_detector_model.pt',
                       help='Path to ball detection model')
    parser.add_argument('--cooldown', type=float, default=3.0,
                       help='Score detection cooldown in seconds (default: 3.0)')
    parser.add_argument('--distance-threshold', type=int, default=50,
                       help='Ball-hoop distance threshold for score detection (default: 50)')
    parser.add_argument('--min-velocity', type=float, default=5.0,
                       help='Minimum ball velocity for score detection (default: 5.0)')
    parser.add_argument('--save-video', type=str, default=None,
                       help='Path to save recorded video (optional)')
    parser.add_argument('--record-analysis', action='store_true',
                       help='Record video for later analysis')
    
    return parser.parse_args()

def main():
    """Main function to run live score detection."""
    args = parse_args()
    
    # Check if model file exists
    if not os.path.exists(args.model):
        print(f"Error: Model file not found at {args.model}")
        print("Please ensure the ball detection model is available.")
        sys.exit(1)
    
    try:
        # Initialize live score detector
        detector = LiveScoreDetector(
            camera_index=args.camera,
            model_path=args.model
        )
        
        # Configure detection parameters
        detector.score_cooldown = args.cooldown
        detector.ball_hoop_distance_threshold = args.distance_threshold
        detector.min_ball_velocity = args.min_velocity
        
        # Setup video recording if requested
        if args.save_video:
            detector.setup_video_recording(args.save_video)
        
        # Setup analysis recording if requested
        if args.record_analysis:
            detector.record_analysis = True
        
        print("Initializing live score detection...")
        print(f"Camera index: {args.camera}")
        print(f"Model path: {args.model}")
        print(f"Score cooldown: {args.cooldown}s")
        print(f"Distance threshold: {args.distance_threshold}px")
        print(f"Min velocity: {args.min_velocity}")
        
        if args.save_video:
            print(f"Recording video to: {args.save_video}")
        
        if args.record_analysis:
            print("Recording frames for later analysis")
        
        # Start live detection
        detector.start_live_detection()
        
    except KeyboardInterrupt:
        print("\nStopping live detection...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # Print final score
        if 'detector' in locals():
            final_score = detector.get_current_score()
            print(f"\nFinal Score - Team 1: {final_score['team1']}, Team 2: {final_score['team2']}")

if __name__ == '__main__':
    main() 