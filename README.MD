# Software Engineering Metrics and Estimation Project

This repository contains two main projects developed for the **COL740 – Software Engineering** course Homework 2:

1.  A **Code Metrics Analyzer** that computes SLOC, Cyclomatic Complexity, Halstead, and Data-flow metrics.
2.  A **COCOMO Analysis Tool** for software cost estimation.

-----

-----

## Part 1: Code Metrics Analyzer – Setup & Usage Guide

This component automatically analyzes Python codebases and computes the following metrics:

  - **SLOC (Source Lines of Code)**
  - **Cyclomatic Complexity**
  - **Halstead Metrics**
  - **Data-flow Metrics**

All four metrics are implemented in `code_metrics_analyzer.py` using Python’s **AST (Abstract Syntax Tree)** module.

-----

### 1\. Prerequisites

  - Docker installed on your system
  - Internet connection (for cloning the open-source repositories)

-----

### 2\. Build the Docker Image

Place the following files in the same directory:

  - `Dockerfile`
  - `code_metrics_analyzer.py`
  - `analyze_all.sh`

Then build the image:

```bash
docker build -t code-metrics-analyzer .
```

This creates a Docker image named **code-metrics-analyzer**.

-----

### 3\. Run Analysis on All Three Repositories

To automatically clone all three repositories and run the analysis:

```bash
docker run --name metrics-analyzer code-metrics-analyzer
```

This performs the following steps inside the container:

1.  Clones repositories into `/app/codebases/`:
      - **Python-URL-Shortener**
      - **todo-cli**
      - **notejam-django** (stored as `notejam`)
2.  Runs `code_metrics_analyzer.py` on each codebase
3.  Stores detailed and summary metrics in `/app/results/`

Generated result files include:

```
url_shortener_metrics.json
url_shortener_metrics_summary.json
todo_cli_metrics.json
todo_cli_metrics_summary.json
notejam_metrics.json
notejam_metrics_summary.json
```

-----

### 4\. Copy Results from Container to Host

Run the following to extract all results into your host system:

```bash
docker cp metrics-analyzer:/app/results ./results
```

Then you should see:

```bash
ls results
# notejam_metrics.json
# notejam_metrics_summary.json
# todo_cli_metrics.json
# todo_cli_metrics_summary.json
# url_shortener_metrics.json
# url_shortener_metrics_summary.json
```

**Important**:
If you delete the container before running `docker cp`, **all results will be lost** because they only exist inside the container.

-----

### 5\. Optional: Interactive Mode

To open a terminal inside the container:

```bash
docker run -it --entrypoint /bin/bash code-metrics-analyzer
```

Inside the container, you may manually run:

```bash
./analyze_all.sh
```

After manual execution, use:

```bash
docker cp <container_id_or_name>:/app/results ./results
```

-----

-----

## Part 2: COCOMO Software Metrics Analysis Project

Complete implementation of COCOMO models for software cost estimation with Docker deployment.

### Quick Start

#### Option 1: Automated Setup (Recommended)

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

#### Option 2: Manual Steps

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

### Docker Deployment

#### Pull and Run from Docker Hub

```bash
# Pull the image
docker pull YOUR_USERNAME/cocomo-analysis:latest

# Run the analysis
docker run YOUR_USERNAME/cocomo-analysis:latest

# Run with volume mount to save results
docker run -v $(pwd)/output:/app/output YOUR_USERNAME/cocomo-analysis:latest
```

#### Docker Hub Repository

**Format:** `https://hub.docker.com/r/watdipak7/code-metrics-analyzer`

