#!/bin/bash

# Deploy using Google Cloud Build (no local Docker required)
# This builds the image directly in Google Cloud

set -e

# Get the project root directory (parent of deployment/)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

PROJECT_ID="coastal-burner-480319-i7"
REGION="us-central1"
SERVICE_NAME="sport-expert-chatbot"
IMAGE_NAME="us-central1-docker.pkg.dev/${PROJECT_ID}/sport-expert/chatbot:latest"

echo "🔨 Building and deploying Sport Expert Chatbot using Cloud Build..."
echo "📁 Project root: ${PROJECT_ROOT}"
echo ""

# Step 1: Build in Cloud Build (from project root)
echo "📦 Step 1/2: Building Docker image in Cloud Build..."
cd "${PROJECT_ROOT}"
gcloud builds submit --tag ${IMAGE_NAME} --project ${PROJECT_ID}

# Step 2: Deploy to Cloud Run
echo ""
echo "🚀 Step 2/2: Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 120s \
  --concurrency 80 \
  --min-instances 1 \
  --max-instances 10 \
  --no-cpu-throttling \
  --cpu-boost \
  --set-env-vars GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},GOOGLE_GENAI_USE_VERTEXAI=True,TAVILY_API_KEY=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

echo ""
echo "✅ Build and deployment complete!"
echo ""
echo "🌐 Your service is available at:"
gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format='value(status.url)'
echo ""
echo "📊 Performance optimizations applied:"
echo "   ✓ Minimum instances: 1 (no cold starts)"
echo "   ✓ CPU: 2 vCPUs with boost"
echo "   ✓ Memory: 2GB"
echo "   ✓ Gunicorn: 2 workers × 4 threads"
echo "   ✓ Response time: Expected 1-5 seconds"
