#!/bin/bash

# COCOMO Analysis - Complete Setup and Deployment Script
# This script automates the entire process from setup to Docker Hub deployment

set -e  # Exit on any error

echo "============================================"
echo "COCOMO Analysis - Setup and Deployment"
echo "============================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if Docker is installed
echo "Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

# Check if user is logged into Docker Hub
echo ""
echo "Checking Docker Hub login..."
if ! docker info | grep -q "Username"; then
    print_info "Not logged into Docker Hub. Please login:"
    docker login
    if [ $? -ne 0 ]; then
        print_error "Docker login failed"
        exit 1
    fi
fi
print_success "Logged into Docker Hub"

# Get Docker Hub username
DOCKER_USERNAME=$(docker info | grep "Username" | awk '{print $2}')
print_info "Docker Hub username: $DOCKER_USERNAME"

# Create project directory structure
echo ""
echo "Setting up project structure..."
mkdir -p cocomo-project/{output,metrics}
cd cocomo-project
print_success "Project directory created"

# Create .dockerignore file
echo "Creating .dockerignore..."
cat > .dockerignore << 'EOF'
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.git/
.gitignore
README.md
*.md
.DS_Store
output/
.vscode/
.idea/
EOF
print_success ".dockerignore created"

# Save the Python script (you'll need to copy your cocomo_analysis.py here)
echo ""
print_info "Please ensure cocomo_analysis.py is in the current directory"
read -p "Press Enter once cocomo_analysis.py is ready..."

# Create Dockerfile
echo "Creating Dockerfile..."
cat > Dockerfile << 'EOF'
# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install required Python packages
RUN pip install --no-cache-dir radon lizard pandas numpy

# Copy the COCOMO analysis script
COPY cocomo_analysis.py .

# Create output directory
RUN mkdir -p /app/output

# Set environment variable to prevent Python buffering
ENV PYTHONUNBUFFERED=1

# Run the analysis when container starts
CMD ["python", "cocomo_analysis.py"]
EOF
print_success "Dockerfile created"

# Create docker-compose.yml
echo "Creating docker-compose.yml..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  cocomo-analysis:
    build: .
    container_name: cocomo-analysis-container
    volumes:
      - ./output:/app/output
    environment:
      - PYTHONUNBUFFERED=1
EOF
print_success "docker-compose.yml created"

# Build Docker image
echo ""
echo "============================================"
echo "Building Docker Image..."
echo "============================================"
IMAGE_NAME="cocomo-analysis"
docker build -t ${IMAGE_NAME}:latest .
if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Test the container locally
echo ""
echo "============================================"
echo "Testing Container Locally..."
echo "============================================"
docker run --rm ${IMAGE_NAME}:latest
if [ $? -eq 0 ]; then
    print_success "Container test passed"
else
    print_error "Container test failed"
    exit 1
fi

# Tag image for Docker Hub
echo ""
echo "============================================"
echo "Tagging Image for Docker Hub..."
echo "============================================"
docker tag ${IMAGE_NAME}:latest ${DOCKER_USERNAME}/${IMAGE_NAME}:latest
print_success "Image tagged as ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"

# Push to Docker Hub
echo ""
echo "============================================"
echo "Pushing to Docker Hub..."
echo "============================================"
print_info "This may take a few minutes..."
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest
if [ $? -eq 0 ]; then
    print_success "Successfully pushed to Docker Hub"
else
    print_error "Push to Docker Hub failed"
    exit 1
fi

# Create docker_hub.lnk file
echo ""
echo "Creating docker_hub.lnk file..."
DOCKER_HUB_URL="https://hub.docker.com/r/${DOCKER_USERNAME}/${IMAGE_NAME}"
echo "${DOCKER_HUB_URL}" > docker_hub.lnk
print_success "docker_hub.lnk created"

# Run container with volume mount to get results
echo ""
echo "============================================"
echo "Running Container with Volume Mount..."
echo "============================================"
docker run --rm -v $(pwd)/output:/app/output ${DOCKER_USERNAME}/${IMAGE_NAME}:latest
if [ -f "output/cocomo_results.json" ]; then
    print_success "Results saved to output/cocomo_results.json"
else
    print_info "Results may be in container logs (check above)"
fi

# Summary
echo ""
echo "============================================"
echo "DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
print_success "Docker image: ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
print_success "Docker Hub URL: ${DOCKER_HUB_URL}"
print_success "Results file: output/cocomo_results.json"
print_success "Submission file: docker_hub.lnk"
echo ""
print_info "Anyone can now run your analysis with:"
echo "  docker pull ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
echo "  docker run ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
echo ""
print_info "Files for Moodle submission:"
echo "  1. docker_hub.lnk"
echo "  2. Your report (PDF)"
echo "  3. output/cocomo_results.json"
echo "  4. Screenshots of Docker Hub and running container"
echo ""
print_info "Don't forget to make your Docker Hub repository PUBLIC!"
echo "  Go to: ${DOCKER_HUB_URL}/settings"
echo ""

# Verification commands
echo "============================================"
echo "VERIFICATION COMMANDS"
echo "============================================"
echo ""
echo "1. View local images:"
echo "   docker images | grep cocomo"
echo ""
echo "2. Test pull from Docker Hub:"
echo "   docker pull ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
echo ""
echo "3. Run pulled image:"
echo "   docker run ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
echo ""
echo "4. View results:"
echo "   cat output/cocomo_results.json"
echo ""
echo "5. Clean up local images:"
echo "   docker rmi ${IMAGE_NAME}:latest"
echo "   docker rmi ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
echo ""
echo "============================================"
print_success "Setup script completed successfully!"
echo "============================================"
