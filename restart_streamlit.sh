#!/bin/bash
# Restart Streamlit and clear all Python caches for reliable backend reloads

# Kill any running Streamlit processes
echo "Stopping Streamlit..."
pkill -f streamlit || true

# Remove all __pycache__ directories
find . -type d -name '__pycache__' -exec rm -rf {} +

# Restart Streamlit
echo "Starting Streamlit..."
streamlit run ui/app.py --server.headless true
