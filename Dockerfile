# Multi-stage Docker build for Code Metrics Analyzer
# Optimized for COL740 Software Engineering course project

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy the analyzer script
COPY code_metrics_analyzer.py /app/

# Copy the analysis runner script
COPY analyze_all.sh /app/analyze_all.sh

# Make the scripts executable
RUN chmod +x /app/code_metrics_analyzer.py /app/analyze_all.sh

# Create directories for codebases and results
RUN mkdir -p /app/codebases /app/results

# Set Python to run in unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Default command: run analysis on all three codebases
CMD ["/app/analyze_all.sh"]

# Alternative: Allow running specific analyses (no custom entrypoint)
ENTRYPOINT []
