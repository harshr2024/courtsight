"""Single-server web UI for the supported CourtSight demo."""

import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid

import cv2
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = (BASE_DIR.parent / "frontend" / "dist").resolve()
OUTPUT_DIR = (BASE_DIR / "output_videos").resolve()
UPLOAD_DIR = (OUTPUT_DIR / "uploads").resolve()
CACHE_DIR = (BASE_DIR / "stubs").resolve()
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIST / "assets"),
    static_url_path="/assets",
)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024
CORS(app, resources={r"/api/*": {"origins": "*"}})

analysis_jobs = {}
jobs_lock = threading.Lock()


def set_job(job_id, **updates):
    with jobs_lock:
        analysis_jobs.setdefault(job_id, {}).update(updates)


def output_metadata(path):
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        return {}
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    capture.release()
    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration_seconds": frame_count / fps if fps > 0 else None,
        "width": width,
        "height": height,
    }


def run_analysis(job_id, input_path, output_path, frame_skip, target_width):
    command = [
        sys.executable,
        str(BASE_DIR / "main.py"),
        str(input_path),
        "--output_video",
        str(output_path),
        "--cache_dir",
        str(CACHE_DIR),
        "--frame_skip",
        str(frame_skip),
        "--target_width",
        str(target_width),
        "--device",
        os.environ.get("COURTSIGHT_DEVICE", "cpu"),
    ]
    set_job(job_id, status="processing", message="Loading video and models")
    output_lines = []
    try:
        process_environment = os.environ.copy()
        process_environment["PYTHONUNBUFFERED"] = "1"
        process = subprocess.Popen(
            command,
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=process_environment,
        )
        for raw_line in process.stdout:
            line = raw_line.strip()
            if not line:
                continue
            output_lines.append(line)
            print(f"[{job_id}] {line}")
            if "STEP 1/3" in line:
                set_job(job_id, message="Detecting and tracking players")
            elif "STEP 2/3" in line:
                set_job(job_id, message="Detecting basketballs")
            elif "STEP 3/3" in line:
                set_job(job_id, message="Detecting court keypoints")
            elif line.startswith("Complete:"):
                set_job(job_id, message="Finalizing annotated video")

        return_code = process.wait()
        if return_code != 0:
            error = output_lines[-1] if output_lines else "Analysis process failed"
            set_job(job_id, status="failed", message="Analysis failed", error=error)
            return

        metadata = output_metadata(output_path)
        set_job(
            job_id,
            status="completed",
            message="Analysis complete",
            output_path=str(output_path),
            video_url=f"/video/{output_path.name}",
            metadata=metadata,
            completed_at=time.time(),
        )
    except Exception as exc:
        set_job(job_id, status="failed", message="Analysis failed", error=str(exc))


@app.get("/")
def index():
    index_path = FRONTEND_DIST / "index.html"
    if not index_path.is_file():
        return jsonify(
            {
                "status": "frontend_not_built",
                "message": "Run `npm ci && npm run build` in frontend, then restart CourtSight.",
            }
        ), 503
    return send_from_directory(str(FRONTEND_DIST), "index.html")


@app.get("/api/test")
def test():
    required_models = [
        BASE_DIR / "models" / "player_detector.pt",
        BASE_DIR / "models" / "ball_detector_model.pt",
        BASE_DIR / "models" / "court_keypoint_detector.pt",
    ]
    return jsonify(
        {
            "status": "ok",
            "models_ready": all(path.is_file() for path in required_models),
            "frontend_ready": (FRONTEND_DIST / "index.html").is_file(),
        }
    )


@app.post("/api/analyze")
def analyze_video():
    upload = request.files.get("video")
    if upload is None or not upload.filename:
        return jsonify({"status": "error", "message": "Choose a video file to analyze."}), 400

    extension = Path(secure_filename(upload.filename)).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify(
            {
                "status": "error",
                "message": f"Unsupported video type. Use one of: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            }
        ), 400

    try:
        frame_skip = int(request.form.get("frame_skip", "1"))
        target_width = int(request.form.get("target_width", "1280"))
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid processing settings."}), 400
    if frame_skip not in {1, 2, 4} or target_width not in {720, 960, 1280}:
        return jsonify({"status": "error", "message": "Unsupported processing settings."}), 400

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    job_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{job_id}{extension}"
    output_path = OUTPUT_DIR / f"annotated-{job_id}.mp4"
    upload.save(input_path)

    set_job(
        job_id,
        status="queued",
        message="Upload complete; analysis queued",
        original_filename=secure_filename(upload.filename),
        started_at=time.time(),
    )
    thread = threading.Thread(
        target=run_analysis,
        args=(job_id, input_path, output_path, frame_skip, target_width),
        daemon=True,
    )
    thread.start()
    return jsonify({"status": "success", "job_id": job_id}), 202


@app.get("/api/analysis_status/<job_id>")
def get_analysis_status(job_id):
    with jobs_lock:
        job = analysis_jobs.get(job_id)
        if job is None:
            return jsonify({"status": "error", "message": "Job not found"}), 404
        return jsonify(dict(job))


@app.get("/video/<path:filename>")
def serve_video(filename):
    safe_name = secure_filename(filename)
    if safe_name != filename:
        return jsonify({"status": "error", "message": "Invalid video path"}), 403
    return send_from_directory(str(OUTPUT_DIR), safe_name, mimetype="video/mp4")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    port = int(os.environ.get("PORT", "5001"))
    print(f"CourtSight demo: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
