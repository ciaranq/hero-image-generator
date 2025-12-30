# Hero Image Generator

Professional hero image generator with theme-based visual systems. Perfect for blog posts, social media, and marketing content.

## Features

- **Dual Generation Modes**:
  - **Programmatic Mode**: Theme-based visual systems with 4 pre-built themes (AI/ML, SEO/Analytics, Automation, Strategy)
  - **AI Mode**: Generate unique hero images using Flux (Replicate) or Gemini/Imagen (Vertex AI) models
- **AI-Powered Image Generation**:
  - Flux Pro ($0.055), Flux Dev ($0.020), Flux Schnell ($0.010)
  - Imagen ($0.020) via Google Vertex AI
  - Optional quality validation with Gemini Vision
  - Built-in cost tracking and logging
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

### Interactive Wizard (Recommended)

Run without arguments to launch the interactive wizard:

```bash
python -m hero_image_generator
```

The wizard will:
1. **Choose mode**: Programmatic themes or AI generation
2. **Collect inputs**: Title/tags (programmatic) or prompt (AI)
3. **Generate and preview** the image
4. Let you refine and regenerate until satisfied
5. Save your preferences for next time

Features:
- Live preview in your default image viewer
- Iterative refinement (change title, colors, fonts, or prompt)
- Auto-saved preferences between sessions
- Color presets with custom hex/RGB support
- AI mode with model selection (Flux Pro/Dev/Schnell, Imagen)

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

## AI Mode (v2.0.0+)

### Setup

AI mode requires API credentials. See [Setup Documentation](docs/setup/) for detailed guides:

- **Flux models** (Replicate): [docs/setup/replicate_setup.md](docs/setup/replicate_setup.md)
- **Imagen/Gemini** (Google Vertex AI): [docs/setup/gcp_setup.md](docs/setup/gcp_setup.md)
- **Testing**: [docs/setup/testing_setup.md](docs/setup/testing_setup.md)

Create a `.env` file in the project root:

```bash
# Replicate API (for Flux models)
REPLICATE_API_TOKEN=r8_YourTokenHere

# Google Cloud Platform (for Imagen/Gemini - optional)
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Model Selection
DEFAULT_MODEL=flux-pro
FALLBACK_MODEL=flux-dev

# Quality Validation (requires GCP)
ENABLE_QUALITY_CHECK=false
MIN_QUALITY_SCORE=0.6

# Cost Tracking
LOG_COSTS=true
COST_LOG_FILE=generation_costs.log
```

### Generate with AI

#### CLI Mode

```bash
# Flux Schnell (fastest, cheapest)
python -m hero_image_generator --ai \
  --prompt "Epic hero image for AI agents blog post" \
  --model flux-schnell \
  --size medium \
  --output ai-agents-hero.png

# Flux Pro (highest quality)
python -m hero_image_generator --ai \
  --prompt "Professional tech conference hero image" \
  --model flux-pro \
  --size large

# Imagen (Google Vertex AI)
python -m hero_image_generator --ai \
  --prompt "Modern software development workspace" \
  --model imagen \
  --validate  # Optional quality check with Gemini Vision
```

#### Model Options

| Model | Provider | Cost | Quality | Speed | Use Case |
|-------|----------|------|---------|-------|----------|
| `flux-schnell` | Replicate | $0.010 | Good | ~2s | Quick drafts, testing |
| `flux-dev` | Replicate | $0.020 | Better | ~4s | Production use |
| `flux-pro` | Replicate | $0.055 | Best | ~6s | Premium content |
| `imagen` | Vertex AI | $0.020 | Excellent | ~5s | Google Cloud users |

#### Size Options

- `small`: 800x450
- `medium`: 1920x1080 (default)
- `large`: 2560x1440

### Quality Validation

Enable Gemini Vision quality checking (requires GCP setup):

```bash
python -m hero_image_generator --ai \
  --prompt "Your prompt here" \
  --model flux-pro \
  --validate
```

Quality validation costs an additional $0.001 per generation and provides:
- Overall quality score (0.0-1.0)
- Detailed feedback on composition, aesthetics, technical quality
- Pass/fail status based on `MIN_QUALITY_SCORE` threshold

### Cost Tracking

All AI generations are automatically logged to `generation_costs.log`:

```
2025-12-30 14:32:15 - Model: flux-pro, Cost: $0.055, Total Session: $0.055
2025-12-30 14:35:22 - Model: flux-schnell, Cost: $0.010, Total Session: $0.065
2025-12-30 14:38:45 - Validation Cost: $0.001, Total Session: $0.066
```

### Programmatic Usage (AI Mode)

```python
from hero_image_generator.ai import AIConfig, FluxModel, GeminiModel

# Load configuration from .env
config = AIConfig.load()

# Generate with Flux
flux = FluxModel(config, variant='pro')  # or 'dev', 'schnell'
result = flux.generate(
    prompt="Epic tech hero image",
    size=(1920, 1080),
    output_path="output.png"
)

# Generate with Imagen
gemini = GeminiModel(config)
result = gemini.generate(
    prompt="Modern workspace hero image",
    size=(1920, 1080),
    output_path="output.png"
)

# Quality validation
from hero_image_generator.ai import QualityValidator

validator = QualityValidator(config)
validation_result = validator.validate(
    image_path=result,
    prompt="Epic tech hero image"
)

print(f"Quality Score: {validation_result.score}")
print(f"Passed: {validation_result.passed}")
print(f"Feedback: {validation_result.feedback}")
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

### Core Dependencies
- Python 3.8+
- Pillow 10.0.0+

### AI Mode (Optional)
- replicate (for Flux models)
- google-cloud-aiplatform (for Imagen/Gemini)
- python-dotenv (for .env configuration)

All dependencies are installed automatically via `pip install -e ".[dev]"`

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
                                       [--ai] [--prompt PROMPT]
                                       [--model {flux-pro,flux-dev,flux-schnell,imagen}]
                                       [--size {small,medium,large}]
                                       [--validate]

Generate professional hero images with theme-based visual systems or AI models

optional arguments:
  -h, --help            show this help message and exit

  Programmatic Mode (default):
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

  AI Mode:
  --ai                  Use AI generation (Flux/Gemini) instead of programmatic themes
  --prompt PROMPT       AI generation prompt (required with --ai)
  --model {flux-pro,flux-dev,flux-schnell,imagen}
                        AI model to use (default: flux-pro)
  --size {small,medium,large}
                        Image size preset (default: medium)
  --validate            Enable quality validation with Gemini Vision (requires GCP)
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Credits

Created by [IntelliAgent](https://intelliagent.com.au) for generating professional hero images for blog posts and marketing content.
