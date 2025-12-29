# Basketball Analysis Web Application

A web-based interface for real-time basketball score detection with post-processing analytics.

## Features

- **Live Video Streaming**: Stream live camera feed directly in your web browser
- **Real-time Score Detection**: Only score detection runs in real-time for optimal performance
- **Automatic Video Recording**: Videos are automatically recorded when detection is started
- **Post-Processing Analysis**: Process recorded videos for passes, interceptions, and other analytics after recording
- **Modern Web Interface**: Beautiful, responsive web interface accessible from any device

## Architecture

The system is designed with a clear separation of concerns:

1. **Live Processing**: Only score detection runs in real-time
2. **Video Recording**: All video is automatically recorded for later analysis
3. **Post-Processing**: Passes, interceptions, player tracking, and other analytics are processed after recording

This architecture ensures:
- Optimal real-time performance (only lightweight score detection)
- Comprehensive analysis (full pipeline on recorded video)
- No data loss (everything is recorded)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have the required models:
   - `models/ball_detector_model.pt`
   - `models/player_detector.pt`
   - `models/court_keypoint_detector.pt`

## Usage

### Starting the Web Application

1. Navigate to the basketball_analysis directory:
```bash
cd basketball_analysis
```

2. Start the web server:
```bash
python web_app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

### Using the Web Interface

1. **Start Detection**:
   - Click the "Start Detection" button
   - The camera will start capturing and processing frames
   - Video recording begins automatically
   - Real-time score detection starts

2. **Monitor Score**:
   - Watch the live video feed
   - Score is displayed in real-time on the video overlay
   - Score updates automatically every 500ms

3. **Stop Detection**:
   - Click the "Stop Detection" button when done
   - Video recording stops
   - The recorded video path is saved

4. **Post-Processing Analysis**:
   - After stopping detection, click "Analyze Video"
   - The system will process the recorded video for:
     - Player tracking
     - Pass detection
     - Interception detection
     - Speed and distance calculations
     - Tactical view generation
   - Analysis status is displayed in real-time
   - When complete, the analyzed video path is shown

5. **Reset Score**:
   - Click "Reset Score" to reset the score counter to 0-0
   - Only available while detection is running

## API Endpoints

The web application provides several REST API endpoints:

### `GET /`
Main web interface page.

### `GET /video_feed`
Live video stream (MJPEG format).

### `GET /api/score`
Get current score.
```json
{
  "team1": 5,
  "team2": 3
}
```

### `POST /api/start`
Start live score detection.
```json
{
  "camera": 0,
  "model": "models/ball_detector_model.pt"
}
```

### `POST /api/stop`
Stop live score detection.
Returns final score and recording path.

### `POST /api/analyze`
Trigger post-processing analysis.
```json
{
  "video_path": "output_videos/live_recording_1234567890.mp4"
}
```
Returns job ID for tracking analysis progress.

### `GET /api/analysis_status/<job_id>`
Get status of analysis job.
```json
{
  "status": "processing|completed|failed",
  "output_path": "output_videos/analyzed_1234567890.mp4",
  "error": null
}
```

### `POST /api/reset_score`
Reset the score counter.

## File Structure

```
basketball_analysis/
├── web_app.py              # Flask web application
├── templates/
│   └── index.html          # Web interface template
├── static/
│   └── style.css           # Web interface styling
├── live_score_detector.py  # Live score detection class
├── analyze_recorded_video.py  # Post-processing analysis
├── output_videos/          # Recorded and analyzed videos
└── stubs/                  # Cached detection results
```

## Workflow

1. **Live Detection Phase**:
   - Start detection via web interface
   - Camera captures frames
   - Score detection runs in real-time
   - Video is recorded to `output_videos/live_recording_<timestamp>.mp4`
   - Score updates are displayed in real-time

2. **Post-Processing Phase**:
   - Stop detection
   - Click "Analyze Video" button
   - System processes recorded video:
     - Player detection and tracking
     - Ball tracking
     - Court keypoint detection
     - Team assignment
     - Ball acquisition detection
     - Pass and interception detection
     - Speed and distance calculations
     - Tactical view generation
   - Analyzed video saved to `output_videos/analyzed_<timestamp>.mp4`

## Configuration

### Camera Settings

Default camera index is 0. To use a different camera, modify the camera index in the start request or update the default in `web_app.py`.

### Score Detection Parameters

Score detection parameters can be adjusted in `live_score_detector.py`:
- `score_cooldown`: Time between score detections (default: 3.0 seconds)
- `ball_hoop_distance_threshold`: Distance threshold for score detection (default: 50 pixels)
- `min_ball_velocity`: Minimum ball velocity for score detection (default: 5.0)

### Video Recording

Videos are automatically recorded when detection starts. Recordings are saved to `output_videos/` with timestamps.

## Troubleshooting

### Camera Not Found
- Check camera permissions
- Try different camera indices (0, 1, 2, etc.)
- Ensure camera is not being used by another application

### Video Not Streaming
- Check that detection is started
- Verify camera is working
- Check browser console for errors

### Analysis Fails
- Ensure recorded video exists
- Check that all required models are available
- Verify sufficient disk space for output videos
- Check analysis job status via API

### Performance Issues
- Reduce camera resolution in `live_score_detector.py`
- Use GPU acceleration if available
- Close other applications using the camera

## Network Access

By default, the web application runs on `0.0.0.0:5000`, making it accessible from other devices on your network:

- Local: `http://localhost:5000`
- Network: `http://<your-ip>:5000`

## Security Note

This application is designed for local network use. For production deployment, consider:
- Adding authentication
- Using HTTPS
- Implementing rate limiting
- Adding input validation

## Future Enhancements

Potential improvements:
- Multiple camera support
- Real-time team identification
- Database integration for score history
- Mobile app companion
- Cloud storage integration
- Advanced analytics dashboard

## License

This project extends the original basketball analysis system with web interface capabilities.


