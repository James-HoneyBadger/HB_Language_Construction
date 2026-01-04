@echo off
REM Run CodeEx - ParserCraft Execution Environment (Windows)
REM This script initializes the virtual environment and launches the CodeEx IDE

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"

echo.
echo 🚀 CodeEx - ParserCraft Execution Environment
echo ==================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python 3 is not installed. Please install Python 3.9 or later.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo ✓ Python %PYTHON_VERSION% found
echo.

REM Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo 📦 Creating virtual environment...
    python -m venv "%VENV_DIR%"
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

echo.

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
echo ✓ Virtual environment activated
echo.

REM Install/upgrade pip
echo 📥 Updating pip...
python -m pip install --quiet --upgrade pip setuptools wheel
echo ✓ pip updated
echo.

REM Install the package in development mode
echo 📚 Installing ParserCraft package...
cd /d "%SCRIPT_DIR%"
python -m pip install --quiet -e ".[ide]"
echo ✓ ParserCraft package installed
echo.

REM Verify tkinter is available
echo 🔍 Checking dependencies...
python -c "import tkinter; print('✓ tkinter available')" || (
    echo ⚠️  tkinter not found. Tkinter is usually included with Python on Windows.
    echo ⚠️  If missing, reinstall Python and check "tcl/tk and IDLE" during installation.
    pause
    exit /b 1
)
echo.

REM Launch the IDE
echo 🎨 Launching CodeEx IDE...
echo ==================================================
echo.

python "%SCRIPT_DIR%src\codex\codex.py"

echo.
echo ==================================================
echo ✓ CodeEx IDE closed
pause
