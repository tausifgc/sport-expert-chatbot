# Use pre-built base image with dependencies (fast!)
# If base image doesn't exist, fall back to installing dependencies
ARG BASE_IMAGE=us-central1-docker.pkg.dev/coastal-burner-480319-i7/sport-expert/base:latest
FROM ${BASE_IMAGE}

WORKDIR /app

# Copy source code (this is the only thing that changes frequently)
COPY . .

# Gunicorn will listen on the port specified by $PORT env var
# Optimized settings: 2 workers, 4 threads each, 120s timeout
CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "--threads", "4", "--timeout", "120", "--worker-class", "sync", "--access-logfile", "-", "--error-logfile", "-", "src.main:app"]
