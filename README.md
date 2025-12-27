# Hero Image Generator

Professional hero image generator with theme-based visual systems. Perfect for blog posts, social media, and marketing content.

## Features

- **Theme-Based Visual Systems**: Automatically detects themes from tags and generates relevant visuals
- **4 Pre-Built Themes**: AI/ML, SEO/Analytics, Automation, and Strategy
- **Customizable Branding**: Easy to configure colors, fonts, and visual elements
- **Single or Batch Generation**: Generate one image or process hundreds from metadata
- **Preview Mode**: See samples of each theme before bulk generation
- **Professional Quality**: 1200x630px Open Graph optimized images

## Installation

```bash
pip install -e .
```

Or for development:

```bash
pip install -e ".[dev]"
```

## Quick Start

### Generate a Single Image

```bash
python -m hero_image_generator \
  --title "AI Agent Orchestration Platform" \
  --tags ai,agent,platform \
  --year 2025 \
  --output my-hero.png
```

### Generate Preview Samples

```bash
python -m hero_image_generator --preview
```

This creates 5 sample images (one for each theme + default) in `public/images/`:
- `preview-ai-ml.png`
- `preview-seo.png`
- `preview-automation.png`
- `preview-strategy.png`
- `preview-default.png`

### Batch Generation from Metadata

Create a JSON file with your content metadata:

```json
[
  {
    "title": "Building AI Agents in 2025",
    "tags": ["ai", "agent", "development"],
    "year": 2025,
    "filename": "ai-agents-2025-hero.png"
  },
  {
    "title": "SEO Best Practices Guide",
    "tags": ["seo", "optimization"],
    "year": 2025,
    "filename": "seo-guide-hero.png"
  }
]
```

Then generate:

```bash
python -m hero_image_generator --metadata content.json
```

### Custom Output Directory

```bash
python -m hero_image_generator --preview --output-dir ./my-images
```

## Themes

The generator automatically selects themes based on your tags:

### AI/ML Theme
**Tags**: `ai`, `ml`, `llm`, `agent`, `platform`, `orchestration`
**Visual Elements**: Connected node networks, central hub with satellites, connection lines
**Accent Color**: Purple `(139, 92, 246)`

### SEO/Analytics Theme
**Tags**: `seo`, `analytics`, `metrics`, `content`, `optimization`
**Visual Elements**: Rising graph lines, bar charts, analytics dashboard elements
**Accent Color**: Green `(34, 197, 94)`

### Automation Theme
**Tags**: `automation`, `api`, `integration`, `technical`, `development`
**Visual Elements**: Interlocking gears, circuit patterns, flow diagrams
**Accent Color**: Orange `(249, 115, 22)`

### Strategy Theme
**Tags**: `strategy`, `business`, `enterprise`, `consulting`
**Visual Elements**: Hierarchical structures, process flows, mind map nodes
**Accent Color**: Cyan `(6, 182, 212)`

### Default Theme
**Used when**: No matching tags found
**Visual Elements**: Geometric patterns
**Accent Color**: Purple `(139, 92, 246)`

## Programmatic Usage

```python
from hero_image_generator import HeroImageGenerator

# Create generator
generator = HeroImageGenerator()

# Generate single image
output_path = generator.generate(
    title="My Blog Post Title",
    tags=["ai", "ml", "platform"],
    year=2025,
    output_filename="my-hero.png"
)

print(f"Generated: {output_path}")
```

## Customization

### Brand Configuration

Create a `brand_config.py` file:

```python
from hero_image_generator import HeroImageGenerator

class MyBrandGenerator(HeroImageGenerator):
    def __init__(self):
        super().__init__()
        # Override colors
        self.bg_color_start = (30, 58, 138)   # Your brand blue
        self.bg_color_end = (59, 130, 246)    # Your lighter blue
        self.text_color = (255, 255, 255)     # White
        self.badge_color = (34, 197, 94)      # Green

# Use custom generator
generator = MyBrandGenerator()
```

### Custom Themes

```python
from hero_image_generator import ThemeDetector, Theme

class MyThemeDetector(ThemeDetector):
    def __init__(self):
        super().__init__()
        # Add custom theme
        self.theme_map['fintech'] = {
            'tags': ['fintech', 'finance', 'banking', 'payments'],
            'accent': (16, 185, 129)  # Custom green
        }
```

## Directory Structure

```
hero-image-generator/
├── hero_image_generator/       # Main package
│   ├── __init__.py            # Package exports
│   ├── cli.py                 # Command-line interface
│   ├── image_generator.py     # Main generator class
│   ├── theme_detector.py      # Theme detection logic
│   ├── subtitle_generator.py  # Subtitle generation
│   └── visual_renderer.py     # Visual element rendering
├── tests/                     # Test suite
│   ├── test_theme_detector.py
│   ├── test_subtitle_generator.py
│   └── test_visual_renderer.py
├── examples/                  # Example scripts
├── docs/                      # Additional documentation
├── requirements.txt           # Dependencies
├── setup.py                   # Package configuration
└── README.md                  # This file
```

## Requirements

- Python 3.8+
- Pillow 10.0.0+

## Development

### Run Tests

```bash
pytest tests/
```

### Run Tests with Coverage

```bash
pytest tests/ --cov=hero_image_generator --cov-report=html
```

### Generate Preview Images

```bash
python -m hero_image_generator --preview
```

## CLI Reference

```
usage: python -m hero_image_generator [-h] [--title TITLE] [--tags TAGS]
                                       [--year YEAR] [--output OUTPUT]
                                       [--metadata METADATA]
                                       [--filter-year FILTER_YEAR]
                                       [--dry-run] [--preview]
                                       [--output-dir OUTPUT_DIR]

Generate professional hero images with theme-based visual systems

optional arguments:
  -h, --help            show this help message and exit
  --title TITLE         Image title text
  --tags TAGS           Comma-separated tags for theme detection
  --year YEAR           Year for badge (default: 2025)
  --output OUTPUT       Output filename (e.g., my-hero.png)
  --metadata METADATA   Generate from JSON metadata file
  --filter-year FILTER_YEAR
                        Only generate images for specific year
  --dry-run             Show what would be generated without creating files
  --preview             Generate preview samples for each theme
  --output-dir OUTPUT_DIR
                        Output directory (default: public/images)
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Credits

Created by [IntelliAgent](https://intelliagent.com.au) for generating professional hero images for blog posts and marketing content.
