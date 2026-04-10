# PDF Forge Setup — Windows
# This installs everything PDF Forge needs to turn your markdown into beautiful PDFs.

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== PDF Forge Setup ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check we're in the right place
if (-not (Test-Path "my-skills\pdf-forge\tools\generate_pdf.py")) {
    Write-Host "Please run this from your Powerhouse folder." -ForegroundColor Red
    Write-Host "  cd ~\Documents\my-powerhouse"
    Write-Host '  powershell -ExecutionPolicy Bypass -File my-skills\pdf-forge\scripts\setup.ps1'
    exit 1
}

# Step 2: Find Python
Write-Host "Step 1: Checking for Python..."
$python = $null
foreach ($ver in @("python3", "python")) {
    try {
        $result = & $ver --version 2>&1
        if ($result -match "Python 3\.") {
            $python = $ver
            Write-Host "  Found: $result"
            break
        }
    } catch { }
}

if (-not $python) {
    Write-Host "  Python 3 not found." -ForegroundColor Red
    Write-Host "  Install Python from: https://www.python.org/downloads/"
    Write-Host "  Make sure to check 'Add Python to PATH' during installation."
    exit 1
}

# Step 3: Create workspace
Write-Host ""
Write-Host "Step 2: Creating a workspace for PDF Forge..."
Write-Host "  (This keeps PDF Forge's tools separate from everything else)"
& $python -m venv my-skills\pdf-forge\.venv
Write-Host "  Workspace created."

# Step 4: Install dependencies
Write-Host ""
Write-Host "Step 3: Installing PDF Forge tools..."
Write-Host "  (This includes the PDF engine — may take a minute)"
& my-skills\pdf-forge\.venv\Scripts\pip install -q -r my-skills\pdf-forge\tools\requirements.txt
Write-Host "  Done."

# Step 4b: Check for GTK3 (required by the PDF engine on Windows)
Write-Host ""
Write-Host "Step 3b: Checking PDF engine dependencies..."
try {
    & my-skills\pdf-forge\.venv\Scripts\python -c "import weasyprint" 2>$null
    Write-Host "  PDF engine dependencies found."
} catch {
    Write-Host ""
    Write-Host "  The PDF engine needs an additional component on Windows (GTK3)." -ForegroundColor Yellow
    Write-Host "  This is a one-time install. Trying automatic installation..."
    Write-Host ""
    try {
        # Try installing via pip with the Windows extras
        & my-skills\pdf-forge\.venv\Scripts\pip install -q weasyprint[windows] 2>$null
        Write-Host "  Installed via pip extras."
    } catch {
        Write-Host "  Automatic installation didn't work." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  You'll need to install GTK3 manually:" -ForegroundColor Yellow
        Write-Host "  1. Download the GTK3 installer from: https://github.com/nicholasgasior/gvsbuild/releases" -ForegroundColor Yellow
        Write-Host "  2. Run the installer" -ForegroundColor Yellow
        Write-Host "  3. Restart your terminal and run this setup again" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Or ask your Powerhouse: 'Help me install GTK3 for PDF Forge on Windows'" -ForegroundColor Yellow
    }
}

# Step 5: Test
Write-Host ""
Write-Host "Step 4: Testing the installation..."
try {
    & my-skills\pdf-forge\.venv\Scripts\python -c "import weasyprint; print('  PDF engine is working.')"
    Write-Host ""
    Write-Host "=== Setup Complete ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "PDF Forge is ready. Try saying:"
    Write-Host '  "Create a test PDF"'
    Write-Host ""
    Write-Host "To create your own brand, copy the template:"
    Write-Host '  Copy-Item -Recurse my-skills\pdf-forge\brands\my-brand-template my-skills\pdf-forge\brands\my-brand'
    Write-Host '  Then edit my-skills\pdf-forge\brands\my-brand\brand.yaml'
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "Something went wrong with the installation." -ForegroundColor Red
    Write-Host "Ask your Powerhouse: 'Help me troubleshoot PDF Forge setup'"
    exit 1
}
