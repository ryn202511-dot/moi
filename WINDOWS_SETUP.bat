@echo off
REM Quick setup script for Windows
REM Thực hiện setup để chạy được Game Account Registrar trên Windows

echo.
echo ================================================
echo   GAME ACCOUNT REGISTRAR - WINDOWS SETUP
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo SOLUTION:
    echo 1. Download Python from: https://www.python.org
    echo 2. During installation, CHECK "Add Python to PATH"
    echo 3. Restart CMD/Terminal
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo [+] Python found!
python --version
echo.

REM Check if we are in the right directory
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    echo Please run this script from the root directory (where requirements.txt is)
    pause
    exit /b 1
)

echo [1/3] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Cleaning previous builds...
rmdir /s /q build dist 2>nul
del *.spec 2>nul

echo.
echo [3/3] Building Windows executable...
echo This may take 1-2 minutes...
echo.
pyinstaller --onefile --windowed --name GameAccountRegistrar gui_launcher.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build executable
    pause
    exit /b 1
)

echo.
echo ================================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo ================================================
echo.
echo Executable: dist\GameAccountRegistrar.exe
echo.
echo TO RUN:
echo   1. Double-click: dist\GameAccountRegistrar.exe
echo   2. Or run: dist\run.bat
echo.
pause
