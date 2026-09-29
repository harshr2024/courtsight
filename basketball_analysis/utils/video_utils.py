"""
A module for reading and writing video files.

This module provides utility functions to load video frames into memory and save
processed frames back to video files, with support for common video formats.
"""

from dataclasses import dataclass
import cv2
import os


@dataclass(frozen=True)
class VideoMetadata:
    source_fps: float
    output_fps: float
    source_width: int
    source_height: int
    output_width: int
    output_height: int
    source_frame_count: int
    processed_frame_count: int
    frame_skip: int

def read_video(video_path, max_frames=None, frame_skip=1, target_width=None, return_metadata=False):
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
    if frame_skip < 1:
        raise ValueError("frame_skip must be at least 1")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    frames = []
    source_frame_index = 0
    
    # Get original video properties
    original_fps = float(cap.get(cv2.CAP_PROP_FPS))
    if original_fps <= 0:
        raise ValueError(f"Video reports an invalid FPS: {original_fps}")
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    original_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
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
        
        # Keep frame zero, then every Nth source frame. Output FPS is derived
        # after reading so the represented input duration remains correct.
        if source_frame_index % frame_skip != 0:
            source_frame_index += 1
            continue
        
        # Resize if needed
        if resize:
            frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
        
        frames.append(frame)
        source_frame_index += 1
        
        # Stop if max_frames reached
        if max_frames and len(frames) >= max_frames:
            break
    
    cap.release()
    output_width = target_width if resize else original_width
    output_height = target_height if resize else original_height
    represented_source_frames = min(
        original_frame_count if original_frame_count > 0 else len(frames) * frame_skip,
        len(frames) * frame_skip,
    )
    represented_duration = represented_source_frames / original_fps
    output_fps = (
        len(frames) / represented_duration
        if represented_duration > 0
        else original_fps / frame_skip
    )
    metadata = VideoMetadata(
        source_fps=original_fps,
        output_fps=output_fps,
        source_width=original_width,
        source_height=original_height,
        output_width=output_width,
        output_height=output_height,
        source_frame_count=original_frame_count,
        processed_frame_count=len(frames),
        frame_skip=frame_skip,
    )
    print(
        f"Loaded {len(frames)} frames from video "
        f"(source_fps={original_fps:.3f}, output_fps={metadata.output_fps:.3f}, "
        f"skip={frame_skip}, resize={output_width}x{output_height})"
    )
    return (frames, metadata) if return_metadata else frames

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
    output_directory = os.path.dirname(output_video_path)
    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
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
    if not os.path.exists(output_video_path) or os.path.getsize(output_video_path) == 0:
        raise RuntimeError(f"Video writer produced no output: {output_video_path}")
    print(f"Saved video to {output_video_path}")
