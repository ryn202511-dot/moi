@echo off
REM Build GameAccountRegistrar_Standalone.py to .EXE
REM Complete build script for Windows with error handling

echo.
echo ================================================
echo  Game Account Registrar v3.0 - Build to EXE
echo ================================================
echo.

setlocal enabledelayedexpansion

REM Step 1: Upgrade pip
echo [1/5] Upgrading pip...
python -m pip install --upgrade pip -q

REM Step 2: Install dependencies from requirements.txt
echo [2/5] Installing dependencies...
python -m pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Step 3: Clean old builds
echo [3/5] Cleaning old builds...
if exist build rmdir /s /q build >nul 2>&1
if exist dist rmdir /s /q dist >nul 2>&1
del /q *.spec >nul 2>&1

REM Step 4: Build EXE
echo [4/5] Building executable (this may take 1-2 minutes)...
echo.
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name GameAccountRegistrar ^
    --add-data "requirements.txt:." ^
    --hide-import=matplotlib ^
    --collect-all selenium ^
    --collect-all webdriver_manager ^
    --collect-all requests ^
    GameAccountRegistrar_Standalone.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: PyInstaller build failed
    echo.
    echo Possible causes:
    echo - Python version incompatibility
    echo - Missing dependencies
    echo - File path issues
    echo.
    echo Try running:
    echo   python GameAccountRegistrar_Standalone.py
    echo.
    pause
    exit /b 1
)

REM Step 5: Verify and cleanup
echo [5/5] Finalizing...
if exist dist\GameAccountRegistrar.exe (
    echo.
    echo ================================================
    echo SUCCESS! Executable built successfully
    echo ================================================
    echo.
    echo File location: dist\GameAccountRegistrar.exe
    echo Size: 
    for %%F in (dist\GameAccountRegistrar.exe) do echo %%~sF bytes
    echo.
    echo You can now:
    echo 1. Move GameAccountRegistrar.exe to desktop
    echo 2. Run it directly - no Python needed!
    echo.
    
    REM Optional: Open dist folder
    echo Opening dist folder...
    start "" dist
    
    echo.
    pause
) else (
    echo ERROR: EXE file not found after build
    pause
    exit /b 1
)

endlocal
