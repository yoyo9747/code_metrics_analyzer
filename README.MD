# Code Metrics Analyzer – Setup & Usage Guide

This repository contains a **Docker-based Code Metrics Analyzer** developed for the **COL740 – Software Engineering** course.  
It automatically analyzes Python codebases and computes the following metrics:

- **SLOC (Source Lines of Code)**
- **Cyclomatic Complexity**
- **Halstead Metrics**
- **Data-flow Metrics**

All four metrics are implemented in `code_metrics_analyzer.py` using Python’s **AST (Abstract Syntax Tree)** module.

---

## 1. Prerequisites
- Docker installed on your system  
- Internet connection (for cloning the open-source repositories)

---

## 2. Build the Docker Image

Place the following files in the same directory:
- `Dockerfile`
- `code_metrics_analyzer.py`
- `analyze_all.sh`

Then build the image:

```bash
docker build -t code-metrics-analyzer .
```

This creates a Docker image named **code-metrics-analyzer**.

---

## 3. Run Analysis on All Three Repositories

To automatically clone all three repositories and run the analysis:

```bash
docker run --name metrics-analyzer code-metrics-analyzer
```

This performs the following steps inside the container:

1. Clones repositories into `/app/codebases/`:
   - **Python-URL-Shortener**
   - **todo-cli**
   - **notejam-django** (stored as `notejam`)
2. Runs `code_metrics_analyzer.py` on each codebase
3. Stores detailed and summary metrics in `/app/results/`

Generated result files include:

```
url_shortener_metrics.json
url_shortener_metrics_summary.json
todo_cli_metrics.json
todo_cli_metrics_summary.json
notejam_metrics.json
notejam_metrics_summary.json
```

---

## 4. Copy Results from Container to Host

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

⚠️ **Important**:  
If you delete the container before running `docker cp`, **all results will be lost** because they only exist inside the container.

---

## 5. Optional: Interactive Mode

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
