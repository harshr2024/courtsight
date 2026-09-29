from ultralytics import YOLO
import supervision as sv
import sys 
import torch
sys.path.append('../')
from utils import read_stub, save_stub


class CourtKeypointDetector:
    """
    The CourtKeypointDetector class uses a YOLO model to detect court keypoints in image frames. 
    It also provides functionality to draw these detected keypoints on the frames.
    """
    def __init__(self, model_path, device='cpu'):
        self.device = device
        self.model = YOLO(model_path)
        if hasattr(self.model, 'to'):
            self.model.to(self.device)
    
    def get_court_keypoints(self, frames, read_from_stub=False, stub_path=None, cache_key=None):
        """
        Detect court keypoints for a batch of frames using the YOLO model. If requested, 
        attempts to read previously detected keypoints from a stub file before running the model.

        Args:
            frames (list of numpy.ndarray): A list of frames (images) on which to detect keypoints.
            read_from_stub (bool, optional): Indicates whether to read keypoints from a stub file 
                instead of running the detection model. Defaults to False.
            stub_path (str, optional): The file path for the stub file. If None, a default path may be used. 
                Defaults to None.

        Returns:
            list: A list of detected keypoints for each input frame.
        """
        court_keypoints = read_stub(read_from_stub, stub_path, cache_key=cache_key)
        if court_keypoints is not None:
            if len(court_keypoints) == len(frames):
                return court_keypoints
        
        batch_size=20
        court_keypoints = []
        total_batches = (len(frames) + batch_size - 1) // batch_size
        for i in range(0,len(frames),batch_size):
            batch_num = (i // batch_size) + 1
            if batch_num % 10 == 0 or batch_num == total_batches:
                print(f"  Processing keypoint batch {batch_num}/{total_batches}...")
            try:
                detections_batch = self.model.predict(frames[i:i+batch_size], conf=0.5, verbose=False, device=self.device)
                for detection in detections_batch:
                    # Handle both pose and detection models
                    if hasattr(detection, 'keypoints') and detection.keypoints is not None:
                        court_keypoints.append(detection.keypoints)
                    else:
                        # If no keypoints, append None or empty
                        court_keypoints.append(None)
            except Exception as e:
                print(f"  Error in batch {batch_num}: {e}")
                # Append None for failed frames
                for _ in range(min(batch_size, len(frames) - i)):
                    court_keypoints.append(None)

        save_stub(stub_path, court_keypoints, cache_key=cache_key)
        
        return court_keypoints
