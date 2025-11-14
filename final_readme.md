# COCOMO Software Metrics Analysis Project

Complete implementation of COCOMO models for software cost estimation with Docker deployment.

## 📁 Project Structure

```
cocomo-project/
├── cocomo_analysis.py          # Main COCOMO analysis script
├── visualization.py            # Generates charts for report
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── setup.sh                    # Automated deployment script
├── docker_hub.lnk             # Docker Hub repository link
├── output/                     # Generated results
│   ├── cocomo_results.json    # COCOMO analysis results
│   ├── cocomo_comparison.png  # Comparison charts
│   ├── metrics_heatmap.png    # Complexity heatmap
│   ├── cost_drivers.png       # Cost drivers visualization
│   ├── effort_breakdown.png   # Effort distribution
│   └── timeline_gantt.png     # Timeline comparison
└── README.md                   # This file
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Make script executable
chmod +x setup.sh

# Run complete setup and deployment
./setup.sh
```

This will:
- Build Docker image
- Test locally
- Push to Docker Hub
- Generate all outputs
- Create submission files

### Option 2: Manual Steps

```bash
# 1. Install dependencies (for local testing)
pip install radon lizard pandas numpy matplotlib

# 2. Run analysis locally
python cocomo_analysis.py

# 3. Generate visualizations
python visualization.py

# 4. Build Docker image
docker build -t cocomo-analysis:latest .

# 5. Test container
docker run cocomo-analysis:latest

# 6. Tag and push to Docker Hub
docker tag cocomo-analysis:latest YOUR_USERNAME/cocomo-analysis:latest
docker login
docker push YOUR_USERNAME/cocomo-analysis:latest
```

## 🐳 Docker Deployment

### Pull and Run from Docker Hub

```bash
# Pull the image
docker pull YOUR_USERNAME/cocomo-analysis:latest

# Run the analysis
docker run YOUR_USERNAME/cocomo-analysis:latest

# Run with volume mount to save results
docker run -v $(pwd)/output:/app/output YOUR_USERNAME/cocomo-analysis:latest
```

### Docker Hub Repository

**Format:** `https://hub.docker.com/r/YOUR_USERNAME/cocomo-analysis`