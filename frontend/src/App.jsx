import { useState, useEffect } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'

function App() {
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [analysisStatus, setAnalysisStatus] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [speedProfile, setSpeedProfile] = useState('balanced')
  const scrollToAnalysis = () => {
    const section = document.getElementById('analysis')
    if (section) {
      section.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }
  const speedSettings = {
    speed: { frame_skip: 4, target_width: 720, use_gpu: true },
    balanced: { frame_skip: 2, target_width: 960, use_gpu: true },
    quality: { frame_skip: 1, target_width: 1280, use_gpu: true }
  }

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
        body: JSON.stringify({
          video_url: youtubeUrl,
          ...speedSettings[speedProfile]
        })
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
      <header className="navbar">
        <div className="nav-inner">
          <div className="logo">arion ai</div>
          <nav className="nav-links">
            <a href="#features">Features</a>
            <a href="#solutions">Solutions</a>
            <a href="#analysis">Analyze</a>
            <a href="#resources">Resources</a>
          </nav>
          <div className="nav-actions">
            <button className="btn ghost" onClick={scrollToAnalysis}>Start Analysis</button>
            <button className="btn primary" onClick={scrollToAnalysis}>Request Demo</button>
          </div>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-inner">
            <div className="hero-content">
              <span className="eyebrow">Basketball intelligence platform</span>
              <h1>Change the way you see the game.</h1>
              <p>
                Arion AI turns any basketball video into actionable insights. Detect passes, interceptions,
                possession changes, and tactical patterns automatically.
              </p>
              <div className="hero-actions">
                <button className="btn primary" onClick={scrollToAnalysis}>Analyze a game</button>
                <button className="btn ghost" onClick={scrollToAnalysis}>Watch demo</button>
              </div>
              <div className="hero-metrics">
                <div>
                  <span className="metric">40+</span>
                  <span className="metric-label">Insights per match</span>
                </div>
                <div>
                  <span className="metric">3x</span>
                  <span className="metric-label">Faster review</span>
                </div>
                <div>
                  <span className="metric">HD</span>
                  <span className="metric-label">Annotated playback</span>
                </div>
              </div>
            </div>
            <div className="hero-card">
              <div className="card-header">
                <span>Live analysis preview</span>
                <span className="pill">AI</span>
              </div>
              <div className="card-preview">
                <div className="preview-grid"></div>
                <div className="preview-overlay">
                  <div className="stat">
                    <span className="stat-value">+12</span>
                    <span className="stat-label">Passes detected</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">4</span>
                    <span className="stat-label">Possession swings</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">98%</span>
                    <span className="stat-label">Frame accuracy</span>
                  </div>
                </div>
              </div>
              <div className="card-footer">
                <span>Auto-tagged highlights</span>
                <button className="btn tiny">View report</button>
              </div>
            </div>
          </div>
        </section>

        <section className="brand-strip">
          <div className="brand-inner">
            <span>Trusted by teams and coaches worldwide</span>
            <div className="brand-list">
              <span>Elite Academies</span>
              <span>College Programs</span>
              <span>Pro Clubs</span>
              <span>Performance Labs</span>
            </div>
          </div>
        </section>

        <section id="features" className="section">
          <div className="section-inner">
            <div className="section-header">
              <h2>See your sport differently</h2>
              <p>Everything you need to turn video into tactical clarity.</p>
            </div>
            <div className="feature-grid">
              <div className="feature-card">
                <h3>Automated capture</h3>
                <p>Upload a YouTube link or recorded file and let Arion AI handle the rest.</p>
              </div>
              <div className="feature-card">
                <h3>AI-driven tagging</h3>
                <p>Identify passes, interceptions, and possession changes with frame-level precision.</p>
              </div>
              <div className="feature-card">
                <h3>Coach-ready insights</h3>
                <p>Visualize tactical patterns and player movement with clear overlays.</p>
              </div>
            </div>
          </div>
        </section>

        <section id="analysis" className="section analysis">
          <div className="section-inner">
            <div className="section-header">
              <h2>Analyze your game</h2>
              <p>Paste a YouTube link to generate your AI report and annotated playback.</p>
            </div>

            <div className="analysis-grid">
              <div className="analysis-video">
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

              <div className="analysis-panel">
                <div className="panel">
                  <h3>Start a new analysis</h3>
                  <p className="info-text">
                    Enter a YouTube URL to analyze basketball video for passes, interceptions, and tactical views.
                  </p>

                  <div className="speed-toggle">
                    <button
                      type="button"
                      className={`toggle-btn ${speedProfile === 'speed' ? 'active' : ''}`}
                      onClick={() => setSpeedProfile('speed')}
                      disabled={loading}
                    >
                      Speed
                    </button>
                    <button
                      type="button"
                      className={`toggle-btn ${speedProfile === 'balanced' ? 'active' : ''}`}
                      onClick={() => setSpeedProfile('balanced')}
                      disabled={loading}
                    >
                      Balanced
                    </button>
                    <button
                      type="button"
                      className={`toggle-btn ${speedProfile === 'quality' ? 'active' : ''}`}
                      onClick={() => setSpeedProfile('quality')}
                      disabled={loading}
                    >
                      Quality
                    </button>
                  </div>
                  <p className="helper-text">
                    Speed processes fewer frames at lower resolution. Quality processes every frame.
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
                      className="btn primary"
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
                        className="btn ghost"
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
                  <h4>How it works</h4>
                  <ul>
                    <li><strong>YouTube URL:</strong> Paste a link to analyze basketball gameplay.</li>
                    <li><strong>Video Download:</strong> The system securely retrieves the video.</li>
                    <li><strong>Analysis:</strong> AI detects passes, interceptions, and tactical patterns.</li>
                    <li><strong>Results:</strong> Watch annotated playback and export insights.</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="solutions" className="section light">
          <div className="section-inner">
            <div className="section-header">
              <h2>Solutions built for every team</h2>
              <p>From youth programs to professional clubs, Arion AI adapts to your workflow.</p>
            </div>
            <div className="solution-grid">
              <div className="solution-card">
                <h3>Coaches & teams</h3>
                <p>Accelerate game review with AI-tagged highlights and possession analytics.</p>
              </div>
              <div className="solution-card">
                <h3>Performance staff</h3>
                <p>Measure decision making, spacing, and tactical execution across games.</p>
              </div>
              <div className="solution-card">
                <h3>Scouting & recruiting</h3>
                <p>Surface key moments instantly to evaluate talent and opponent tendencies.</p>
              </div>
            </div>
          </div>
        </section>

        <section id="resources" className="section">
          <div className="section-inner">
            <div className="section-header">
              <h2>Resources & support</h2>
              <p>Everything you need to get started with Arion AI.</p>
            </div>
            <div className="resource-grid">
              <div className="resource-card">
                <h3>Quick start guide</h3>
                <p>Launch your first analysis in minutes with step-by-step instructions.</p>
              </div>
              <div className="resource-card">
                <h3>Deployment playbook</h3>
                <p>Best practices for hosting, scaling, and sharing analysis results.</p>
              </div>
              <div className="resource-card">
                <h3>Support center</h3>
                <p>FAQs and troubleshooting tips for smooth video processing.</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="footer-inner">
          <div>
            <div className="logo">arion ai</div>
            <p>Basketball intelligence for modern teams.</p>
          </div>
          <div className="footer-links">
            <a href="#features">Features</a>
            <a href="#analysis">Analyze</a>
            <a href="#solutions">Solutions</a>
          </div>
          <div className="footer-cta">
            <button className="btn primary" onClick={scrollToAnalysis}>Get started</button>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
