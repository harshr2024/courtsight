# CourtSight

CourtSight is a deliberately narrow basketball computer-vision demo:

```text
video upload -> player detections and temporary tracks
             -> observed ball detections
             -> court keypoints
             -> correctly timed annotated video
```

The supported demo does **not** infer player names, teams, possession, passes,
speed, shots, or score. Numeric player IDs are temporary tracker IDs and may
change after occlusion. Missing ball detections are left missing rather than
filled with invented positions. Detection accuracy has not been benchmarked;
the overlays are model outputs, not ground truth or an accuracy claim.

## Required manual assets

Model weights and videos are intentionally ignored by Git because of their size.
Place these exact model files in `basketball_analysis/models/`:

- `player_detector.pt` — 172,649,923 bytes
  SHA-256 `ff16fcbeb6c0500d687a2b070c78c6644a809376397ef3354b84b5fec6096a18`
- `ball_detector_model.pt` — 172,669,123 bytes
  SHA-256 `d29455e42dc9b4ec9bf2cf12b352b1c2ef517ec99bc6a6d79376c61b70ed74d4`
- `court_keypoint_detector.pt` — 139,472,097 bytes
  SHA-256 `a5f8ecd34bfade70e652403ade0dec25d6a11e296ef626ba725bed7a37ec1786`

The original download locations are:

- [player detector](https://drive.google.com/file/d/1fVBLZtPy9Yu6Tf186oS4siotkioHBLHy/view?usp=sharing)
- [ball detector](https://drive.google.com/file/d/1KejdrcEnto2AKjdgdo1U1syr5gODp6EL/view?usp=sharing)
- [court-keypoint detector](https://drive.google.com/file/d/1nGoG-pUkSg4bWAUIeQ8aN6n7O1fOkXU0/view?usp=sharing)

### Sample-video status

The local development reference clip is intentionally **not** committed. Its
source and redistribution permission could not be verified from repository
history, so it must not be copied into a release. If you already have the same
clip, its expected location and fingerprint are:

`basketball_analysis/input_videos/video_1.mp4`

- 4,450,890 bytes
- SHA-256 `4b725473dfb15f27795d03683b6b35edd00472ffb86506799bd6c3d7f6415b13`

There is currently no verified public source for those exact bytes. This is the
remaining blocker to reproducing the recorded reference result exactly.

For an accessible replacement, use Pexels' 12-second, 3840×2160, 24 FPS
[Intense Indoor Basketball Game Footage](https://www.pexels.com/video/intense-indoor-basketball-game-footage-31955038/).
Pexels marks the clip as free to use under its
[content license](https://www.pexels.com/license/). Because that license limits
standalone redistribution, this repository links to the source instead of
bundling the file.

1. Open the Pexels clip page and select **Free download**, or download the
   same asset directly from the repository root:

   ```bash
   curl -L --fail \
     https://www.pexels.com/download/video/31955038/ \
     -o basketball_analysis/input_videos/pexels-basketball-31955038.mp4
   ```

2. Verify the downloaded MP4. The rendition tested on September 29, 2026 was
   49,437,624 bytes with SHA-256
   `e9fe2cebfa994a52ca922a258cb2330f6038d0d633122a6ed4e23074efba4a44`.
3. Build and start the UI using the commands below, open
   `http://localhost:5001`, and upload that file; or run:

   ```bash
   cd basketball_analysis
   python main.py input_videos/pexels-basketball-31955038.mp4 \
     --output_video output_videos/pexels-demo.mp4 \
     --frame_skip 2 \
     --target_width 960 \
     --device cpu
   ```

The Pexels clip is a setup example, not the unavailable clip used for the older
development reference measurement later in this README. Its detections have not
been benchmarked.

A final CPU smoke test used the first 2.000 seconds of that download, resized to
960×540 before upload (48 input frames at 24 FPS). The UI sampled every other
frame and produced 24 frames at 12 FPS, 960×540, and 2.000 seconds. With no
matching cache present, upload through completed processing took **45.87
seconds**. A subsequent command-line run with the same input and settings reused
the generated detections and took **13.60 seconds**. These timings verify the
pipeline and cache behavior on one machine; they are not detection-accuracy or
general performance benchmarks.

Verify installed assets:

```bash
cd basketball_analysis
python test_models.py
shasum -a 256 models/*.pt
# Only if you already have the unavailable local reference clip:
shasum -a 256 input_videos/video_1.mp4
```

## Supported setup

Use Python 3.11 and Node.js 20.19 or newer.

```bash
python3.11 -m venv basketball_analysis/.venv
source basketball_analysis/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r basketball_analysis/requirements.txt

cd frontend
npm ci
npm run build
cd ../basketball_analysis
python web_app.py
```

Open `http://localhost:5001`, choose a short video, and select **Create
annotated video**. Flask serves the built React UI and the API from the same
process, so there is only one user-facing application.

The UI samples every other frame at up to 960 pixels wide on CPU, and derives an
output FPS that preserves the source duration. This keeps the demo practical
without pretending skipped frames were analyzed. Set
`COURTSIGHT_DEVICE=mps` or `COURTSIGHT_DEVICE=cuda` before starting the server
only when that Torch device is available.

### Measured CPU reference

On the development machine, fresh CPU inference of the unavailable local
reference clip took approximately **2 minutes**. The input was 3.900 seconds,
1280×720, 30 FPS, and 117 frames. With the UI settings (`frame_skip=2`,
`target_width=960`), CourtSight produced 59 frames at approximately 15.128 FPS,
960×540, with a measured output duration of 3.900 seconds.

That figure is a single observed processing time, not a performance guarantee or
benchmark. A repeat with a warm detection cache took approximately **13.5
seconds** on the same machine, including process startup, model loading,
annotation, and video writing. The cached run reused detections for the exact
video/model/settings fingerprint and therefore did not measure inference. Use
`--no_cache` when measuring a fresh run.

## Command-line run

```bash
cd basketball_analysis
python main.py input_videos/video_1.mp4 \
  --output_video output_videos/reference-demo.mp4 \
  --frame_skip 2 \
  --target_width 960 \
  --device cpu
```

When frames are skipped, CourtSight derives a constant output FPS that preserves
the represented input segment's duration, including clips whose frame count is
not divisible by the skip factor. Detection caches are keyed by the exact video
bytes, model bytes, and processing settings. Use `--no_cache` to force fresh
inference.

## Focused checks

```bash
cd basketball_analysis
python -m unittest discover -s tests -v
python test_models.py

cd ../frontend
npm run lint
npm run build
```

The unit checks cover cross-video cache isolation, frame preservation, output
FPS after frame skipping, and the upload API contract. `test_models.py` is a
local asset smoke test and requires the three ignored weight files.

## Repository note

Older experimental modules for team assignment, possession, pass detection,
speed, tactical statistics, and live scoring remain in the repository as
unsupported research code. The canonical `main.py`, web API, and React UI do
not import or execute them.
