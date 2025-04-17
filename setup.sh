#!/bin/bash

set -e

echo "📦 Setting up Patent Analyser FYP..."

# Create .venv if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "🔧 Creating virtual environment..."
  uv venv
fi

# Activate the environment
echo "✅ Activating environment..."
source .venv/bin/activate

# Install everything from requirements.txt
echo "📥 Installing dependencies from requirements.txt..."
uv pip install --requirements requirements.txt

echo "🎉 Setup complete. You're ready to go!"
