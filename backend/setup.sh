#!/bin/bash

# Check Python version
REQUIRED_PYTHON="3.13"
PYTHON_VERSION=$(python3.13 --version 2>&1 | awk '{print $2}')

if [[ ! "$PYTHON_VERSION" =~ ^3\.13\. ]]; then
    echo "Error: Python 3.13 is required, but you have Python $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python 3.13 detected: $PYTHON_VERSION"

# Setup virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment with Python 3.13..."
    python3.13 -m venv venv
fi

# Activate and install
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Setup complete!"
