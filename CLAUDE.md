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

Both invoke `cli.main()` which supports four modes: wizard (no args), single image, batch metadata, or preview.

## Interactive Wizard (v1.1.0+)

### Overview

The interactive wizard (`hero_image_generator/wizard/`) provides a guided CLI experience for creating hero images with live preview and iterative refinement. Launched when running without arguments.

### Architecture

The wizard is built with 4 modular components in `hero_image_generator/wizard/`:

#### 1. ConfigManager (`config.py`)

**Purpose:** Manages preference persistence between wizard sessions.

**Storage location:**
- macOS/Linux: `~/.config/hero-image-generator/last-used.json`
- Windows: `%APPDATA%/hero-image-generator/last-used.json`

**Saved settings:**
```json
{
  "accent_color": [139, 92, 246],
  "gradient_start": [59, 130, 246],
  "gradient_end": [139, 92, 246],
  "title_font_size": 60,
  "subtitle_font_size": 32,
  "year_font_size": 36,
  "theme_override": null,
  "last_year": 2025
}
```

**Key methods:**
- `get_config_path()` → Platform-specific path resolution
- `load()` → Load config or return defaults (handles missing/corrupted files)
- `save(config)` → Persist to JSON with directory creation
- `get_default_config()` → Default values

**Test coverage:** 100% (`tests/wizard/test_config.py`)

#### 2. InputPrompter (`prompt.py`)

**Purpose:** Handles user input with validation for all wizard prompts.

**Validation methods:**
- `validate_hex_color(hex_str)` → Accepts `#8B5CF6` or `8B5CF6`
- `validate_rgb_color(rgb_str)` → Accepts `139,92,246` or `139, 92, 246`
- `validate_year(year_str)` → Range 1900-2099

**Prompt methods:**
- `prompt_title()` → Non-empty, max 100 chars (warns at 60+)
- `prompt_tags()` → Comma-separated, auto-lowercase, stripped
- `prompt_year(default)` → Integer with default
- `prompt_color(name, default)` → 7-option menu (6 presets + custom)

**Color presets:**
```python
'1': ('purple', (139, 92, 246))
'2': ('green', (34, 197, 94))
'3': ('orange', (249, 115, 22))
'4': ('cyan', (6, 182, 212))
'5': ('red', (239, 68, 68))
'6': ('blue', (59, 130, 246))
'7': Custom hex/RGB input
```

**Test coverage:** 94% (`tests/wizard/test_prompt.py`)

#### 3. PreviewManager (`preview.py`)

**Purpose:** Cross-platform image preview and refinement workflow.

**Platform-specific preview commands:**
- macOS: `subprocess.run(['open', image_path])`
- Linux: `subprocess.run(['xdg-open', image_path])`
- Windows: `os.startfile(image_path)`

**Refinement menu options:**
```
[1] Title
[2] Tags (will re-detect theme)
[3] Year badge
[4] Override theme
[5] Accent color
[6] Gradient colors
[7] Font sizes
[8] Start over
[0] Cancel (keep current image)
```

**Key methods:**
- `open_preview(image_path)` → Platform-specific viewer launch (non-fatal errors)
- `ask_satisfied()` → y/n prompt with validation
- `show_refinement_menu()` → Display options, return choice
- `prompt_output_filename(default)` → Custom filename with .png validation
- `prompt_output_directory(default)` → Directory path with existence check

**Test coverage:** 100% (`tests/wizard/test_preview.py`)

#### 4. WizardRunner (`__init__.py`)

**Purpose:** Main orchestration class that coordinates all wizard components.

**Workflow:**
1. Load saved preferences via ConfigManager
2. Collect initial inputs (title, tags, year, optional customizations)
3. Generate temp preview image
4. Open preview in system viewer
5. Refinement loop:
   - Ask if satisfied
   - If no: show menu, apply changes, regenerate
   - If yes: proceed to save
6. Save final image with custom filename
7. Persist preferences for next session

**Key methods:**
- `run()` → Main entry point (handles Ctrl+C gracefully)
- `_collect_initial_inputs()` → Initial prompts
- `_collect_customizations()` → Color/font customization
- `_generate_and_preview()` → Generate + open preview
- `_handle_refinement(choice)` → Apply menu choice
- `_save_final_image()` → Final save with filename prompt
- `_save_config()` → Persist to ConfigManager
- `_slugify(text)` → Convert title to filename-safe slug

**State management:**
```python
self.config: Dict[str, Any]      # Loaded preferences
self.title: str                   # Current title
self.tags: list                   # Current tags
self.year: int                    # Current year
self.theme_override: Optional[str] # Manual theme override
self.output_path: str             # Last generated image path
```

**Error handling:**
- KeyboardInterrupt → Clean exit with message
- Missing config → Use defaults silently
- Corrupted config → Warning + defaults
- Preview failures → Non-fatal, show file path

**Test coverage:** 20% (integration tests - most requires user input simulation)

### CLI Integration

**Detection logic** (`cli.py:196-201`):
```python
if len(sys.argv) == 1:
    from .wizard import WizardRunner
    wizard = WizardRunner()
    wizard.run()
    return
```

**Backward compatibility:** All existing CLI flags unchanged:
- `--preview` → Generate theme samples
- `--title/--tags/--output` → Single image
- `--metadata` → Batch generation
- `--help` → Show help

Only change: No arguments launches wizard instead of help.

### Testing Strategy

**Unit tests** (59 wizard tests total):
- `test_config.py` (8 tests) → Path resolution, save/load, error handling
- `test_prompt.py` (45 tests) → Validation, color parsing, input prompts
- `test_preview.py` (18 tests) → Platform detection, menu, filename validation
- `test_wizard_runner.py` (1 test) → Initialization
- `test_cli.py` (3 tests) → CLI integration, backward compatibility

**Coverage:**
- ConfigManager: 100%
- InputPrompter: 94%
- PreviewManager: 100%
- WizardRunner: 20% (input simulation complexity)
- Overall: 62% (72 tests passing)

**Test techniques:**
- Mock `input()` for automated testing
- Mock `subprocess.run()` for preview commands
- Mock `sys.platform` for cross-platform tests
- `tmp_path` fixture for filesystem operations
- `monkeypatch` for config path overrides

### File Structure

```
hero_image_generator/
├── wizard/
│   ├── __init__.py          # WizardRunner (294 lines)
│   ├── config.py            # ConfigManager (79 lines)
│   ├── preview.py           # PreviewManager (155 lines)
│   └── prompt.py            # InputPrompter (231 lines)
├── cli.py                   # Modified: no-args detection
├── image_generator.py       # Core generator (unchanged)
└── ...

tests/
├── wizard/
│   ├── __init__.py
│   ├── test_config.py       # 112 lines, 8 tests
│   ├── test_preview.py      # 280 lines, 18 tests
│   ├── test_prompt.py       # 217 lines, 45 tests
│   └── test_wizard_runner.py # 11 lines, 1 test
├── test_cli.py              # Added: wizard integration tests
└── ...

docs/
├── plans/
│   └── 2025-12-28-interactive-wizard.md  # Implementation plan
└── screenshots/
    ├── WIZARD_DEMO.md       # Complete walkthrough
    ├── demo-ai-ml.png       # AI/ML theme sample
    ├── demo-seo.png         # SEO theme sample
    ├── demo-automation.png  # Automation theme sample
    └── demo-strategy.png    # Strategy theme sample
```

### Development Workflow Used

The wizard was built following a disciplined TDD approach:

1. **Planning:** Detailed design document → implementation plan (9 tasks)
2. **Implementation:** Task-by-task with test-first methodology
   - Write failing test
   - Implement minimal code to pass
   - Refactor
   - Commit
3. **Integration:** CLI integration with backward compatibility tests
4. **Documentation:** README, CLAUDE.md, demo screenshots, walkthrough
5. **Release:** PR review, merge, tag v1.1.0

**Key decisions:**
- Modular architecture for testability
- Platform abstraction for cross-platform support
- Non-fatal preview errors for resilience
- Preference persistence for UX continuity
- Color preset system for ease of use
