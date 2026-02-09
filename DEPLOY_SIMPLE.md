# 🚀 Simple Deployment Guide

## Deploy to Railway (Easiest - 5 minutes!)

### Step 1: Your code is already on GitHub ✅
Repository: `https://github.com/harshr2024/courtsight`

### Step 2: Deploy on Railway

1. **Visit**: https://railway.app
2. **Sign up/Login** (use GitHub login for easiest setup)
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your `courtsight` repository**
6. **Set Root Directory**:
   - Go to your service → Settings
   - Set "Root Directory" to: `basketball_analysis`
   - OR Railway will auto-detect it

### Step 3: Wait for deployment
Railway will automatically:
- Install all dependencies
- Start your app
- Give you a public URL

### Step 4: Upload Model Files
Since models aren't in GitHub (too large), upload them:

**Quick Method:**
1. Railway dashboard → Your service → Connect → Shell
2. Run: `mkdir -p models`
3. Upload your `.pt` files to the `models/` folder

### Step 5: Done! 🎉
Your site will be live at: `https://your-app-name.up.railway.app`

---

## That's it!

Your app is configured and ready. Just:
1. Deploy on Railway
2. Upload model files
3. Start using it!

For detailed steps, see `basketball_analysis/DEPLOYMENT_STEPS.md`

