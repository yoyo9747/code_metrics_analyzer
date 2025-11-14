# Multi-stage Docker build for Code Metrics Analyzer with COCOMO Analysis
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

# Install required Python packages
RUN pip install --no-cache-dir radon lizard pandas numpy

# Copy all analysis scripts
COPY code_metrics_analyzer.py /app/
COPY cocomo_analysis.py /app/
COPY analyze_all.sh /app/analyze_all.sh

# Make the scripts executable
RUN chmod +x /app/code_metrics_analyzer.py /app/analyze_all.sh

# Create directories for codebases, results, and output
RUN mkdir -p /app/codebases /app/results /app/output

# Set Python to run in unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Default command: run analysis on all three codebases
CMD ["/app/analyze_all.sh"]

# Alternative: Allow running specific analyses
ENTRYPOINT []