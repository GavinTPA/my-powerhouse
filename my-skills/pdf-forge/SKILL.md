---
name: pdf-forge
description: Generates beautiful, brand-aware PDFs from markdown using WeasyPrint. Use when "create a PDF", "make a PDF", "PDF forge", "generate PDF from markdown", "branded PDF".
allowed-tools: Read, Write, Edit, Glob, Bash
---

# PDF Forge

## What This Does

Transforms markdown content into professionally designed PDFs. Your colours, your fonts, your logo — every time.

## Setup Required

Before first use, run the setup script for your platform. This installs the PDF engine and creates your workspace.

**Mac:**
```bash
bash my-skills/pdf-forge/scripts/setup.sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File my-skills\pdf-forge\scripts\setup.ps1
```

If you haven't run setup yet and the user asks to create a PDF, guide them through setup first.

## Brands Available

| Brand | When to Use |
|-------|-------------|
| `ai-powerhouse` | Example brand (Burnt Orange, Clash Display). Use as reference. |
| `my-brand-template` | Starting point for your own brand. Copy and customise. |

If the user has created their own brand folder in `brands/`, use that.

## Document Types

### Research Reports
Full-featured reports with cover page, table of contents, executive summary, branded tables, and sources.

### Guides
General purpose documents with clean typography, section headers, code blocks, and callout boxes.

### Letters
Gary Halbert-style letters with legal pad aesthetic, Courier font, and yellow background.

### Workshop Guides
Workshop materials with cover image support and structured content blocks.

## Instructions

### Step 1: Identify Source and Brand

Read the markdown file. Determine:
- Document type (research report, guide, letter, workshop guide)
- Desired brand (check what brands exist in `my-skills/pdf-forge/brands/`)

### Step 2: Generate the PDF

```bash
my-skills/pdf-forge/.venv/bin/python my-skills/pdf-forge/tools/generate_pdf.py \
  --input "/path/to/source.md" \
  --output "~/Downloads/Output.pdf" \
  --brand "ai-powerhouse" \
  --template "research-report"
```

**Arguments:**
- `--input` (required): Path to source markdown file
- `--output` (optional): Output path (defaults to ~/Downloads/<title>.pdf)
- `--brand` (optional): Brand to use (default: ai-powerhouse)
- `--template` (optional): Template type (auto-detected if omitted)
- `--cover-image` (optional): Path to cover image for workshop guides
- `--verbose` (optional): Show detailed processing info

### Step 3: Review Before Showing

After generating, review the PDF yourself before presenting it to the user:
- Check for text running off the page
- Verify brand colours and fonts are correct
- Check page breaks aren't splitting tables or headings
- Verify the cover page looks professional

This is the Mirror Pass — catch issues before the user sees them.

### Step 4: Open for Review

```bash
open "~/Downloads/Output.pdf"
```

On Windows, use `start` instead of `open`.

## Create Your Own Brand

1. Copy the template:
```bash
cp -r my-skills/pdf-forge/brands/my-brand-template my-skills/pdf-forge/brands/my-brand
```

2. Edit `my-skills/pdf-forge/brands/my-brand/brand.yaml` — fill in your colours, fonts, and logo path

3. If you have custom fonts (OTF or TTF files), drop them in `my-skills/pdf-forge/brands/my-brand/fonts/`

4. If you don't have custom fonts, use system fonts like Arial, Georgia, or Trebuchet MS — no font files needed

5. Test it:
```bash
my-skills/pdf-forge/.venv/bin/python my-skills/pdf-forge/tools/generate_pdf.py \
  --input "test.md" --brand "my-brand"
```

Think of the brand config like a style guide you'd hand a designer. Set it up once, and every document comes out consistent.

## Smart Page Breaks

The system automatically prevents:
- Tables splitting across pages
- Headings orphaned at bottom of page
- Fewer than 3 lines at top/bottom of page
- Code blocks splitting

## Brand Detection

- "Create a PDF" → uses default brand (first one found, or ai-powerhouse)
- "Create a PDF using my-brand" → uses specified brand
- "Create a PDF with my colours" → check what brands exist, use the user's custom brand

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Use specified brand | Switch brands mid-document | Modify brand YAML without permission |
| Apply smart page breaks | Add new template types | Skip font embedding |
| Auto-detect template | Override user's brand choice | Generate without reviewing source |
| Run the Mirror Pass before presenting | | |

## Output Location

Default: `~/Downloads/<Document Title>.pdf`
