# orchestrator/Dockerfile

FROM python:3.8-slim

# Ensure output is sent straight to terminal
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libyaml-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy orchestrator code
COPY orchestrator ./orchestrator

# Copy OSINT feed scripts and IOC enrichment
COPY osint/feeds ./osint/feeds
COPY osint/ioc_enrichment ./osint/ioc_enrichment

# Install Python dependencies
RUN pip install --no-cache-dir \
      boto3 \
      requests \
      PyYAML \
      elasticsearch>=7.0.0,<9.0.0 \
      feedparser

# Entrypoint: run the orchestrator scheduler
ENTRYPOINT ["python3", "-u", "orchestrator/runner.py"]

