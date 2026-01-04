#!/bin/bash
# Run CodeEx - ParserCraft Execution Environment
# This script initializes the virtual environment and launches the CodeEx IDE

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_VERSION="3.9"

echo "🚀 CodeEx - ParserCraft Execution Environment"
echo "=================================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3.9 or later."
    exit 1
fi

PYTHON_VERSION_INSTALLED=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION_INSTALLED found"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo "✓ Virtual environment activated"
echo ""

# Install/upgrade pip
echo "📥 Updating pip..."
pip install --quiet --upgrade pip setuptools wheel
echo "✓ pip updated"
echo ""

# Install the package in development mode
echo "📚 Installing ParserCraft package..."
cd "$SCRIPT_DIR"
pip install --quiet -e ".[ide]"
echo "✓ ParserCraft package installed"
echo ""

# Verify tkinter is available
echo "🔍 Checking dependencies..."
python3 -c "import tkinter; print('✓ tkinter available')" || {
    echo "⚠️  tkinter not found. On Ubuntu/Debian, run: sudo apt-get install python3-tk"
    echo "⚠️  On macOS with Homebrew: brew install python-tk"
    exit 1
}
echo ""

# Launch the IDE
echo "🎨 Launching CodeEx IDE..."
echo "=================================================="
echo ""

python3 "$SCRIPT_DIR/src/codex/codex.py"

echo ""
echo "=================================================="
echo "✓ CodeEx IDE closed"
