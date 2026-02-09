# Quick Deployment Guide - Railway (Easiest!)

## 🚀 Deploy to Railway in 5 Minutes

### Step 1: Make sure code is on GitHub ✅
Your code is already on GitHub at: `https://github.com/harshr2024/courtsight`

### Step 2: Deploy on Railway

1. **Go to Railway**: https://railway.app
2. **Sign up/Login** (you can use GitHub to sign in)
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Select your `courtsight` repository**
6. **Railway will automatically**:
   - Detect it's a Python app
   - Install dependencies from `requirements.txt`
   - Run the app using the `Procfile`

### Step 3: Set Working Directory (Important!)

Since your `web_app.py` is in the `basketball_analysis` folder:

1. In Railway dashboard, go to your service
2. Click on **Settings**
3. Find **"Root Directory"** or **"Working Directory"**
4. Set it to: `basketball_analysis`
5. Save

### Step 4: Add Models (After First Deploy)

Since model files aren't in GitHub, you have a few options:

**Option A: Upload via Railway Console**
1. After deployment, go to Railway dashboard
2. Click on your service → "Connect" or "Terminal"
3. Upload model files to `models/` folder

**Option B: Use Railway Volumes** (Better for persistent storage)
1. Add a Volume in Railway dashboard
2. Mount it to `/models`
3. Upload model files there

**Option C: Use Cloud Storage** (Best for production)
- Upload models to AWS S3, Google Cloud Storage, etc.
- Download them on app startup

### Step 5: Get Your URL

Railway will give you a public URL like:
`https://courtsight-production.up.railway.app`

That's it! Your site will be live! 🎉

---

## Alternative: Render (Also Easy)

1. Go to https://render.com
2. Sign up (free tier available)
3. New → Web Service
4. Connect GitHub repo: `harshr2024/courtsight`
5. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 web_app.py`
   - **Root Directory**: `basketball_analysis`
6. Deploy!

---

## Important Notes:

1. **Models**: You'll need to upload the `.pt` model files separately (they're too large for GitHub)
2. **Video Storage**: For production, consider using cloud storage (S3) for uploaded/downloaded videos
3. **Processing Time**: Video analysis on CPU will be slow - consider GPU instances for production
4. **Free Tiers**: Both Railway and Render have free tiers with limitations

---

## Current Status:

✅ Code is ready for deployment
✅ `web_app.py` uses PORT from environment (production-ready)
✅ `Procfile` is configured
✅ `.gitignore` excludes large files

Just deploy and upload your model files!

