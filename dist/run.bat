@echo off
REM Batch file để chạy Game Account Registrar Tool

echo.
echo ============================================
echo   GAME ACCOUNT REGISTRAR TOOL
echo   Game Account Auto Registration Tool
echo ============================================
echo.

REM Check if Windows executable exists
if exist "%~dp0GameAccountRegistrar.exe" (
    echo [+] Found Windows executable!
    "%~dp0GameAccountRegistrar.exe"
    pause
    exit /b 0
)

REM Check if Linux executable exists
if exist "%~dp0GameAccountRegistrar" (
    echo [!] Found Linux executable (not compatible with Windows)
    echo.
    echo To run on Windows, you need to:
    echo.
    echo OPTION 1: Build Windows .exe from Python source
    echo ================================================
    echo 1. Install Python 3.8+ from https://www.python.org
    echo 2. Open CMD in parent directory (where requirements.txt is)
    echo 3. Run: build_windows.bat
    echo 4. Then run: dist\GameAccountRegistrar.exe
    echo.
    echo OPTION 2: Use Python directly
    echo ================================================
    echo 1. Install Python 3.8+ from https://www.python.org
    echo 2. Open CMD and run: python gui_launcher.py
    echo.
    pause
    exit /b 1
)

echo [ERROR] No executable found!
echo.
echo Please run the build script first:
echo   - Windows: build_windows.bat (requires Python)
echo   - Linux/Mac: ./build_linux.sh (requires Python)
echo.
pause
exit /b 1
