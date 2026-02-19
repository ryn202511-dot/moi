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

echo Checking PyInstaller installation...
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller not installed
    echo Trying to install again...
    pip install --no-cache-dir pyinstaller==6.19.0
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo [2/3] Cleaning old build...
rmdir /s /q build dist 2>nul
del *.spec 2>nul

echo.
echo [3/3] Building executable...
echo This may take 1-2 minutes...
echo.

REM Use python -m to ensure pyinstaller is found
python -m PyInstaller --onefile --windowed --name GameAccountRegistrar gui_launcher_advanced.py
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
