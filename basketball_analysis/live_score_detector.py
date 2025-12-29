import cv2
import numpy as np
import time
from ultralytics import YOLO
import supervision as sv
from collections import deque
import threading
import queue
import os

class LiveScoreDetector:
    """
    Real-time basketball score detection from live camera feed.
    
    This class captures live video, detects basketball hoops, tracks ball movement,
    and counts scores in real-time while allowing for post-processing of other analytics.
    """
    
    def __init__(self, camera_index=0, model_path="models/ball_detector_model.pt"):
        """
        Initialize the live score detector.
        
        Args:
            camera_index (int): Index of the camera to use (default: 0)
            model_path (str): Path to the ball detection model
        """
        self.camera_index = camera_index
        self.cap = None
        self.is_running = False
        self.score_team1 = 0
        self.score_team2 = 0
        self.last_score_time = 0
        self.score_cooldown = 3.0  # seconds between score detections
        
        # Ball tracking
        self.ball_model = YOLO(model_path)
        self.ball_tracker = sv.ByteTrack()
        self.ball_positions = deque(maxlen=30)  # Track last 30 ball positions
        
        # Hoop detection
        self.hoop_detector = cv2.createHOGDescriptor()
        self.hoop_positions = []
        
        # Threading for real-time processing
        self.frame_queue = queue.Queue(maxsize=10)
        self.result_queue = queue.Queue(maxsize=10)
        
        # Score detection parameters
        self.hoop_threshold = 0.7
        self.ball_hoop_distance_threshold = 50
        self.min_ball_velocity = 5.0
        
        # Video recording
        self.video_writer = None
        self.record_video = False
        self.video_path = None
        
        # Analysis recording
        self.analysis_frames = []
        self.record_analysis = False
        
    def start_camera(self):
        """Start the camera capture."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open camera at index {self.camera_index}")
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
    def setup_video_recording(self, video_path):
        """Setup video recording."""
        if video_path:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(video_path), exist_ok=True)
            
            self.video_writer = cv2.VideoWriter(video_path, fourcc, fps, (frame_width, frame_height))
            self.record_video = True
            self.video_path = video_path
            print(f"Recording video to: {video_path}")
    
    def detect_hoops(self, frame):
        """
        Detect basketball hoops in the frame.
        
        Args:
            frame: Input frame
            
        Returns:
            list: List of hoop bounding boxes
        """
        # Convert to grayscale for hoop detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Use HOG detector for hoop detection (simplified approach)
        # In a real implementation, you'd want a trained model for hoop detection
        hoops = []
        
        # Simple hoop detection using circle detection
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
            param1=50, param2=30, minRadius=20, maxRadius=100
        )
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for circle in circles[0, :]:
                x, y, r = circle
                hoops.append((x-r, y-r, x+r, y+r))  # Convert to bbox format
                
        return hoops
    
    def detect_ball(self, frame):
        """
        Detect basketball in the frame.
        
        Args:
            frame: Input frame
            
        Returns:
            list: List of ball detections
        """     
        results = self.ball_model(frame, conf=0.5, verbose=False)
        detections = sv.Detections.from_ultralytics(results[0])
        
        if len(detections) > 0:
            # Track ball using ByteTrack
            detections = self.ball_tracker.update_with_detections(detections)
            
            # Get ball positions
            ball_positions = []
            for xyxy, confidence, class_id, tracker_id in detections:
                if class_id == 0:  # Assuming ball is class 0
                    center_x = (xyxy[0] + xyxy[2]) / 2
                    center_y = (xyxy[1] + xyxy[3]) / 2
                    ball_positions.append((center_x, center_y))
                    
            return ball_positions
        return []
    
    def calculate_ball_velocity(self):
        """
        Calculate ball velocity from recent positions.
        
        Returns:
            float: Ball velocity magnitude
        """
        if len(self.ball_positions) < 2:
            return 0.0
            
        positions = list(self.ball_positions)
        velocities = []
        
        for i in range(1, len(positions)):
            dx = positions[i][0] - positions[i-1][0]
            dy = positions[i][1] - positions[i-1][1]
            velocity = np.sqrt(dx*dx + dy*dy)
            velocities.append(velocity)
            
        return np.mean(velocities) if velocities else 0.0
    
    def detect_score(self, ball_positions, hoop_positions):
        """
        Detect if a score occurred based on ball and hoop positions.
        
        Args:
            ball_positions: List of ball positions
            hoop_positions: List of hoop positions
            
        Returns:
            bool: True if score detected
        """
        if not ball_positions or not hoop_positions:
            return False
            
        current_time = time.time()
        if current_time - self.last_score_time < self.score_cooldown:
            return False
            
        ball_velocity = self.calculate_ball_velocity()
        if ball_velocity < self.min_ball_velocity:
            return False
            
        # Check if ball is near any hoop
        for ball_pos in ball_positions:
            for hoop_bbox in hoop_positions:
                hoop_center_x = (hoop_bbox[0] + hoop_bbox[2]) / 2
                hoop_center_y = (hoop_bbox[1] + hoop_bbox[3]) / 2
                
                distance = np.sqrt(
                    (ball_pos[0] - hoop_center_x)**2 + 
                    (ball_pos[1] - hoop_center_y)**2
                )
                
                if distance < self.ball_hoop_distance_threshold:
                    self.last_score_time = current_time
                    return True
                    
        return False
    
    def process_frame(self, frame):
        """
        Process a single frame for score detection.
        
        Args:
            frame: Input frame
            
        Returns:
            tuple: (processed_frame, score_detected)
        """
        # Detect hoops and ball
        hoops = self.detect_hoops(frame)
        ball_positions = self.detect_ball(frame)
        
        # Update ball position history
        if ball_positions:
            self.ball_positions.extend(ball_positions)
        
        # Check for score
        score_detected = self.detect_score(ball_positions, hoops)
        if score_detected:
            # Determine which team scored (simplified - you'd need team detection)
            # For now, alternate between teams
            if self.score_team1 <= self.score_team2:
                self.score_team1 += 1
            else:
                self.score_team2 += 1
        
        # Draw detections on frame
        processed_frame = frame.copy()
        
        # Draw hoops
        for hoop_bbox in hoops:
            cv2.rectangle(processed_frame, 
                         (int(hoop_bbox[0]), int(hoop_bbox[1])),
                         (int(hoop_bbox[2]), int(hoop_bbox[3])),
                         (0, 255, 0), 2)
            cv2.putText(processed_frame, "Hoop", 
                       (int(hoop_bbox[0]), int(hoop_bbox[1]) - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw ball positions
        for ball_pos in ball_positions:
            cv2.circle(processed_frame, 
                      (int(ball_pos[0]), int(ball_pos[1])), 10, (255, 0, 0), -1)
        
        # Draw score
        cv2.putText(processed_frame, f"Team 1: {self.score_team1}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(processed_frame, f"Team 2: {self.score_team2}", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Draw velocity
        velocity = self.calculate_ball_velocity()
        cv2.putText(processed_frame, f"Ball Velocity: {velocity:.1f}", 
                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(processed_frame, f"Time: {timestamp}", 
                   (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return processed_frame, score_detected
    
    def frame_processor_thread(self):
        """Thread for processing frames in background."""
        while self.is_running:
            try:
                frame = self.frame_queue.get(timeout=0.1)
                processed_frame, score_detected = self.process_frame(frame)
                self.result_queue.put((processed_frame, score_detected))
            except queue.Empty:
                continue
    
    def start_live_detection(self):
        """Start live score detection."""
        self.start_camera()
        self.is_running = True
        
        # Start processing thread
        processor_thread = threading.Thread(target=self.frame_processor_thread)
        processor_thread.daemon = True
        processor_thread.start()
        
        print("Live score detection started. Press 'q' to quit.")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame from camera")
                    break
                
                # Add frame to processing queue
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
                
                # Get processed result
                try:
                    processed_frame, score_detected = self.result_queue.get_nowait()
                    
                    # Record video if enabled
                    if self.record_video and self.video_writer:
                        self.video_writer.write(processed_frame)
                    
                    # Store frame for analysis if enabled
                    if self.record_analysis:
                        self.analysis_frames.append(processed_frame.copy())
                    
                    # Display the frame
                    cv2.imshow('Live Basketball Score Detection', processed_frame)
                    
                    if score_detected:
                        print(f"SCORE! Team 1: {self.score_team1}, Team 2: {self.score_team2}")
                        
                except queue.Empty:
                    # If no processed frame available, show original
                    cv2.imshow('Live Basketball Score Detection', frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("Stopping live detection...")
        finally:
            self.stop_live_detection()
    
    def stop_live_detection(self):
        """Stop live score detection."""
        self.is_running = False
        if self.cap:
            self.cap.release()
        if self.video_writer:
            self.video_writer.release()
        cv2.destroyAllWindows()
        
        # Save analysis frames if recorded
        if self.record_analysis and self.analysis_frames:
            self.save_analysis_video()
    
    def save_analysis_video(self):
        """Save recorded frames for later analysis."""
        if not self.analysis_frames:
            return
            
        analysis_path = "output_videos/live_analysis_video.mp4"
        os.makedirs(os.path.dirname(analysis_path), exist_ok=True)
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        height, width = self.analysis_frames[0].shape[:2]
        fps = 30
        
        writer = cv2.VideoWriter(analysis_path, fourcc, fps, (width, height))
        
        for frame in self.analysis_frames:
            writer.write(frame)
        
        writer.release()
        print(f"Analysis video saved to: {analysis_path}")
    
    def get_current_score(self):
        """Get current score."""
        return {
            'team1': self.score_team1,
            'team2': self.score_team2
        }
    
    def reset_score(self):
        """Reset the score."""
        self.score_team1 = 0
        self.score_team2 = 0 