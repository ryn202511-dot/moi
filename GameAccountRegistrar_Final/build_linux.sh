#!/bin/bash
# Build GameAccountRegistrar_Standalone.py to executable on Linux/Mac
# Make this executable: chmod +x build_linux.sh

echo ""
echo "================================================"
echo "  Game Account Registrar v3.0 - Build"
echo "================================================"
echo ""

# Step 1: Check Python version
echo "[1/5] Checking Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Step 2: Upgrade pip
echo "[2/5] Upgrading pip..."
python3 -m pip install --upgrade pip -q

# Step 3: Install dependencies
echo "[3/5] Installing dependencies..."
python3 -m pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Step 4: Clean old builds
echo "[4/5] Cleaning old builds..."
rm -rf build dist *.spec

# Step 5: Build executable
echo "[5/5] Building executable (this may take 1-2 minutes)..."
echo ""
python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name GameAccountRegistrar \
    --add-data "requirements.txt:." \
    --hide-import=matplotlib \
    --collect-all selenium \
    --collect-all webdriver_manager \
    --collect-all requests \
    GameAccountRegistrar_Standalone.py

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "SUCCESS! Executable built successfully"
    echo "================================================"
    echo ""
    echo "File location: ./dist/GameAccountRegistrar"
    echo "Size: $(du -h dist/GameAccountRegistrar | cut -f1)"
    echo ""
    echo "You can now:"
    echo "1. Run: ./dist/GameAccountRegistrar"
    echo "2. Make it executable: chmod +x dist/GameAccountRegistrar"
    echo "3. Copy to /usr/local/bin/ to use systemwide"
    echo ""
else
    echo ""
    echo "ERROR: Build failed"
    echo ""
    echo "Try running test first:"
    echo "  python3 GameAccountRegistrar_Standalone.py"
    echo ""
    exit 1
fi
