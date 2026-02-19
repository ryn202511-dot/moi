@echo off
REM Build GameAccountRegistrar_Standalone.py to .EXE

echo ======================================================
echo  Game Account Registrar v2.1-OTP - Building EXE...
echo ======================================================
echo.

REM Check if dependencies are installed
echo [1/3] Checking dependencies...
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller -q
)

python -m pip show selenium >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Selenium...
    python -m pip install selenium webdriver-manager requests -q
)

echo Done!
echo.

REM Build EXE
echo [2/3] Building EXE (this may take a few minutes)...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name GameAccountRegistrar ^
    --icon=icon.ico ^
    GameAccountRegistrar_Standalone.py 2>nul

if %errorlevel% equ 0 (
    echo Done!
    echo.
    echo [3/3] Cleaning up...
    rmdir /s /q build >nul 2>&1
    del /q GameAccountRegistrar.spec >nul 2>&1
    echo Done!
    echo.
    echo ======================================================
    echo Success! 
    echo EXE file location: dist\GameAccountRegistrar.exe
    echo ======================================================
    echo.
    pause
    explorer dist
) else (
    echo ERROR: Build failed!
    pause
)
