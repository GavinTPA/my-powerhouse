#!/bin/bash
# PDF Forge Setup — Mac
# This installs everything PDF Forge needs to turn your markdown into beautiful PDFs.

set -e

echo ""
echo "=== PDF Forge Setup ==="
echo ""

# Step 1: Check we're in the right place
if [ ! -f "my-skills/pdf-forge/tools/generate_pdf.py" ]; then
    echo "Please run this from your Powerhouse folder."
    echo "  cd ~/Documents/my-powerhouse"
    echo "  bash my-skills/pdf-forge/scripts/setup.sh"
    exit 1
fi

echo "Step 1: Checking Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "  Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "  Homebrew found."
fi

echo ""
echo "Step 2: Installing the PDF engine dependencies..."
echo "  (These are the libraries that make PDF generation possible)"
brew install pango cairo gdk-pixbuf libffi 2>/dev/null || true
echo "  Done."

echo ""
echo "Step 3: Creating a workspace for PDF Forge..."
echo "  (This keeps PDF Forge's tools separate from everything else)"

PYTHON=""
for ver in python3.12 python3.13 python3.14 python3; do
    if command -v $ver &> /dev/null; then
        PYTHON=$ver
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "  Python 3 not found. Install it with: brew install python@3.12"
    exit 1
fi

echo "  Using $PYTHON"
$PYTHON -m venv my-skills/pdf-forge/.venv
echo "  Workspace created."

echo ""
echo "Step 4: Installing PDF Forge tools..."
my-skills/pdf-forge/.venv/bin/pip install -q -r my-skills/pdf-forge/tools/requirements.txt
echo "  Done."

echo ""
echo "Step 5: Testing the installation..."
my-skills/pdf-forge/.venv/bin/python -c "import weasyprint; print('  PDF engine is working.')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo ""
    echo "=== Setup Complete ==="
    echo ""
    echo "PDF Forge is ready. Try saying:"
    echo '  "Create a test PDF"'
    echo ""
    echo "To create your own brand, copy the template:"
    echo "  cp -r my-skills/pdf-forge/brands/my-brand-template my-skills/pdf-forge/brands/my-brand"
    echo "  Then edit my-skills/pdf-forge/brands/my-brand/brand.yaml"
    echo ""
else
    echo ""
    echo "Something went wrong with the installation."
    echo "Ask your Powerhouse: 'Help me troubleshoot PDF Forge setup'"
    exit 1
fi
