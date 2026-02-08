# GitHub Setup Guide

## Quick Setup (Automated)

Run the setup script which will guide you through the process:

```bash
./setup-github.sh
```

This script will:
1. Initialize git repository
2. Add and commit all files
3. Guide you to create a GitHub repository
4. Push your code to GitHub

---

## Manual Setup

If you prefer to do it manually:

### 1. Initialize Git
```bash
git init
git add .
git commit -m "Initial commit: Sport Expert Multi-Agent Chatbot"
```

### 2. Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `sport-expert-chatbot` (or your choice)
3. Description: `Multi-Agent Sports Expert Chatbot powered by Google Gemini & ADK`
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

### 3. Push to GitHub
```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your actual values.

---

## Important Notes

### Files Excluded from Git (.gitignore)
- `.env` - Contains sensitive API keys (NEVER commit this!)
- `__pycache__/` - Python cache files
- `faiss_index/` - Can be regenerated from knowledge_base/
- `.vscode/`, `.idea/` - IDE settings

### Files Included (.env.example)
- A template showing required environment variables
- No actual secrets - safe to commit

### Before Pushing
Make sure to:
- ✅ Review `.gitignore` to ensure no secrets are committed
- ✅ Check that `.env` is NOT staged (`git status`)
- ✅ Update README with your specific deployment URLs (optional)

### After Pushing
Consider:
- Adding repository secrets for CI/CD (Settings → Secrets → Actions)
- Adding a LICENSE file
- Setting up GitHub Actions for automated deployment
- Adding badges to README (build status, license, etc.)

---

## Updating the Repository

After making changes:
```bash
git add .
git commit -m "Description of your changes"
git push
```

## Troubleshooting

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### Error: "failed to push some refs"
```bash
git pull origin main --rebase
git push origin main
```

### Checking what will be committed
```bash
git status
git diff --cached
```
