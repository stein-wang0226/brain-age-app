#!/bin/bash
# NeuroAge - Brain Age Prediction System
# Startup script

cd "$(dirname "$0")"

echo ""
echo "  NeuroAge - Brain Age Prediction System"
echo "  ========================================"
echo ""

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

# Use venv Python directly (absolute path, no source activate needed)
PYTHON="$(pwd)/venv/bin/python"
PIP="$(pwd)/venv/bin/pip"

# Install dependencies
echo "  Installing dependencies..."
$PIP install -q -r requirements.txt

echo ""
echo "  Starting server at http://localhost:5001"
echo "  Press Ctrl+C to stop"
echo ""

$PYTHON app.py
