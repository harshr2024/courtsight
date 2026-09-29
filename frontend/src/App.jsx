import { useEffect, useState } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

function App() {
  const [videoFile, setVideoFile] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [job, setJob] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const analyze = async () => {
    if (!videoFile) return
    setSubmitting(true)
    setJob({ status: 'uploading', message: 'Uploading video' })
    const body = new FormData()
    body.append('video', videoFile)
    body.append('frame_skip', '2')
    body.append('target_width', '960')

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, { method: 'POST', body })
      const data = await response.json()
      if (!response.ok) throw new Error(data.message || 'Unable to start analysis')
      setJobId(data.job_id)
      setJob({ status: 'queued', message: 'Analysis queued' })
    } catch (error) {
      setSubmitting(false)
      setJob({ status: 'failed', message: 'Upload failed', error: error.message })
    }
  }

  useEffect(() => {
    if (!jobId) return undefined
    const interval = window.setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/analysis_status/${jobId}`)
        const data = await response.json()
        setJob(data)
        if (data.status === 'completed' || data.status === 'failed') {
          setSubmitting(false)
          window.clearInterval(interval)
        }
      } catch (error) {
        setSubmitting(false)
        setJob({ status: 'failed', message: 'Status check failed', error: error.message })
        window.clearInterval(interval)
      }
    }, 1500)
    return () => window.clearInterval(interval)
  }, [jobId])

  const reset = () => {
    setVideoFile(null)
    setJobId(null)
    setJob(null)
    setSubmitting(false)
  }

  const metadata = job?.metadata

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">CourtSight</div>
        <span className="scope-label">Detection demo</span>
      </header>

      <main>
        <section className="intro">
          <p className="eyebrow">Basketball computer vision</p>
          <h1>Turn a basketball clip into an annotated video.</h1>
          <p className="lede">
            CourtSight detects players, assigns temporary tracking IDs, marks observed basketball
            detections, and overlays detected court keypoints. It does not claim player identity,
            possession, scoring, or performance statistics.
          </p>
        </section>

        <section className="workspace" aria-label="Video analysis workspace">
          <div className="viewer">
            {job?.status === 'completed' && job.video_url ? (
              <video src={`${API_BASE_URL}${job.video_url}`} controls preload="metadata" />
            ) : (
              <div className="viewer-empty">
                <span>Annotated output</span>
                <p>Your processed video will appear here.</p>
              </div>
            )}
          </div>

          <div className="control-panel">
            <h2>Analyze a video</h2>
            <p className="helper">
              Use a short MP4, MOV, AVI, MKV, or WebM clip. The demo samples every other frame at
              up to 960 px and preserves the original playback duration.
            </p>

            <label className="file-picker">
              <span>{videoFile ? videoFile.name : 'Choose video file'}</span>
              <input
                type="file"
                accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska,video/webm"
                onChange={(event) => setVideoFile(event.target.files?.[0] || null)}
                disabled={submitting}
              />
            </label>

            <div className="actions">
              <button className="primary" onClick={analyze} disabled={!videoFile || submitting}>
                {submitting ? 'Processing…' : 'Create annotated video'}
              </button>
              {job && <button className="secondary" onClick={reset}>Reset</button>}
            </div>

            {job && (
              <div className={`status status-${job.status}`} role="status">
                <strong>{job.message || job.status}</strong>
                {job.error && <p>{job.error}</p>}
              </div>
            )}

            {metadata && (
              <dl className="metadata">
                <div><dt>Frames</dt><dd>{metadata.frame_count}</dd></div>
                <div><dt>Output FPS</dt><dd>{metadata.fps?.toFixed(2)}</dd></div>
                <div><dt>Duration</dt><dd>{metadata.duration_seconds?.toFixed(2)} s</dd></div>
                <div><dt>Resolution</dt><dd>{metadata.width} × {metadata.height}</dd></div>
              </dl>
            )}
          </div>
        </section>

        <section className="legend" aria-label="Annotation legend">
          <div><span className="mark player-mark" />Player detection with a temporary track ID</div>
          <div><span className="mark ball-mark" />Observed ball detection for that frame</div>
          <div><span className="mark court-mark" />Detected court keypoint</div>
        </section>

        <section className="limitations">
          <h2>What this demo does not infer</h2>
          <p>
            Track IDs are local to one clip and may change after occlusion. Missing ball detections
            are left missing rather than interpolated. Team assignment, possession, passes, speed,
            shots, and score are intentionally outside this demo’s supported scope.
          </p>
        </section>
      </main>
    </div>
  )
}

export default App
