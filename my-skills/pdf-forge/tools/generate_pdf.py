#!/usr/bin/env python3
"""
PDF Forge - Generate beautiful, brand-aware PDFs from markdown.

Uses WeasyPrint to convert HTML/CSS to PDF with proper font embedding,
smart page breaks, and brand-specific styling.

Usage:
    python3 generate_pdf.py --input "/path/to/source.md" --brand "ai-powerhouse"
    python3 generate_pdf.py --input "/path/to/source.md" --output "~/Downloads/Report.pdf"
    python3 generate_pdf.py --input "/path/to/source.md" --template "guide"
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime

import yaml
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Add tools directory to path for imports
TOOLS_DIR = Path(__file__).parent
SKILL_DIR = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))

from markdown_parser import parse_markdown_file, detect_template, generate_slug


def load_brand(brand_name: str) -> dict:
    """Load brand configuration from YAML file."""
    brand_dir = SKILL_DIR / 'brands' / brand_name
    brand_file = brand_dir / 'brand.yaml'

    if not brand_file.exists():
        raise FileNotFoundError(f"Brand '{brand_name}' not found at {brand_file}")

    with open(brand_file, 'r') as f:
        brand = yaml.safe_load(f)

    # Add computed paths
    brand['_dir'] = brand_dir
    brand['_styles_path'] = brand_dir / 'styles.css'
    brand['_fonts_dir'] = brand_dir / 'fonts'

    # Logo path if configured
    if brand.get('logo', {}).get('file'):
        logo_path = brand_dir / brand['logo']['file']
        if logo_path.exists():
            brand['_logo_path'] = logo_path
        else:
            brand['_logo_path'] = None
    else:
        brand['_logo_path'] = None

    return brand


def check_brand_fonts(brand: dict) -> list:
    """Check if font files referenced in brand CSS exist on disk.

    Parses @font-face src: url('fonts/...') declarations from the brand's
    styles.css and verifies each file exists. Returns list of missing paths.
    """
    styles_path = brand['_styles_path']
    brand_dir = brand['_dir']
    missing = []

    if not styles_path.exists():
        return missing

    css_content = styles_path.read_text()

    # Extract font file paths from @font-face url() declarations
    font_urls = re.findall(r"url\(['\"]?(fonts/[^'\")\s]+)['\"]?\)", css_content)

    for font_rel in font_urls:
        font_path = brand_dir / font_rel
        if not font_path.exists():
            missing.append(str(font_path))

    return missing


def get_available_brands() -> list:
    """List available brand names."""
    brands_dir = SKILL_DIR / 'brands'
    return [d.name for d in brands_dir.iterdir() if d.is_dir() and (d / 'brand.yaml').exists()]


def generate_pdf(
    input_path: str,
    output_path: str = None,
    brand_name: str = 'ai-powerhouse',
    template_name: str = None,
    cover_image: str = None,
    verbose: bool = False
) -> Path:
    """
    Generate a PDF from a markdown file.

    Args:
        input_path: Path to source markdown file
        output_path: Path for output PDF (optional, auto-generated if not provided)
        brand_name: Brand to use for styling
        template_name: Template to use (auto-detected if not provided)
        verbose: Print progress messages

    Returns:
        Path to generated PDF
    """
    input_path = Path(input_path).expanduser().resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if verbose:
        print(f"Parsing markdown: {input_path}")

    # Parse markdown
    parsed = parse_markdown_file(str(input_path))

    # Auto-detect template if not specified
    if not template_name:
        template_name = detect_template(input_path.read_text(), str(input_path))
        if verbose:
            print(f"Auto-detected template: {template_name}")

    # Load brand
    if verbose:
        print(f"Loading brand: {brand_name}")
    brand = load_brand(brand_name)

    # Check for missing font files
    missing_fonts = check_brand_fonts(brand)
    if missing_fonts:
        for font_path in missing_fonts:
            print(f"WARNING: Font file not found: {font_path}. PDF will use fallback fonts.", file=sys.stderr)
        download_script = SKILL_DIR / 'scripts' / 'download-fonts.sh'
        if download_script.exists():
            print(f"Run: bash {download_script} {brand_name}", file=sys.stderr)

    # Generate output path if not provided
    if not output_path:
        title_slug = (parsed['title'] or 'document').replace(' ', '-').replace('/', '-')[:50]
        date_str = datetime.now().strftime('%Y%m%d')
        output_path = Path(f"~/Downloads/{title_slug}-{date_str}.pdf").expanduser()
    else:
        output_path = Path(output_path).expanduser()

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"Output: {output_path}")

    # Set up Jinja2 environment
    templates_dir = SKILL_DIR / 'templates'
    env = Environment(loader=FileSystemLoader(str(templates_dir)))

    # Load template
    template_file = f"{template_name}.html"
    template = env.get_template(template_file)

    # Auto-show TOC when document has 3+ H2 sections
    show_toc = parsed.get('h2_count', 0) >= 3

    if verbose:
        print(f"H2 sections: {parsed.get('h2_count', 0)}, show TOC: {show_toc}")

    # Prepare template context
    context = {
        # Parsed content
        **parsed,

        # TOC control
        'show_toc': show_toc,

        # Brand info
        'brand_name': brand['name'],

        # Paths for CSS - use file:// URLs for WeasyPrint
        'print_styles_path': f"file://{templates_dir / 'print-styles.css'}",
        'brand_styles_path': f"file://{brand['_styles_path']}",

        # Logo
        'logo_path': f"file://{brand['_logo_path']}" if brand['_logo_path'] else None,
        'logo_width': brand.get('logo', {}).get('width', '120px'),
        'logo_position': brand.get('logo', {}).get('position', 'header'),

        # Additional context
        'generated_date': datetime.now().strftime('%Y-%m-%d'),

        # Cover image (workshop-guide template)
        'cover_image': f"file://{Path(cover_image).expanduser().resolve()}" if cover_image else None,
    }

    if verbose:
        print(f"Rendering template: {template_name}")

    # Render HTML
    html_content = template.render(**context)

    # Configure fonts
    font_config = FontConfiguration()

    if verbose:
        print("Generating PDF with WeasyPrint...")

    # Generate PDF
    html = HTML(string=html_content, base_url=str(SKILL_DIR))
    html.write_pdf(
        str(output_path),
        font_config=font_config
    )

    if verbose:
        print(f"PDF generated successfully: {output_path}")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Generate beautiful, brand-aware PDFs from markdown.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate_pdf.py --input "~/Documents/report.md"
  python3 generate_pdf.py --input "report.md" --brand ai-powerhouse
  python3 generate_pdf.py --input "guide.md" --template guide --output "~/Downloads/Guide.pdf"
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to source markdown file'
    )

    parser.add_argument(
        '--output', '-o',
        help='Path for output PDF (auto-generated if not provided)'
    )

    parser.add_argument(
        '--brand', '-b',
        default='ai-powerhouse',
        help=f'Brand to use (available: {", ".join(get_available_brands())})'
    )

    parser.add_argument(
        '--template', '-t',
        help='Template to use (auto-detected if not provided: research-report, guide)'
    )

    parser.add_argument(
        '--cover-image',
        help='Path to hero image for cover page (workshop-guide template)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print progress messages'
    )

    parser.add_argument(
        '--list-brands',
        action='store_true',
        help='List available brands and exit'
    )

    args = parser.parse_args()

    if args.list_brands:
        print("Available brands:")
        for brand in get_available_brands():
            print(f"  - {brand}")
        return

    try:
        output_path = generate_pdf(
            input_path=args.input,
            output_path=args.output,
            brand_name=args.brand,
            template_name=args.template,
            cover_image=args.cover_image,
            verbose=args.verbose
        )
        print(f"PDF created: {output_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error generating PDF: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
