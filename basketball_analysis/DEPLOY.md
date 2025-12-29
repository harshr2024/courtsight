# Deploying Courtsight to Production

This guide covers deploying the Courtsight basketball analysis web application.

## Option 1: Railway (Recommended - Easiest)

Railway is the easiest option for deployment.

### Steps:

1. **Install Railway CLI** (optional, can use web interface):
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Deploy from GitHub**:
   - Push your code to GitHub
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Python and deploy

3. **Set Environment Variables** (if needed):
   - In Railway dashboard, go to Variables
   - Add: `PORT=5001` (Railway will provide PORT automatically)

4. **Update web_app.py for Railway**:
   ```python
   port = int(os.environ.get('PORT', 5001))
   app.run(host='0.0.0.0', port=port, debug=False)
   ```

## Option 2: Render

1. **Create account** at [render.com](https://render.com)

2. **Create New Web Service**:
   - Connect your GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python3 web_app.py`
   - Environment: Python 3

3. **Set Environment Variables**:
   - `PORT=5001` (Render provides PORT automatically)

## Option 3: Fly.io

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   flyctl auth login
   ```

2. **Initialize**:
   ```bash
   cd basketball_analysis
   flyctl launch
   ```

3. **Deploy**:
   ```bash
   flyctl deploy
   ```

## Option 4: Heroku

1. **Install Heroku CLI**

2. **Login and create app**:
   ```bash
   heroku login
   heroku create courtsight-app
   ```

3. **Deploy**:
   ```bash
   git push heroku main
   ```

## Important Notes for Production:

1. **Update web_app.py** to use environment PORT:
   ```python
   port = int(os.environ.get('PORT', 5001))
   app.run(host='0.0.0.0', port=port, debug=False)
   ```

2. **Models**: You'll need to upload model files to the hosting service or use cloud storage (S3, etc.)

3. **Storage**: Video files will need cloud storage (S3, etc.) for production

4. **CPU Processing**: Analysis will be slow on CPU - consider using GPU instances or async processing

5. **Security**: Add authentication, rate limiting, and input validation for production

## Quick Railway Deployment

The fastest way is Railway:

1. Push code to GitHub
2. Go to railway.app
3. New Project → GitHub Repo
4. Deploy!

Railway will handle everything automatically.

