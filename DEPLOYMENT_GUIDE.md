# Deployment Guide - Courtsight Basketball Analysis

This guide covers deploying both the **React Frontend** and **Flask Backend** to production.

## Architecture Overview

```
Frontend (React) → API Calls → Backend (Flask) → AI Models → Analysis
```

- **Frontend**: React app (Vite) - can be deployed to Vercel, Netlify, or Railway
- **Backend**: Flask API - deployed to Railway or Render
- **Models**: Stored on cloud storage or hosting service

---

## Option 1: Railway (Recommended - Easiest for Both)

### Deploy Backend

1. **Go to Railway**: https://railway.app
2. **Sign up/Login** (use GitHub to sign in)
3. **New Project** → **Deploy from GitHub repo**
4. **Select your repository**
5. **Important Settings**:
   - **Root Directory**: `basketball_analysis`
   - **Start Command**: `python3 web_app.py`
   - **Environment Variables**:
     - `PORT=5001` (Railway will auto-provide this, but defaults to 5001)
     - `FLASK_ENV=production`

6. **Add Models** (After first deploy):
   - Go to Railway dashboard → Your service → Settings
   - Connect to terminal/console
   - Upload model files to `models/` folder:
     - `ball_detector_model.pt`
     - `player_detector.pt`
     - `court_keypoint_detector.pt`

7. **Get Backend URL**: Railway will give you a URL like `https://courtsight-backend.up.railway.app`

### Deploy Frontend

1. **In Railway**: Create a new service in the same project
2. **Deploy from GitHub** (same repo)
3. **Settings**:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run preview` (or use Vercel/Netlify - see below)
   - **Environment Variables**:
     - `VITE_API_URL=https://your-backend-url.railway.app`

---

## Option 2: Separate Hosting (Best Practice)

### Backend: Railway or Render

**Railway** (recommended):
- Follow steps above for backend
- Get your backend URL

**Render** (alternative):
1. Go to https://render.com
2. Create new **Web Service**
3. Connect GitHub repo
4. Settings:
   - **Root Directory**: `basketball_analysis`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 web_app.py`
   - **Environment**: Python 3
5. Add environment variable: `VITE_API_URL` (you'll use this in frontend)

### Frontend: Vercel (Recommended)

1. **Go to Vercel**: https://vercel.com
2. **Sign up/Login** (use GitHub)
3. **New Project** → **Import Git Repository**
4. **Configure**:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. **Environment Variables**:
   - `VITE_API_URL=https://your-backend-url.railway.app`
   - (Replace with your actual backend URL)

6. **Deploy** - Vercel will auto-deploy on every push to main branch!

### Frontend: Netlify (Alternative)

1. **Go to Netlify**: https://netlify.com
2. **New site from Git**
3. **Settings**:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`

4. **Environment Variables**:
   - `VITE_API_URL=https://your-backend-url.railway.app`

---

## Model Storage Solutions

Since model files are large and shouldn't be in Git:

### Option A: Railway Volumes (Simple)
1. Add a Volume in Railway
2. Mount to `/models`
3. Upload model files via terminal

### Option B: Cloud Storage (Recommended for Production)
1. **Upload models to S3, Google Cloud Storage, or similar**
2. **Modify web_app.py** to download models on startup:
   ```python
   import boto3
   s3 = boto3.client('s3')
   s3.download_file('your-bucket', 'models/ball_detector_model.pt', 'models/ball_detector_model.pt')
   ```

### Option C: GitHub Releases (Free)
1. Create a GitHub release with model files
2. Download on first startup using GitHub API

---

## Environment Variables Reference

### Backend (Flask)
```
PORT=5001                    # Auto-provided by Railway/Render
FLASK_ENV=production         # Set to production
```

### Frontend (React)
```
VITE_API_URL=https://your-backend-url.railway.app
```

---

## Local Development

### Backend
```bash
cd basketball_analysis
pip install -r requirements.txt
python3 web_app.py
# Runs on http://localhost:5001
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
# Make sure VITE_API_URL in .env points to backend
```

---

## Quick Deploy Checklist

- [ ] Backend deployed to Railway/Render
- [ ] Backend URL obtained
- [ ] Models uploaded to backend
- [ ] Frontend deployed to Vercel/Netlify
- [ ] `VITE_API_URL` set in frontend environment variables
- [ ] Test the full flow: Frontend → Backend → Analysis

---

## Troubleshooting

### CORS Errors
- Make sure `flask-cors` is installed in backend
- Check that frontend `VITE_API_URL` matches backend URL exactly

### Models Not Found
- Verify models are uploaded to correct path
- Check file permissions on hosting service

### Build Failures
- Check Node.js version (should be 18+)
- Verify all dependencies in package.json
- Check build logs in deployment platform

### API Connection Issues
- Verify backend URL is accessible (test in browser)
- Check environment variables are set correctly
- Ensure backend is running (check logs)

---

## Next Steps

1. **Set up CI/CD**: Auto-deploy on git push
2. **Add monitoring**: Track errors and performance
3. **Set up database**: Store analysis history
4. **Add authentication**: Secure your API endpoints
5. **Optimize models**: Use quantized models for faster inference

---

## Support

For issues:
- Check deployment platform logs
- Verify environment variables
- Test API endpoints directly with curl/Postman
- Check browser console for frontend errors



