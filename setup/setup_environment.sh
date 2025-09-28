#!/bin/bash

echo "🚀 Setting up NIFTY Stock Manager environment..."

# Detect system architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    echo "✅ Apple Silicon detected"
    PYTHON_PATH="/opt/homebrew/bin/python3"
else
    echo "ℹ️  Intel Mac detected"
    PYTHON_PATH="/usr/bin/python3"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
$PYTHON_PATH -m venv nifty_env
source nifty_env/bin/activate

# Install dependencies
echo "⬇️  Installing dependencies..."
pip install --upgrade pip
pip install -r setup/requirements.txt

echo "✅ Environment setup complete!"
