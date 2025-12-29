from ultralytics import YOLO
import supervision as sv
import sys 
import torch
sys.path.append('../')
from utils import read_stub, save_stub

class PlayerTracker:
    """
    A class that handles player detection and tracking using YOLO and ByteTrack.

    This class combines YOLO object detection with ByteTrack tracking to maintain consistent
    player identities across frames while processing detections in batches.
    """
    def __init__(self, model_path):
        """
        Initialize the PlayerTracker with YOLO model and ByteTrack tracker.

        Args:
            model_path (str): Path to the YOLO model weights.
        """
        # Force CPU if CUDA is not available
        device = 'cpu'  # Always use CPU to avoid CUDA errors
        self.model = YOLO(model_path)
        # Set model to CPU explicitly
        if hasattr(self.model, 'to'):
            self.model.to(device)
        self.tracker = sv.ByteTrack()

    def detect_frames(self, frames):
        """
        Detect players in a sequence of frames using batch processing.

        Args:
            frames (list): List of video frames to process.

        Returns:
            list: YOLO detection results for each frame.
        """
        # Increase batch size for better GPU utilization
        batch_size = 32 if len(frames) > 100 else 20
        detections = [] 
        total_batches = (len(frames) + batch_size - 1) // batch_size
        
        for i in range(0, len(frames), batch_size):
            batch_num = (i // batch_size) + 1
            if batch_num % 10 == 0 or batch_num == total_batches:
                print(f"  Processing batch {batch_num}/{total_batches}...")
            
            # Always use CPU to avoid CUDA errors
            detections_batch = self.model.predict(
                frames[i:i+batch_size],
                conf=0.5,
                verbose=False,  # Reduce output
                device='cpu'  # Force CPU
            )
            detections += detections_batch
        return detections

    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None):
        """
        Get player tracking results for a sequence of frames with optional caching.

        Args:
            frames (list): List of video frames to process.
            read_from_stub (bool): Whether to attempt reading cached results.
            stub_path (str): Path to the cache file.

        Returns:
            list: List of dictionaries containing player tracking information for each frame,
                where each dictionary maps player IDs to their bounding box coordinates.
        """
        tracks = read_stub(read_from_stub,stub_path)
        if tracks is not None:
            if len(tracks) == len(frames):
                return tracks

        detections = self.detect_frames(frames)

        tracks=[]

        for frame_num, detection in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {v:k for k,v in cls_names.items()}

            # Covert to supervision Detection format
            detection_supervision = sv.Detections.from_ultralytics(detection)

            # Track Objects
            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)

            tracks.append({})

            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_names_inv['Player']:
                    tracks[frame_num][track_id] = {"bbox":bbox}
        
        save_stub(stub_path,tracks)
        return tracks
