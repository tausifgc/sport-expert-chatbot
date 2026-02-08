# Performance Optimization Guide

## Problem Analysis

Your chatbot was experiencing **1 minute 45 second response times** despite the actual agent processing taking less than 1 second.

### Root Causes Identified:

1. **Google Cloud Run Cold Starts** - Container scaling down between requests
2. **Thread Lock Bottleneck** - Unnecessary locking blocking concurrent requests
3. **Suboptimal Gunicorn Configuration** - Single worker with 8 threads and infinite timeout
4. **No CPU Allocation Between Requests** - CPU throttling when idle

## Applied Optimizations

### 1. Removed Thread Lock ✅
**File:** `src/main.py`
- Removed `request_lock` that was blocking concurrent requests
- The Google ADK Runner can handle concurrent requests safely

### 2. Optimized Gunicorn Settings ✅
**File:** `Dockerfile`
```bash
# Before:
--workers 1 --threads 8 --timeout 0

# After:
--workers 2 --threads 4 --timeout 120 --worker-class sync
```
- **2 workers**: Handle concurrent requests better
- **4 threads per worker**: Total 8 threads with better load distribution
- **120s timeout**: Reasonable timeout (0 = infinite caused issues)
- **Sync worker class**: More stable for this use case

### 3. Cloud Run Minimum Instances ✅
**New Feature:** Always keep at least 1 instance warm
```bash
--min-instances 1
```
- **Eliminates cold starts** entirely
- Trades cost for performance (instance always running)
- Response time should drop to **< 5 seconds**

### 4. Additional Cloud Run Optimizations ✅
```bash
--no-cpu-throttling     # Keep CPU allocated when idle
--cpu-boost             # Extra CPU during startup
--cpu 2                 # 2 vCPUs for faster processing
--memory 2Gi            # Sufficient RAM for FAISS index
--concurrency 80        # Handle up to 80 concurrent requests
```

## Expected Performance Improvements

| Scenario | Before | After |
|----------|--------|-------|
| Cold Start (first request) | 60-90s | 5-10s* |
| Warm Instance | 10-30s | 2-5s |
| Subsequent Requests | Variable | 1-3s |

*With `--min-instances 1`, cold starts are eliminated entirely

## Deployment Instructions

### Option 1: Quick Deploy (Recommended)
```bash
# Deploy everything in one command (uses Cloud Build - no Docker required)
./deploy.sh
```

This automatically:
- Builds the Docker image in Google Cloud Build
- Pushes to Artifact Registry
- Deploys to Cloud Run with all optimizations

### Option 2: Manual Deploy
If you prefer to build locally:
```bash
# 1. Build and push Docker image
docker build -t us-central1-docker.pkg.dev/coastal-burner-480319-i7/sport-expert/chatbot:latest .
docker push us-central1-docker.pkg.dev/coastal-burner-480319-i7/sport-expert/chatbot:latest

# 2. Deploy to Cloud Run
./deployment/deploy-cloud-build.sh
```

### Option 3: Using gcloud directly
```bash
gcloud run deploy sport-expert-chatbot \
  --image us-central1-docker.pkg.dev/coastal-burner-480319-i7/sport-expert/chatbot:latest \
  --platform managed \
  --region us-central1 \
  --project coastal-burner-480319-i7 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 120s \
  --concurrency 80 \
  --min-instances 1 \
  --max-instances 10 \
  --no-cpu-throttling \
  --cpu-boost \
  --set-env-vars GOOGLE_CLOUD_PROJECT=coastal-burner-480319-i7,GOOGLE_CLOUD_LOCATION=us-central1,GOOGLE_GENAI_USE_VERTEXAI=True,TAVILY_API_KEY=your-key
```

### Option 4: Using YAML Config
```bash
gcloud run services replace deployment/cloud-run-config.yaml
```

## Cost Implications

### With `--min-instances 1`:
- **Monthly Cost:** ~$50-70 USD for 1 always-running instance
- **Benefit:** Zero cold starts, instant responses

### Without `--min-instances` (cost-optimized):
```bash
# Remove this flag from deploy script:
--min-instances 1

# Instances scale to zero when idle (free)
# But cold starts return (~5-10s delay on first request)
```

### Cost-Performance Trade-off:
- **Keep min-instances=1 for production** (better UX)
- **Remove min-instances for development** (save costs)

## Monitoring Performance

### Check Cloud Run Logs:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sport-expert-chatbot" \
  --project coastal-burner-480319-i7 \
  --limit 50 \
  --format json
```

### Key Metrics to Watch:
1. **Request latency** - Should be < 5s for warm instances
2. **Cold start count** - Should be 0 with min-instances=1
3. **Instance count** - Should stay at 1 or more
4. **CPU utilization** - Should be < 50% average

## Troubleshooting

### If responses are still slow:

1. **Check if instances are cold starting:**
```bash
gcloud run services describe sport-expert-chatbot --region us-central1 | grep minScale
# Should show: minScale: "1"
```

2. **Verify FAISS index is loading fast:**
- Check logs for "Warming up resources..." at container start
- Should complete in < 5 seconds

3. **Test directly without UI:**
```bash
curl -X POST https://sport-expert-chatbot-997402636968.us-central1.run.app/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "what are the rules of tennis?"}'
```

4. **Check if Vertex AI API is slow:**
- Most Gemini API calls should return in < 1 second
- If slower, check API quotas and regional issues

## Additional Recommendations

### 1. Add Caching
Consider caching common queries with Redis or Memcached:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(query: str):
    # Cache results for identical queries
    pass
```

### 2. Async Processing
For very long queries, consider async responses:
- Return immediately with a request ID
- Use WebSockets or polling for results

### 3. Load Testing
Test the optimized deployment:
```bash
# Install Apache Bench
brew install httpd

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 -p query.json -T application/json \
  https://sport-expert-chatbot-997402636968.us-central1.run.app/ask
```

## Summary

**Key Changes Made:**
1. ✅ Removed blocking thread lock
2. ✅ Optimized Gunicorn to 2 workers × 4 threads
3. ✅ Set min-instances=1 to eliminate cold starts
4. ✅ Enabled CPU boost and no throttling
5. ✅ Increased resources to 2 vCPU + 2GB RAM

**Expected Result:**
- **Before:** 1 minute 45 seconds
- **After:** 1-5 seconds (with warm instance)

**Deploy the changes and test!** 🚀
