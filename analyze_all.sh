#!/bin/bash
set -e

echo "=============================================="
echo "Code Metrics Analyzer - COL740 Project"
echo "=============================================="
echo ""

# Clone repositories if not already present
echo "Step 1: Cloning repositories..."
echo "----------------------------------------------"

if [ ! -d "/app/codebases/Python-URL-Shortener" ]; then
    echo "Cloning Python-URL-Shortener..."
    git clone https://github.com/MasiatHasin/Python-URL-Shortener.git /app/codebases/Python-URL-Shortener
else
    echo "Python-URL-Shortener already exists."
fi

if [ ! -d "/app/codebases/todo-cli" ]; then
    echo "Cloning todo-cli..."
    git clone https://github.com/lukosth/todo-cli.git /app/codebases/todo-cli
else
    echo "todo-cli already exists."
fi

if [ ! -d "/app/codebases/notejam" ]; then
    echo "Cloning notejam..."
    git clone https://github.com/yoyo9747/notejam-django.git /app/codebases/notejam
else
    echo "notejam already exists."
fi

echo ""
echo "Step 2: Analyzing codebases..."
echo "----------------------------------------------"

echo ""
echo "=== Analyzing Python-URL-Shortener ==="
python3 /app/code_metrics_analyzer.py \
    /app/codebases/Python-URL-Shortener \
    -o /app/results/url_shortener_metrics.json \
    -s

echo ""
echo "=== Analyzing todo-cli ==="
python3 /app/code_metrics_analyzer.py \
    /app/codebases/todo-cli \
    -o /app/results/todo_cli_metrics.json \
    -s

echo ""
echo "=== Analyzing notejam ==="
python3 /app/code_metrics_analyzer.py \
    /app/codebases/notejam \
    -o /app/results/notejam_metrics.json \
    -s

echo ""
echo "=============================================="
echo "Analysis Complete!"
echo "=============================================="
echo ""
echo "Results are available in /app/results/"
echo "- url_shortener_metrics.json & summary"
echo "- todo_cli_metrics.json & summary"
echo "- notejam_metrics.json & summary"
echo ""
echo "To access results from host:"
echo "docker cp <container_id>:/app/results ./results"
echo ""

