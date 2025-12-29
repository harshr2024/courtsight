# Live Basketball Score Detection

This system extends the basketball analysis program to work with live camera feeds, providing real-time score detection while allowing for post-processing of comprehensive analytics.

## Features

### Real-time Score Detection
- **Live Camera Feed**: Captures video from any connected camera
- **Ball Tracking**: Uses YOLO model to detect and track basketball movement
- **Hoop Detection**: Automatically detects basketball hoops using computer vision
- **Score Counting**: Counts points in real-time with configurable parameters
- **Visual Overlay**: Displays current score, ball velocity, and detections on screen

### Video Recording
- **Live Recording**: Option to record the live feed with score overlays
- **Analysis Recording**: Record frames for later comprehensive analysis
- **Post-processing**: Run full analysis (player tracking, passes, etc.) on recorded videos

## Installation

1. Ensure you have the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure the ball detection model is available:
```bash
# The model should be at models/ball_detector_model.pt
```

## Usage

### Basic Live Detection

Start live score detection with default settings:
```bash
python live_main.py
```

### Advanced Configuration

```bash
python live_main.py \
    --camera 0 \
    --model models/ball_detector_model.pt \
    --cooldown 3.0 \
    --distance-threshold 50 \
    --min-velocity 5.0 \
    --save-video output_videos/live_recording.mp4 \
    --record-analysis
```

### Parameters

- `--camera`: Camera index (default: 0)
- `--model`: Path to ball detection model
- `--cooldown`: Score detection cooldown in seconds (default: 3.0)
- `--distance-threshold`: Ball-hoop distance threshold for score detection (default: 50)
- `--min-velocity`: Minimum ball velocity for score detection (default: 5.0)
- `--save-video`: Path to save recorded video (optional)
- `--record-analysis`: Record frames for later analysis

### Post-processing Analysis

After recording a video, run the full analysis:

```bash
python analyze_recorded_video.py output_videos/live_recording.mp4 \
    --output_video output_videos/analyzed_video.mp4 \
    --stub_path stubs/
```

## How It Works

### 1. Live Score Detection
The system works by:
1. **Camera Capture**: Continuously captures frames from the camera
2. **Ball Detection**: Uses YOLO model to detect basketball in each frame
3. **Hoop Detection**: Detects basketball hoops using circle detection
4. **Score Logic**: Determines if a score occurred based on:
   - Ball proximity to hoops
   - Ball velocity (must be above threshold)
   - Time cooldown (prevents multiple detections)
5. **Visual Display**: Shows live score, ball tracking, and hoop detection

### 2. Score Detection Algorithm
```python
# Simplified score detection logic
if (ball_near_hoop and 
    ball_velocity > min_velocity and 
    time_since_last_score > cooldown):
    increment_score()
```

### 3. Post-processing Pipeline
Recorded videos can be processed with the full analysis pipeline:
- Player detection and tracking
- Team assignment
- Pass and interception detection
- Speed and distance calculations
- Tactical view generation

## Configuration

### Score Detection Parameters

Adjust these parameters based on your setup:

```python
# In live_score_detector.py
self.score_cooldown = 3.0  # seconds between score detections
self.ball_hoop_distance_threshold = 50  # pixels
self.min_ball_velocity = 5.0  # minimum ball movement
```

### Camera Setup

For optimal performance:
- Use a camera with 720p or higher resolution
- Ensure good lighting conditions
- Position camera to capture both hoops clearly
- Minimize camera movement during game

## Troubleshooting

### Common Issues

1. **Camera not found**
   ```
   Error: Could not open camera at index 0
   ```
   - Try different camera indices: `--camera 1`, `--camera 2`
   - Check camera permissions
   - Ensure camera is not being used by another application

2. **Model not found**
   ```
   Error: Model file not found at models/ball_detector_model.pt
   ```
   - Ensure the ball detection model is available
   - Check the model path in arguments

3. **Poor score detection**
   - Adjust `--distance-threshold` (increase for more sensitive detection)
   - Adjust `--min-velocity` (decrease for slower ball movement)
   - Adjust `--cooldown` (decrease for faster scoring games)

4. **Performance issues**
   - Reduce camera resolution
   - Use a more powerful GPU
   - Close other applications using the camera

### Performance Optimization

For better real-time performance:
- Use GPU acceleration if available
- Reduce frame processing resolution
- Adjust detection confidence thresholds
- Use SSD storage for video recording

## File Structure

```
basketball_analysis/
├── live_score_detector.py      # Main live detection class
├── live_main.py               # Command-line interface
├── analyze_recorded_video.py  # Post-processing analysis
├── main.py                    # Original analysis pipeline
├── models/                    # Detection models
├── output_videos/             # Recorded and analyzed videos
└── stubs/                     # Cached detection results
```

## Integration with Existing System

The live detection system is designed to work alongside the existing analysis pipeline:

1. **Live Detection**: `live_score_detector.py` handles real-time score counting
2. **Video Recording**: Captures video for later analysis
3. **Post-processing**: `analyze_recorded_video.py` runs full analysis on recorded videos
4. **Original Pipeline**: `main.py` remains unchanged for pre-recorded video analysis

## Future Enhancements

Potential improvements for the live detection system:

1. **Team Detection**: Automatic team identification and assignment
2. **Advanced Hoop Detection**: Trained model for more accurate hoop detection
3. **Score Validation**: Additional validation to reduce false positives
4. **Network Streaming**: Stream live detection to remote displays
5. **Database Integration**: Store scores and statistics in database
6. **Mobile App**: Companion app for score display and control

## Contributing

To contribute to the live detection system:

1. Test with different camera setups
2. Improve hoop detection algorithms
3. Add team detection capabilities
4. Optimize performance for different hardware
5. Add support for multiple camera angles

## License

This project extends the original basketball analysis system with live detection capabilities. 