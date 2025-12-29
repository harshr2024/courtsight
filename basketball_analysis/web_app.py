#!/usr/bin/env python3
"""
Courtsight - Basketball Analysis Web Application

This Flask web application provides:
- Live video streaming with real-time score detection
- API endpoints for score data
- Post-processing analysis trigger for passes and other analytics
"""

import os
import cv2
import numpy as np
import threading
import time
import json
import re
from flask import Flask, render_template, Response, jsonify, request
from live_score_detector import LiveScoreDetector
import subprocess
import uuid
try:
    import yt_dlp
except ImportError:
    yt_dlp = None

app = Flask(__name__)

# Global detector instance
detector = None
detector_lock = threading.Lock()
recording_path = None
analysis_jobs = {}  # Track analysis jobs

# Store latest processed frame for streaming
latest_frame = None
latest_frame_lock = threading.Lock()

def frame_processing_loop():
    """Background thread to continuously process frames."""
    global detector, latest_frame
    
    while True:
        # Check if detector exists and is running (quick check)
        with detector_lock:
            if detector is None or not detector.is_running:
                time.sleep(0.1)
                continue
            # Get reference to detector and cap (release lock quickly)
            current_detector = detector
            current_cap = current_detector.cap
            record_video = current_detector.record_video
            video_writer = current_detector.video_writer
        
        # Process frame outside of lock
        try:
            ret, frame = current_cap.read()
            if not ret:
                time.sleep(0.1)
                continue
            
            # Process frame for score detection
            processed_frame, _ = current_detector.process_frame(frame)
            
            # Record video if enabled
            if record_video and video_writer:
                video_writer.write(processed_frame)
            
            # Store latest frame for streaming
            with latest_frame_lock:
                latest_frame = processed_frame.copy()
                
        except Exception as e:
            print(f"Error processing frame: {e}")
            time.sleep(0.1)

def generate_frames():
    """Generate video frames for streaming."""
    global latest_frame
    
    while True:
        with latest_frame_lock:
            if latest_frame is not None:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', latest_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.033)  # ~30 FPS

@app.route('/')
def index():
    """Main page with live video stream."""
    return render_template('index.html')

@app.route('/api/test')
def test():
    """Test endpoint to verify server is working."""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

# Video feed route removed - using YouTube URLs instead

@app.route('/api/score')
def get_score():
    """Get current score."""
    global detector
    with detector_lock:
        if detector is None:
            return jsonify({'team1': 0, 'team2': 0})
        score = detector.get_current_score()
        return jsonify(score)

@app.route('/api/start', methods=['POST'])
def start_detection():
    """Start live score detection."""
    global detector, recording_path
    
    data = request.get_json() or {}
    camera_index = data.get('camera', 0)
    model_path = data.get('model', 'models/ball_detector_model.pt')
    
    with detector_lock:
        if detector is not None and detector.is_running:
            return jsonify({'status': 'error', 'message': 'Detection already running'}), 400
        
        try:
            # Generate unique recording path
            timestamp = int(time.time())
            recording_path = f"output_videos/live_recording_{timestamp}.mp4"
            os.makedirs(os.path.dirname(recording_path), exist_ok=True)
            
            # Initialize detector
            detector = LiveScoreDetector(camera_index=camera_index, model_path=model_path)
            detector.start_camera()
            detector.is_running = True
            
            # Setup video recording
            detector.setup_video_recording(recording_path)
            
            # Start frame processing thread for web streaming
            processing_thread = threading.Thread(target=frame_processing_loop)
            processing_thread.daemon = True
            processing_thread.start()
            
            return jsonify({
                'status': 'success',
                'message': 'Detection started',
                'recording_path': recording_path
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_detection():
    """Stop live score detection."""
    global detector, recording_path
    
    with detector_lock:
        if detector is None:
            return jsonify({'status': 'error', 'message': 'No detection running'}), 400
        
        try:
            detector.is_running = False
            final_score = detector.get_current_score()
            stopped_recording = recording_path
            
            # Release resources
            if detector.video_writer:
                detector.video_writer.release()
                detector.video_writer = None
            if detector.cap:
                detector.cap.release()
            
            recording_path = None
            
            # Clear latest frame
            global latest_frame
            with latest_frame_lock:
                latest_frame = None
            
            return jsonify({
                'status': 'success',
                'message': 'Detection stopped',
                'final_score': final_score,
                'recording_path': stopped_recording
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            detector = None

def is_youtube_url(url):
    """Check if URL is a valid YouTube URL."""
    youtube_pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
    return bool(re.match(youtube_pattern, url))

def download_youtube_video(url, output_path):
    """Download YouTube video using yt-dlp."""
    if yt_dlp is None:
        raise ImportError("yt-dlp is not installed. Please install it with: pip install yt-dlp")
    
    # Remove extension from output_path as yt-dlp will add it
    base_path = output_path.rsplit('.', 1)[0] if '.' in output_path else output_path
    
    ydl_opts = {
        'format': 'best[height<=720]/best',  # Download best quality up to 720p, fallback to best
        'outtmpl': base_path + '.%(ext)s',
        'quiet': False,
        'no_warnings': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # Find the actual downloaded file
    for ext in ['.mp4', '.webm', '.mkv', '.m4a']:
        file_path = base_path + ext
        if os.path.exists(file_path):
            return file_path
    
    # If no file found, return the base path (might need manual check)
    raise FileNotFoundError(f"Downloaded video file not found. Expected at: {base_path}")

@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    """Trigger post-processing analysis for passes and other analytics."""
    global recording_path, analysis_jobs
    
    data = request.get_json() or {}
    video_input = data.get('video_url') or data.get('video_path') or recording_path
    
    print(f"Received analyze request: {data}")
    
    if not video_input:
        print("Error: No video URL or path provided")
        return jsonify({
            'status': 'error',
            'message': 'No video URL or path provided.'
        }), 400
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    print(f"Created analysis job: {job_id} for input: {video_input}")
    
    # Start analysis in background thread
    def run_analysis():
        try:
            print(f"[{job_id}] Starting analysis for: {video_input}")
            
            # Ensure job entry exists
            if job_id not in analysis_jobs:
                print(f"[{job_id}] WARNING: Job entry not found, creating it...")
                analysis_jobs[job_id] = {
                    'status': 'processing',
                    'video_path': video_input,
                    'started_at': time.time(),
                    'message': 'Starting...'
                }
            
            video_path = None
            
            # Check if it's a YouTube URL
            if is_youtube_url(video_input):
                print(f"[{job_id}] Detected YouTube URL, starting download...")
                # Download YouTube video
                download_path = f"output_videos/youtube_{int(time.time())}"
                try:
                    analysis_jobs[job_id]['status'] = 'downloading'
                    analysis_jobs[job_id]['message'] = 'Downloading YouTube video...'
                except KeyError:
                    print(f"[{job_id}] KeyError updating status, recreating job entry")
                    analysis_jobs[job_id] = {
                        'status': 'downloading',
                        'message': 'Downloading YouTube video...',
                        'video_path': video_input,
                        'started_at': time.time()
                    }
                try:
                    video_path = download_youtube_video(video_input, download_path)
                    print(f"[{job_id}] Download complete: {video_path}")
                except Exception as e:
                    print(f"[{job_id}] Download failed: {e}")
                    analysis_jobs[job_id] = {
                        'status': 'failed',
                        'error': f'Download failed: {str(e)}',
                        'completed_at': time.time(),
                        'video_path': video_input,
                        'started_at': analysis_jobs.get(job_id, {}).get('started_at', time.time())
                    }
                    return
            elif os.path.exists(video_input):
                video_path = video_input
                print(f"[{job_id}] Using existing video file: {video_path}")
            else:
                error_msg = f'Video file not found: {video_input}'
                print(f"[{job_id}] {error_msg}")
                analysis_jobs[job_id] = {
                    'status': 'failed',
                    'error': error_msg,
                    'completed_at': time.time()
                }
                return
            
            if not video_path or not os.path.exists(video_path):
                error_msg = f'Video file not found after processing: {video_path}'
                print(f"[{job_id}] {error_msg}")
                analysis_jobs[job_id] = {
                    'status': 'failed',
                    'error': error_msg,
                    'completed_at': time.time()
                }
                return
            
            # Run analysis
            output_path = f"output_videos/analyzed_{int(time.time())}.mp4"
            try:
                analysis_jobs[job_id]['status'] = 'processing'
                analysis_jobs[job_id]['message'] = 'Step 1/8: Detecting players...'
            except KeyError:
                print(f"[{job_id}] KeyError updating status, recreating job entry")
                analysis_jobs[job_id] = {
                    'status': 'processing',
                    'message': 'Step 1/8: Detecting players...',
                    'video_path': video_input,
                    'started_at': time.time()
                }
            print(f"[{job_id}] Starting video analysis...")
            print(f"[{job_id}] This may take a while on CPU - processing {len(video_frames) if 'video_frames' in locals() else 'unknown'} frames...")
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            analyze_script = os.path.join(script_dir, 'analyze_recorded_video.py')
            
            if not os.path.exists(analyze_script):
                error_msg = f'Analysis script not found: {analyze_script}'
                print(f"[{job_id}] {error_msg}")
                analysis_jobs[job_id] = {
                    'status': 'failed',
                    'error': error_msg,
                    'completed_at': time.time()
                }
                return
            
            # Set environment to force CPU mode
            env = os.environ.copy()
            env['CUDA_VISIBLE_DEVICES'] = ''  # Disable CUDA
            
            cmd = [
                'python3', analyze_script,
                video_path,
                '--output_video', output_path,
                '--stub_path', 'stubs/',
                '--frame_skip', '2',
                '--target_width', '1280'
            ]
            
            print(f"[{job_id}] Running command: {' '.join(cmd)}")
            print(f"[{job_id}] Working directory: {script_dir}")
            print(f"[{job_id}] Analysis will output progress messages - this may take 30-60 minutes for a 20-minute video on CPU")
            
            # Use Popen to stream output and update status
            import subprocess as sp
            process = sp.Popen(
                cmd,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                text=True,
                cwd=script_dir,
                env=env,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output line by line and update status
            last_update_time = time.time()
            output_lines = []
            error_lines = []
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    output_lines.append(line)
                    print(f"[{job_id}] {line}")
                    
                    # Update status based on progress messages
                    current_time = time.time()
                    if current_time - last_update_time > 5:  # Update every 5 seconds
                        if 'STEP 1/8' in line or 'Detecting players' in line:
                            analysis_jobs[job_id]['message'] = 'Step 1/8: Detecting players...'
                        elif 'STEP 2/8' in line or 'Detecting ball' in line:
                            analysis_jobs[job_id]['message'] = 'Step 2/8: Detecting ball...'
                        elif 'STEP 3/8' in line or 'Detecting court keypoints' in line:
                            analysis_jobs[job_id]['message'] = 'Step 3/8: Detecting court keypoints...'
                        elif 'STEP 4/8' in line or 'Cleaning ball tracks' in line:
                            analysis_jobs[job_id]['message'] = 'Step 4/8: Cleaning ball tracks...'
                        elif 'STEP 5/8' in line or 'Assigning teams' in line:
                            analysis_jobs[job_id]['message'] = 'Step 5/8: Assigning teams...'
                        elif 'STEP 6/8' in line or 'Detecting ball possession' in line:
                            analysis_jobs[job_id]['message'] = 'Step 6/8: Detecting ball possession...'
                        elif 'STEP 7/8' in line or 'Detecting passes' in line:
                            analysis_jobs[job_id]['message'] = 'Step 7/8: Detecting passes...'
                        elif 'STEP 8/8' in line or 'Calculating tactical view' in line:
                            analysis_jobs[job_id]['message'] = 'Step 8/8: Calculating tactical view...'
                        elif 'RENDERING' in line or 'Drawing' in line:
                            analysis_jobs[job_id]['message'] = 'Rendering video with annotations...'
                        elif 'Saving' in line or 'Analysis complete' in line:
                            analysis_jobs[job_id]['message'] = 'Saving output video...'
                        
                        last_update_time = current_time
            
            # Wait for process to complete
            return_code = process.wait()
            
            # Create result object similar to subprocess.run
            class Result:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr
            
            result = Result(
                return_code,
                '\n'.join(output_lines),
                '\n'.join(error_lines) if error_lines else ''
            )
            
            print(f"[{job_id}] Analysis completed with return code: {result.returncode}")
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                print(f"[{job_id}] Error output (first 1000 chars): {error_msg[:1000]}")
                print(f"[{job_id}] Full stderr: {result.stderr}")
                print(f"[{job_id}] Full stdout: {result.stdout}")
                
                # Try to extract the most relevant error message
                error_lines = error_msg.split('\n')
                relevant_error = None
                for line in reversed(error_lines):
                    if line.strip() and ('error' in line.lower() or 'exception' in line.lower() or 'traceback' in line.lower() or 'failed' in line.lower()):
                        relevant_error = line.strip()
                        break
                
                if not relevant_error and error_lines:
                    relevant_error = error_lines[-1].strip() if error_lines[-1].strip() else error_msg[:200]
            else:
                relevant_error = None
            
            analysis_jobs[job_id] = {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'output_path': output_path if result.returncode == 0 else None,
                'error': relevant_error if result.returncode != 0 else None,
                'full_error': result.stderr if result.returncode != 0 else None,
                'stdout': result.stdout if result.returncode != 0 else None,
                'completed_at': time.time()
            }
        except subprocess.TimeoutExpired:
            error_msg = 'Analysis timed out after 1 hour'
            print(f"[{job_id}] {error_msg}")
            analysis_jobs[job_id] = {
                'status': 'failed',
                'error': error_msg,
                'completed_at': time.time()
            }
        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            print(f"[{job_id}] {error_msg}")
            import traceback
            traceback.print_exc()
            analysis_jobs[job_id] = {
                'status': 'failed',
                'error': error_msg,
                'traceback': traceback.format_exc(),
                'completed_at': time.time()
            }
    
    # Initialize job entry BEFORE starting thread to avoid race condition
    initial_status = 'downloading' if is_youtube_url(video_input) else 'processing'
    analysis_jobs[job_id] = {
        'status': initial_status,
        'video_path': video_input,
        'started_at': time.time(),
        'message': 'Initializing...'
    }
    
    # Start thread
    thread = threading.Thread(target=run_analysis)
    thread.daemon = True
    thread.start()
    
    print(f"Analysis job {job_id} started, status: {initial_status}")
    
    return jsonify({
        'status': 'success',
        'job_id': job_id,
        'message': 'Analysis started'
    })

@app.route('/api/analysis_status/<job_id>')
def get_analysis_status(job_id):
    """Get status of analysis job."""
    if job_id not in analysis_jobs:
        return jsonify({'status': 'error', 'message': 'Job not found'}), 404
    
    return jsonify(analysis_jobs[job_id])

@app.route('/api/reset_score', methods=['POST'])
def reset_score():
    """Reset the score."""
    global detector
    with detector_lock:
        if detector is None:
            return jsonify({'status': 'error', 'message': 'No detection running'}), 400
        
        detector.reset_score()
        return jsonify({'status': 'success', 'message': 'Score reset'})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('output_videos', exist_ok=True)
    os.makedirs('stubs', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Get port from environment (for production hosting) or use default
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("Starting Courtsight Web Application...")
    print(f"Open your browser and navigate to http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)

