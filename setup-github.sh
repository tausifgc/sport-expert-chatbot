#!/bin/bash

# GitHub Repository Setup Script
# This script initializes git, commits files, and helps you push to GitHub

set -e

echo "🚀 Setting up GitHub repository for Sport Expert Chatbot..."
echo ""

# Step 1: Initialize git repository
echo "📦 Step 1/5: Initializing git repository..."
git init

# Step 2: Add all files
echo "📝 Step 2/5: Adding files to git..."
git add .

# Step 3: Create initial commit
echo "💾 Step 3/5: Creating initial commit..."
git commit -m "Initial commit: Sport Expert Multi-Agent Chatbot

- Multi-agent system using Google ADK and Gemini 2.0 Flash
- RAG-based knowledge retrieval for Tennis & Cricket
- Web search integration via Tavily for other sports
- Performance optimized for Google Cloud Run (1-5s response time)
- Fully containerized with Docker
- Production-ready deployment scripts"

# Step 4: Instructions for creating GitHub repo
echo ""
echo "✅ Local git repository is ready!"
echo ""
echo "📋 Step 4/5: Create a GitHub repository:"
echo "   1. Go to: https://github.com/new"
echo "   2. Repository name: sport-expert-chatbot (or your choice)"
echo "   3. Description: Multi-Agent Sports Expert Chatbot powered by Google Gemini & ADK"
echo "   4. Choose: Public or Private"
echo "   5. DO NOT initialize with README (we already have one)"
echo "   6. Click 'Create repository'"
echo ""
echo "⏸️  Press Enter after you've created the GitHub repository..."
read -r

# Step 5: Get GitHub repo URL and push
echo ""
echo "📤 Step 5/5: Push to GitHub"
echo ""
echo "Enter your GitHub repository URL (e.g., https://github.com/username/sport-expert-chatbot.git):"
read -r REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ No URL provided. Exiting..."
    exit 1
fi

# Add remote and push
git branch -M main
git remote add origin "$REPO_URL"
git push -u origin main

echo ""
echo "🎉 Successfully pushed to GitHub!"
echo "🌐 Your repository: $REPO_URL"
echo ""
echo "📝 Next steps:"
echo "   - Add repository secrets for TAVILY_API_KEY (if using GitHub Actions)"
echo "   - Update README with your specific Cloud Run URLs"
echo "   - Consider adding CI/CD workflows"
