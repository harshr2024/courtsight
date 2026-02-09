# Quick GitHub Setup Guide

## ✅ Your code is ready! Now follow these steps:

### Step 1: Create Repository on GitHub

1. Go to **https://github.com/new**
2. Repository name: `courtsight` (or any name you like)
3. Description: "Basketball video analysis with AI"
4. Choose **Public** or **Private**
5. **⚠️ IMPORTANT:** Do NOT check "Add a README file" or any other options
6. Click **"Create repository"**

### Step 2: Connect and Push (Copy and paste these commands)

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
cd /Users/harshraghuwanshi/Desktop/basket
git remote add origin https://github.com/YOUR_USERNAME/courtsight.git
git branch -M main
git push -u origin main
```

### Example:
If your GitHub username is `johnsmith`, you would run:
```bash
git remote add origin https://github.com/johnsmith/courtsight.git
git branch -M main
git push -u origin main
```

### Step 3: Authentication

When you run `git push`, you'll be prompted for:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your password!)

#### To create a Personal Access Token:
1. Go to GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Click "Generate new token (classic)"
4. Name it: "Courtsight Push"
5. Select scope: **`repo`** (check the box)
6. Click "Generate token"
7. **Copy the token** (you'll only see it once!)
8. Use this token as your password when pushing

---

## 🚀 That's it! Your code will be on GitHub.

After pushing, visit: `https://github.com/YOUR_USERNAME/courtsight`

---

## Troubleshooting

**If remote already exists:**
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/courtsight.git
git push -u origin main
```

**If you need to start over:**
```bash
git reset
git add .
git commit -m "Initial commit: Courtsight"
```

