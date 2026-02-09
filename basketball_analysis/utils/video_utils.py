"""
A module for reading and writing video files.

This module provides utility functions to load video frames into memory and save
processed frames back to video files, with support for common video formats.
"""

import cv2
import os

def read_video(video_path, max_frames=None, frame_skip=1, target_width=None):
    """
    Read frames from a video file into memory with optimizations.
    
    Args:
        video_path (str): Path to the input video file.
        max_frames (int): Maximum number of frames to read (None for all).
        frame_skip (int): Process every Nth frame (1 = all frames, 2 = every other frame, etc.).
        target_width (int): Resize frames to this width (maintains aspect ratio, None for original).
    
    Returns:
        list: List of video frames as numpy arrays.
    """
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_count = 0
    skipped = 0
    
    # Get original video properties
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Calculate target height if resizing
    if target_width and target_width < original_width:
        target_height = int(original_height * (target_width / original_width))
        resize = True
    else:
        resize = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Skip frames if needed
        if skipped < frame_skip - 1:
            skipped += 1
            continue
        skipped = 0
        
        # Resize if needed
        if resize:
            frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
        
        frames.append(frame)
        frame_count += 1
        
        # Stop if max_frames reached
        if max_frames and frame_count >= max_frames:
            break
    
    cap.release()
    print(f"Loaded {len(frames)} frames from video (skip={frame_skip}, resize={target_width if resize else 'none'})")
    return frames

def save_video(output_video_frames, output_video_path, fps=24):
    """
    Save a sequence of frames as a video file with optimizations.
    
    Creates necessary directories if they don't exist and writes frames using efficient codec.
    
    Args:
        output_video_frames (list): List of frames to save.
        output_video_path (str): Path where the video should be saved.
        fps (int): Frames per second for output video.
    """
    if not output_video_frames:
        raise ValueError("No frames to save")
    
    if len(output_video_frames) == 0:
        raise ValueError("Empty frame list - cannot save video")
    
    # If folder doesn't exist, create it
    if not os.path.exists(os.path.dirname(output_video_path)):
        os.makedirs(os.path.dirname(output_video_path))
    
    # Use more efficient codec (H.264 if available, fallback to XVID)
    if output_video_frames[0] is None or len(output_video_frames[0].shape) < 2:
        raise ValueError(f"Invalid frame format at index 0: {type(output_video_frames[0])}")
    
    height, width = output_video_frames[0].shape[:2]
    
    # Try H.264 codecs first (browser-compatible)
    # Try different H.264 fourcc codes
    codecs_to_try = [
        ('avc1', 'H.264/AVC1'),  # H.264 in MP4 container (browser-compatible)
        ('H264', 'H.264'),       # H.264 alternative
        ('mp4v', 'MPEG-4'),      # MPEG-4 Part 2 (fallback, less browser support)
        ('XVID', 'XVID'),        # XVID codec (last resort)
    ]
    
    out = None
    used_codec = None
    for fourcc_str, codec_name in codecs_to_try:
        try:
            fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
            if out.isOpened():
                used_codec = codec_name
                print(f"Using codec: {codec_name} ({fourcc_str})")
                break
        except Exception as e:
            print(f"Failed to initialize codec {fourcc_str}: {e}")
            if out is not None:
                out.release()
            out = None
            continue
    
    if out is None or not out.isOpened():
        raise RuntimeError("Could not initialize video writer with any codec")
    
    for frame in output_video_frames:
        out.write(frame)
    
    out.release()
    print(f"Saved video to {output_video_path}")
