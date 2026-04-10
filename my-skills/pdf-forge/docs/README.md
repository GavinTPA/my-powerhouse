# PDF Forge — Technical Reference

## Architecture

```
pdf-forge/
├── SKILL.md              # Instructions for Claude
├── tools/
│   ├── generate_pdf.py   # Main PDF generator (WeasyPrint)
│   ├── markdown_parser.py # Extracts structure from markdown
│   └── requirements.txt  # Python dependencies
├── templates/
│   ├── base.html         # Shared HTML structure
│   ├── research-report.html # Cover, TOC, sections, sources
│   ├── guide.html        # Clean flowing documents
│   ├── letter.html       # Gary Halbert legal pad style
│   ├── workshop-guide.html # Workshop materials with cover image
│   └── print-styles.css  # Smart page break rules
├── brands/
│   ├── ai-powerhouse/    # Example brand (Burnt Orange, Clash Display)
│   └── my-brand-template/ # Starting point for your own brand
├── scripts/
│   ├── setup.sh          # Mac setup
│   └── setup.ps1         # Windows setup
└── docs/
    ├── README.md         # This file
    ├── GUIDE.md          # Business-friendly guide
    └── ROADMAP.md        # Version history
```

## Dependencies

- **Python 3.12+** with virtual environment
- **WeasyPrint 60.0+** (HTML/CSS to PDF engine)
- **Jinja2** (template rendering)
- **PyYAML** (brand config loading)
- **Markdown** (markdown to HTML conversion)

### System dependencies (Mac only)

```
brew install pango cairo gdk-pixbuf libffi
```

Windows: WeasyPrint's pip wheel bundles GTK automatically.

## CLI Usage

```bash
.venv/bin/python tools/generate_pdf.py \
  --input "source.md" \
  --output "~/Downloads/output.pdf" \
  --brand "ai-powerhouse" \
  --template "research-report" \
  --verbose
```

## Adding a New Brand

1. Copy `brands/my-brand-template/` to `brands/your-name/`
2. Edit `brand.yaml` with your colours, fonts, logo
3. Add font files to `fonts/` (optional — system fonts work too)
4. Edit `styles.css` to register custom fonts (see examples in file)
5. Test: `--brand your-name`

## Template Auto-Detection

- Content contains "Executive Summary" or "Sources" → `research-report`
- Filename contains "research" → `research-report`
- Default → `guide`

## Known Limitations

- YAML frontmatter in markdown files renders as visible text. Strip it before generating, or create a temp copy without frontmatter.
- Very long code blocks may overflow page width. Use shorter lines in code blocks.
