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

# Activate venv
source venv/bin/activate

# Install dependencies
echo "  Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "  Starting server at http://localhost:5001"
echo "  Press Ctrl+C to stop"
echo ""

python app.py
