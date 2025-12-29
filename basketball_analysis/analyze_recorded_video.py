#!/usr/bin/env python3
"""
Analyze Recorded Basketball Video

This script runs the full basketball analysis on recorded videos from the live detection system.
It processes the video with all the original analysis features (player tracking, passes, etc.).
"""

import os
# Force CPU mode to avoid CUDA errors - must be set before importing torch/ultralytics
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Disable CUDA
import argparse
import sys
from main import main as run_full_analysis

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Analyze Recorded Basketball Video')
    parser.add_argument('input_video', type=str, 
                       help='Path to recorded video file')
    parser.add_argument('--output_video', type=str, default='output_videos/analyzed_video.mp4',
                       help='Path to output analyzed video file')
    parser.add_argument('--stub_path', type=str, default='stubs/',
                       help='Path to stub directory')
    parser.add_argument('--skip_stubs', action='store_true',
                       help='Skip using stubs and run full detection')
    parser.add_argument('--frame_skip', type=int, default=2,
                       help='Process every Nth frame (default: 2)')
    parser.add_argument('--target_width', type=int, default=1280,
                       help='Resize frames to this width (default: 1280, 0 = no resize)')
    parser.add_argument('--max_frames', type=int, default=None,
                       help='Maximum number of frames to process')
    
    return parser.parse_args()

def main():
    """Main function to run analysis on recorded video."""
    args = parse_args()
    
    # Check if input video exists
    if not os.path.exists(args.input_video):
        print(f"Error: Input video file not found at {args.input_video}")
        print("Please ensure the video file exists.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output_video), exist_ok=True)
    
    # Create stub directory if it doesn't exist
    if not args.skip_stubs:
        os.makedirs(args.stub_path, exist_ok=True)
    
    print(f"Analyzing recorded video: {args.input_video}")
    print(f"Output will be saved to: {args.output_video}")
    
    if args.skip_stubs:
        print("Running full detection (not using stubs)")
    else:
        print(f"Using stubs from: {args.stub_path}")
    
    # Run the full analysis using the original main function
    # We need to modify sys.argv to pass arguments to the original main function
    original_argv = sys.argv.copy()
    sys.argv = [
        'main.py',
        args.input_video,
        '--output_video', args.output_video,
        '--stub_path', args.stub_path,
        '--frame_skip', str(args.frame_skip),
        '--target_width', str(args.target_width)
    ]
    if args.max_frames:
        sys.argv.extend(['--max_frames', str(args.max_frames)])
    
    try:
        run_full_analysis()
        print(f"\nAnalysis complete! Output saved to: {args.output_video}")
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)
    finally:
        # Restore original argv
        sys.argv = original_argv

if __name__ == '__main__':
    main() 