# CourtSight frontend

This React/Vite interface is the single UI for CourtSight's supported local
demo: upload a video, wait for player tracks, observed ball detections, and
court keypoints, then play the correctly timed annotated output.

Use Node.js 20.19 or newer. From this directory:

```bash
npm ci
npm run lint
npm run build
```

The Flask service in `../basketball_analysis/web_app.py` serves the resulting
`dist/` directory and API together at `http://localhost:5001`. For frontend-only
development, `npm run dev` starts Vite on port 3000 and proxies `/api` and
`/video` requests to Flask on port 5001.

Model downloads, Python 3.11 setup, sample-video availability, limitations, and
the complete run instructions are documented in the repository root
[README](../README.md).
