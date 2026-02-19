@echo off
REM Batch file để chạy Game Account Registrar Tool
REM File này chạy executable trên Windows

echo.
echo ============================================
echo   GAME ACCOUNT REGISTRAR TOOL
echo   Game Account Auto Registration Tool
echo ============================================
echo.

REM Check if GameAccountRegistrar.exe exists
if not exist "%~dp0GameAccountRegistrar.exe" (
    echo ERROR: GameAccountRegistrar.exe not found!
    echo Please ensure the executable is in the same directory as this batch file.
    pause
    exit /b 1
)

REM Run the executable
"%~dp0GameAccountRegistrar.exe"

pause
