# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install required Python packages
RUN pip install --no-cache-dir radon lizard pandas numpy

# Copy the COCOMO analysis script
COPY cocomo_analysis.py .

# Copy metrics data if you have it as a separate file
# COPY metrics_data.json .

# Create output directory
RUN mkdir -p /app/output

# Set environment variable to prevent Python buffering
ENV PYTHONUNBUFFERED=1

# Run the analysis when container starts
CMD ["python", "cocomo_analysis.py"]