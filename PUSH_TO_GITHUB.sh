#!/bin/bash
# Script to push Courtsight to GitHub
# Replace YOUR_USERNAME with your GitHub username before running

echo "Setting up GitHub repository..."
echo ""
echo "STEP 1: First, create a new repository on GitHub.com"
echo "  - Go to https://github.com/new"
echo "  - Repository name: courtsight"
echo "  - Don't initialize with README"
echo "  - Click 'Create repository'"
echo ""
read -p "Press Enter once you've created the repository on GitHub..."

echo ""
echo "STEP 2: Enter your GitHub username:"
read GITHUB_USERNAME

echo ""
echo "STEP 3: Connecting to GitHub and pushing code..."
echo ""

# Set branch to main
git branch -M main

# Add remote (will fail if already exists, that's okay)
git remote add origin https://github.com/$GITHUB_USERNAME/courtsight.git 2>/dev/null || git remote set-url origin https://github.com/$GITHUB_USERNAME/courtsight.git

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "Done! Your code should now be on GitHub."
echo "Visit: https://github.com/$GITHUB_USERNAME/courtsight"

