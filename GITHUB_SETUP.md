# Setting Up GitHub Repository for Courtsight

Follow these steps to create a GitHub repository and push your code.

## Step 1: Create Repository on GitHub (Web)

1. Go to [github.com](https://github.com) and log in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Fill in:
   - **Repository name**: `courtsight` (or any name you want)
   - **Description**: "Basketball video analysis with AI-powered insights"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we'll add these)
4. Click **"Create repository"**

## Step 2: Initialize Git (if not already done)

Open terminal in your project folder and run:

```bash
cd /Users/harshraghuwanshi/Desktop/basket

# Check if git is already initialized
git status

# If not initialized, run:
git init
```

## Step 3: Add All Files

```bash
# Add all files to git
git add .

# Check what will be committed
git status
```

## Step 4: Make Initial Commit

```bash
git commit -m "Initial commit: Courtsight basketball analysis web app"
```

## Step 5: Connect to GitHub Repository

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
# Add the GitHub repository as remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/courtsight.git

# Verify it was added
git remote -v
```

## Step 6: Push to GitHub

```bash
# Push to GitHub (main branch)
git branch -M main
git push -u origin main
```

You'll be prompted for your GitHub username and password/token.

## Using GitHub Personal Access Token

If you get authentication errors, you'll need a Personal Access Token:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token"
3. Give it a name and select scopes: `repo` (full control)
4. Click "Generate token"
5. Copy the token (you'll only see it once!)
6. Use this token as your password when pushing

## Alternative: Using GitHub CLI

If you have GitHub CLI installed:

```bash
gh repo create courtsight --public --source=. --remote=origin --push
```

## Quick Copy-Paste Commands

Once you have your GitHub repo URL, run these in order:

```bash
cd /Users/harshraghuwanshi/Desktop/basket
git init
git add .
git commit -m "Initial commit: Courtsight basketball analysis web app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/courtsight.git
git push -u origin main
```

Remember to replace `YOUR_USERNAME` with your actual GitHub username!

