@echo off
REM Script để build file .EXE cho Windows
REM Chạy script này trên Windows cmd.exe

echo.
echo ================================================
echo   BUILDING GAME ACCOUNT REGISTRAR .EXE
echo ================================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
echo Upgrading pip...
python -m pip install --upgrade pip
echo Installing packages...
pip install --no-cache-dir -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Try: pip install --upgrade pip
    pause
    exit /b 1
)

echo.
echo [2/3] Cleaning old build...
rmdir /s /q build dist *.spec 2>nul

echo.
echo [3/3] Building executable...
pyinstaller --onefile --windowed --name GameAccountRegistrar gui_launcher.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to build executable
    pause
    exit /b 1
)

echo.
echo ================================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo ================================================
echo.
echo Executable location: dist\GameAccountRegistrar.exe
echo.
goto end

:end
pause
