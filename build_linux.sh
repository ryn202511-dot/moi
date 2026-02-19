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
echo "Upgrading pip..."
pip3 install --upgrade pip
echo "Installing packages..."
pip3 install --no-cache-dir -r requirements.txt

echo "Checking PyInstaller installation..."
python3 -m pip show pyinstaller > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: PyInstaller not installed"
    echo "Trying to install again..."
    pip3 install --no-cache-dir pyinstaller==6.19.0
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install PyInstaller"
        exit 1
    fi
fi

echo ""
echo "[2/3] Cleaning old build..."
rm -rf build/ dist/ *.spec

echo ""
echo "[3/3] Building executable..."
echo "This may take 1-2 minutes..."
python3 -m PyInstaller --onefile --windowed --name GameAccountRegistrar gui_launcher.py

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build executable"
    exit 1
fi

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
