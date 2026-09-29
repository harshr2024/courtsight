# CourtSight analysis service

The supported service performs only player tracking, observed ball detection,
court-keypoint detection, and annotated-video rendering. See the repository
root [README](../README.md) for exact model files, checksums, setup, tests, and
manual sample-video requirements.

Run the complete single-server demo after building the frontend:

```bash
python web_app.py
```

Run the same pipeline without the UI:

```bash
python main.py input_videos/video_1.mp4 --output_video output_videos/demo.mp4
```
