import { useState, useEffect } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'

function App() {
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [analysisStatus, setAnalysisStatus] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    if (!youtubeUrl.trim()) {
      alert('Please enter a YouTube URL')
      return
    }

    setLoading(true)
    setAnalysisStatus({ status: 'starting', message: 'Starting analysis...' })

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_url: youtubeUrl })
      })

      const data = await response.json()

      if (data.status === 'success') {
        setJobId(data.job_id)
        setAnalysisStatus({ status: 'processing', message: 'Analysis started...' })
      } else {
        alert('Error: ' + (data.message || 'Failed to start analysis'))
        setLoading(false)
      }
    } catch (error) {
      alert('Error starting analysis: ' + error.message)
      setLoading(false)
      setAnalysisStatus(null)
    }
  }

  useEffect(() => {
    if (!jobId) return

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/analysis_status/${jobId}`)
        const data = await response.json()

        setAnalysisStatus({
          status: data.status,
          message: data.message || data.status,
          outputPath: data.output_path,
          error: data.error
        })

        if (data.status === 'completed') {
          setLoading(false)
          if (data.video_url) {
            setVideoUrl(`${API_BASE_URL}${data.video_url}`)
          }
          clearInterval(interval)
        } else if (data.status === 'failed') {
          setLoading(false)
          clearInterval(interval)
        }
      } catch (error) {
        console.error('Error checking status:', error)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [jobId])

  const resetAnalysis = () => {
    setYoutubeUrl('')
    setAnalysisStatus(null)
    setJobId(null)
    setVideoUrl(null)
    setLoading(false)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>Courtsight</h1>
          <p className="subtitle">Basketball video analysis with AI-powered insights</p>
        </div>
      </header>

      <main className="main-content">
        <div className="video-section">
          <div className="video-container">
            {videoUrl ? (
              <video 
                src={videoUrl} 
                controls 
                className="video-player"
                autoPlay={false}
              >
                Your browser does not support the video tag.
              </video>
            ) : (
              <div className="video-placeholder">
                <div className="placeholder-content">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="2" y="2" width="20" height="20" rx="2" />
                    <path d="M10 8l6 4-6 4V8z" />
                  </svg>
                  <p>Video preview will appear here after analysis</p>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="controls-section">
          <div className="panel">
            <h2>Video Analysis</h2>
            <p className="info-text">
              Enter a YouTube URL to analyze basketball video for passes, interceptions, and other analytics
            </p>

            <div className="input-group">
              <input
                type="text"
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !loading && handleAnalyze()}
                placeholder="https://www.youtube.com/watch?v=..."
                className="url-input"
                disabled={loading}
              />
            </div>

            <div className="button-group">
              <button
                onClick={handleAnalyze}
                disabled={loading || !youtubeUrl.trim()}
                className="btn btn-primary"
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Analyzing...
                  </>
                ) : (
                  'Analyze Video'
                )}
              </button>
              {analysisStatus && (
                <button
                  onClick={resetAnalysis}
                  className="btn btn-secondary"
                >
                  Reset
                </button>
              )}
            </div>

            {analysisStatus && (
              <div className="status-panel">
                <div className="status-item">
                  <span className="status-label">Status:</span>
                  <span className={`status-value status-${analysisStatus.status}`}>
                    {analysisStatus.message || analysisStatus.status}
                  </span>
                </div>
                {analysisStatus.error && (
                  <div className="status-item error">
                    <span className="status-label">Error:</span>
                    <span className="status-value">{analysisStatus.error}</span>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="info-panel">
            <h3>How it works</h3>
            <ul>
              <li><strong>YouTube URL:</strong> Paste a YouTube video link to analyze basketball gameplay</li>
              <li><strong>Video Download:</strong> The system automatically downloads the video from YouTube</li>
              <li><strong>Analysis:</strong> Full analysis includes player tracking, passes, interceptions, and tactical views</li>
              <li><strong>Results:</strong> Analyzed video with all annotations will be displayed above</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
