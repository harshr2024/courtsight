# Deployment Steps for Courtsight

## 🎯 Quickest Option: Railway (Recommended)

### Pre-deployment Checklist:
- ✅ Code is on GitHub: `https://github.com/harshr2024/courtsight`
- ✅ `web_app.py` is production-ready (uses PORT env variable)
- ✅ `Procfile` is configured
- ⚠️ Model files need to be uploaded separately (too large for GitHub)

---

## Step-by-Step: Deploy to Railway

### 1. Go to Railway
Visit: **https://railway.app**

### 2. Sign Up / Login
- Click "Login" or "Start a New Project"
- Sign in with GitHub (easiest since your code is there)

### 3. Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub (if needed)
4. Select your repository: **`courtsight`**

### 4. Configure Deployment

Railway should auto-detect Python. But you need to set the **Root Directory**:

1. Click on your newly created service
2. Go to **Settings** tab
3. Find **"Root Directory"** or **"Working Directory"**
4. Set it to: **`basketball_analysis`**
5. Save

### 5. Deploy

Railway will automatically:
- Install dependencies from `requirements.txt`
- Run `web_app.py` using the `Procfile`
- Give you a public URL

### 6. Upload Model Files

Since model files aren't in GitHub, you need to add them:

**Option A: Via Railway CLI** (Recommended)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Upload models (from your local machine)
railway run bash
# Then inside the terminal:
mkdir -p models
# Upload your .pt files to models/ folder
```

**Option B: Via Railway Dashboard**
1. Go to your service → "Connect" → "Shell"
2. Create `models` directory: `mkdir -p models`
3. Upload files via Railway's file upload or use `scp`/`rsync`

**Option C: Download on Startup** (Best for production)
Modify `web_app.py` to download models from cloud storage (S3, etc.) on startup

### 7. Get Your URL

Railway will provide a URL like:
- `https://courtsight-production.up.railway.app`

Your site is now live! 🎉

---

## Alternative: Render.com

### 1. Go to Render
Visit: **https://render.com**

### 2. Sign Up
Create account (free tier available)

### 3. New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub account
3. Select repository: **`courtsight`**

### 4. Configure
- **Name**: `courtsight` (or any name)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: `basketball_analysis`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python3 web_app.py`

### 5. Deploy
Click **"Create Web Service"** and Render will deploy!

### 6. Get URL
Render gives you a URL like: `https://courtsight.onrender.com`

---

## Important Production Considerations:

### 1. Model Files
- Models are ~460MB total
- Need to be uploaded to the server
- Consider cloud storage (S3) for better management

### 2. Video Storage
- Downloaded YouTube videos and output videos need storage
- Consider using cloud storage (S3, Google Cloud Storage)
- Or use Railway/Render volumes for persistent storage

### 3. Processing Time
- Video analysis on CPU is slow (30-60 min for 20-min video)
- Consider:
  - GPU instances (more expensive)
  - Queue system for long-running jobs
  - Progress updates (already implemented)

### 4. Security (Important!)
Before going public, consider:
- Add authentication/login
- Rate limiting (prevent abuse)
- Input validation (YouTube URL validation)
- HTTPS (Railway/Render provide this automatically)

### 5. Environment Variables
You can set these in Railway/Render dashboard:
- `PORT` - Automatically set by hosting service
- `FLASK_ENV=production` - Disables debug mode
- Any API keys or secrets you need

---

## Current Setup Status:

✅ **Ready for deployment:**
- Code is on GitHub
- Production-ready configuration
- Procfile configured
- Uses environment PORT
- Error handling in place

⚠️ **Need to handle:**
- Model files (upload separately)
- Video storage (cloud storage recommended)
- Long processing times (consider async/queue)

---

## Testing Your Deployment:

Once deployed, test:
1. Visit your Railway/Render URL
2. Paste a YouTube URL
3. Click "Analyze Video"
4. Check if it downloads and processes

---

## Troubleshooting:

**App won't start:**
- Check Root Directory is set to `basketball_analysis`
- Check logs in Railway/Render dashboard
- Verify `requirements.txt` is correct

**Models not found:**
- Make sure models are uploaded to `models/` folder
- Check file paths in code match deployment structure

**Analysis fails:**
- Check CPU/memory limits on free tier
- Consider upgrading for better performance
- Check logs for specific errors

---

Good luck with deployment! 🚀

