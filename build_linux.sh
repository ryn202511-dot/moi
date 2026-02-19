#!/bin/bash
# Script để build executable cho Linux/Mac
# Chạy: chmod +x build_linux.sh && ./build_linux.sh

set -e

echo ""
echo "================================================"
echo "   BUILDING GAME ACCOUNT REGISTRAR EXECUTABLE"
echo "================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found! Please install Python 3.8+"
    exit 1
fi

echo "[1/3] Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "[2/3] Cleaning old build..."
rm -rf build/ dist/ *.spec

echo ""
echo "[3/3] Building executable..."
pyinstaller --onefile --windowed --name GameAccountRegistrar gui_launcher.py

echo ""
echo "================================================"
echo "   BUILD COMPLETED SUCCESSFULLY!"
echo "================================================"
echo ""
echo "Executable location: dist/GameAccountRegistrar"
echo ""
echo "To run:"
echo "  ./dist/GameAccountRegistrar"
echo ""
