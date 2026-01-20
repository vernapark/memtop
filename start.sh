#!/bin/bash
# Render.com startup script

echo "========================================"
echo "Starting Video Streaming Site + Bot"
echo "========================================"
echo "Python version:"
python --version
echo "Pip version:"
pip --version
echo "Current directory:"
pwd
echo "Files present:"
ls -la
echo "========================================"

# Run the combined server
exec python combined_server.py
