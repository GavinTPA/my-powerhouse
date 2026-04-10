#!/bin/bash
# YouTube Processor — One-Time Setup
# Run this once. After that, the skill works automatically.

set -e

# Find the skill directory (one level up from scripts/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo ""
echo "YouTube Processor Setup"
echo "======================="
echo ""

# Check Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is needed but not installed."
    echo ""
    echo "To install it:"
    echo "  Mac:     brew install python3"
    echo "  Windows: Download from python.org"
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Found Python $PYTHON_VERSION"

# Create a clean environment in the skill folder
echo "Creating environment..."
cd "$SKILL_DIR"
python3 -m venv .venv

# Install the transcript extraction tool (free, no API key needed)
echo "Installing transcript tool..."
.venv/bin/pip install -q youtube-transcript-api

echo ""
echo "Setup complete!"
echo ""
echo "You can now use the YouTube Processor skill."
echo "Try saying: 'Summarize this video: [paste any YouTube link]'"
echo ""
