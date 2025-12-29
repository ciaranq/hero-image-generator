# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hero Image Generator is a Python package that generates professional 1200x630px Open Graph hero images with theme-based visual systems. It automatically detects themes from tags and renders theme-specific visual elements (AI/ML networks, SEO charts, automation gears, strategy diagrams).

## Development Commands

### Installation
```bash
# Development install with test dependencies
pip install -e ".[dev]"

# Production install
pip install -e .
```

### Testing
```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=hero_image_generator --cov-report=html

# Run specific test file
pytest tests/test_theme_detector.py -v
```

### Interactive Wizard
```bash
# Launch wizard (no arguments)
python -m hero_image_generator

# Wizard will prompt for inputs and show live preview
# Config saved to ~/.config/hero-image-generator/last-used.json
```

### Generate Images
```bash
# Single image
python -m hero_image_generator --title "My Title" --tags ai,ml --year 2025 --output test.png

# Preview all themes
python -m hero_image_generator --preview

# Batch from metadata JSON
python -m hero_image_generator --metadata content.json

# Custom output directory
python -m hero_image_generator --preview --output-dir ./my-images
```

## Architecture

### Theme-Based Pipeline (image_generator.py:90-194)

The generator follows a 7-step pipeline in `HeroImageGenerator.generate()`:

1. **Theme Detection** (`theme_detector.py`) - Tags → Theme object with accent colors
2. **Gradient Background** - Creates base gradient (default blue→purple or theme-specific)
3. **Grid Overlay** - Adds subtle white grid pattern (26 alpha, 100px spacing)
4. **Visual Rendering** (`visual_renderer.py`) - Routes to theme-specific renderer methods
5. **Subtitle Generation** (`subtitle_generator.py`) - Creates descriptive subtitle from tags
6. **Text Layers** - Renders title (left-aligned), subtitle, year badge (top-right)
7. **Save** - Outputs to `public/images/` (configurable via `output_dir`)

### Theme Detection System (theme_detector.py:41-64)

Theme selection uses **first-match** logic across 4 pre-defined themes:
- **ai_ml**: Purple (139,92,246) - Connected node networks
- **seo_analytics**: Green (34,197,94) - Rising charts and graphs
- **automation**: Orange (249,115,22) - Interlocking gears
- **strategy**: Cyan (6,182,212) - Hierarchical org charts
- **default**: Purple - Simple geometric circles

**Important**: If tags match multiple themes, the first match in iteration order wins. Tags are case-insensitive.

### Visual Rendering (visual_renderer.py:10-243)

Each theme has a dedicated `_render_<theme>()` method that draws on the right side of the image (x > 700) to avoid text collision. Visual elements use PIL's RGBA mode with transparency for layered effects:
- Node networks with connection lines (AI/ML)
- Bar charts with trend lines (SEO)
- Circuit-style gear connections (Automation)
- Hierarchical box diagrams (Strategy)

All renderers receive the base image and Theme object, returning the modified image.

### Font Fallback Strategy (image_generator.py:120-135)

Font loading tries 3 levels:
1. macOS system fonts (`/System/Library/Fonts/Helvetica.ttc`)
2. Linux fonts (`/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`)
3. PIL default font (fallback, lower quality)

When adding font customization, maintain this fallback chain.

## Package Exports

Public API via `__init__.py`:
- `HeroImageGenerator` - Main generator class
- `ThemeDetector` - Tag → Theme mapper
- `SubtitleGenerator` - Tag → subtitle text
- `VisualRenderer` - Theme → visual elements
- `Theme` - Dataclass (name, accent_color, gradient colors)

## Key Constraints

- **Image dimensions**: Fixed 1200x630 (Open Graph standard)
- **Text positioning**: Title at y=200, max width 700px to avoid visual overlap
- **Output format**: PNG with optimization enabled
- **Python version**: 3.8+ required
- **Dependencies**: Pillow 10.0.0+ (only runtime dependency)

## Extending Themes

To add new themes:

1. Add theme mapping to `ThemeDetector.theme_map` (theme_detector.py:16-34)
2. Add renderer method to `VisualRenderer` (visual_renderer.py)
3. Update router in `VisualRenderer.render()` (visual_renderer.py:21-31)
4. Add preview sample to `generate_preview_samples()` (cli.py:99-155)

Example theme structure:
```python
'fintech': {
    'tags': ['fintech', 'finance', 'banking'],
    'accent': (16, 185, 129)  # RGB tuple
}
```

## CLI Entry Points

Package is executable via:
- `python -m hero_image_generator` (module execution via `__main__.py`)
- `hero-image-generator` (console script from setup.py:38-42)

Both invoke `cli.main()` which supports three modes: single image, batch metadata, or preview.
