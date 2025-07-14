#!/bin/bash

# Setup script for Cloud Storage Network Simulation
echo "🚀 Setting up Cloud Storage Network Simulation Environment"

# Check if Python virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To run the simulation:"
echo "1. Activate virtual environment: source .venv/bin/activate"
echo "2. Run simplified version: python sma_simplified.py"
echo "3. Run SPADE version (requires XMPP server): python cloud_storage_spade.py"
echo ""
echo "For SPADE version, you can either:"
echo "- Install and configure ejabberd locally"
echo "- Use a public XMPP server (modify the JIDs in the code)"
echo "- Run the simplified version for testing"
