#!/bin/bash

set -e  # exit immediately on any error

echo "📦 Setting up Patent Analyser FYP..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "🔧 Creating virtual environment using python3..."
  python3 -m venv .venv
fi

# Activate the environment
echo "✅ Activating environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies from requirements.txt..."
uv pip install -r requirements.txt

echo "🎉 Setup complete. Virtual environment is active."
echo "💡 You can now run: streamlit run app.py"
