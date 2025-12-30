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
# Run all unit tests (no API calls)
pytest tests/ -v -m "not slow"

# Run all tests including integration tests (incurs API costs ~$0.04)
pytest tests/ --run-slow -v

# Run with coverage report
pytest tests/ --cov=hero_image_generator --cov-report=html

# Run specific test file
pytest tests/test_theme_detector.py -v

# Run only AI module unit tests
pytest tests/ai/ -v

# Run integration tests (real API calls)
pytest tests/integration/ --run-slow -v
```

### Interactive Wizard
```bash
# Launch wizard (no arguments)
python -m hero_image_generator

# Wizard will prompt for inputs and show live preview
# Config saved to ~/.config/hero-image-generator/last-used.json
```

### Generate Images

#### Programmatic Mode (Theme-Based)
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

#### AI Mode (Flux/Gemini)
```bash
# Flux Schnell (fast, cheap)
python -m hero_image_generator --ai --prompt "Epic tech hero image" --model flux-schnell

# Flux Pro (highest quality)
python -m hero_image_generator --ai --prompt "Professional conference hero" --model flux-pro --size large

# Imagen with quality validation
python -m hero_image_generator --ai --prompt "Modern workspace" --model imagen --validate

# Custom output path
python -m hero_image_generator --ai --prompt "AI agents platform" --model flux-dev --output my-hero.png
```

## Development Workflow

**Branch Strategy:** Use regular git branches directly in the main repository. Do NOT use git worktrees for this project.

**Task Management:** Use GitHub Issues to track features, bugs, and tasks. Create issues before starting new work and reference them in commits.

**Feature Development:**
```bash
# Create feature branch from main
git checkout -b feature/feature-name

# Make changes, commit regularly
git add .
git commit -m "feat: description (#issue-number)"

# Push and create PR
git push -u origin feature/feature-name
gh pr create
```

**Testing:** Always run full test suite before pushing:
```bash
pytest tests/ -v
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

## AI Integration (v2.0.0+)

### Overview

The AI module (`hero_image_generator/ai/`) adds support for generating hero images using external AI models (Flux via Replicate, Imagen/Gemini via Google Vertex AI) as an alternative to the programmatic theme-based system.

### Architecture: Separate Modes

The project uses a **dual-mode architecture** with mode selection upfront:

1. **Mode Selection** - Wizard/CLI asks user to choose mode first
2. **Separate Code Paths** - Each mode has independent implementation
3. **Shared Infrastructure** - Both use same output handling and file management

**Key Design Decision:** Separate modes prevent complexity of merging AI visuals with programmatic themes. User gets either theme-based OR AI-generated images, never hybrid.

### AI Module Structure

```
hero_image_generator/ai/
├── __init__.py           # Exports: AIConfig, FluxModel, GeminiModel, QualityValidator, CostTracker
├── config.py             # Configuration loader from .env
├── flux.py               # Flux model integration (Replicate API)
├── gemini.py             # Imagen/Gemini integration (Vertex AI)
├── cost_tracker.py       # Cost logging and session tracking
└── quality_validator.py  # Quality validation with Gemini Vision
```

### AI Configuration (config.py:15-89)

**Purpose:** Load and validate environment variables from `.env` file.

**Environment Variables:**
```bash
# Required for Flux
REPLICATE_API_TOKEN=r8_...

# Required for Imagen/Gemini
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# Model Selection
DEFAULT_MODEL=flux-pro
FALLBACK_MODEL=flux-dev

# Quality Validation
ENABLE_QUALITY_CHECK=false
MIN_QUALITY_SCORE=0.6

# Image Sizes (WIDTHxHEIGHT)
SIZE_SMALL=800x450
SIZE_MEDIUM=1920x1080
SIZE_LARGE=2560x1440

# Output
OUTPUT_DIRECTORY=public/images
FAILED_OUTPUT_DIRECTORY=public/images/failed
SAVE_FAILED_GENERATIONS=true

# Cost Tracking
LOG_COSTS=true
COST_LOG_FILE=generation_costs.log

# Retry Logic
MAX_RETRIES=2
RETRY_DELAY_SECONDS=5
```

**Loading:**
```python
from hero_image_generator.ai import AIConfig

config = AIConfig.load()  # Loads from .env, validates required vars
```

**Validation:**
- Raises `ConfigurationError` if required vars missing
- Validates file paths exist (GOOGLE_APPLICATION_CREDENTIALS)
- Parses size strings to tuples: "1920x1080" → (1920, 1080)

**Test Coverage:** 100% (`tests/ai/test_config.py`)

### Flux Model Integration (flux.py:12-134)

**Purpose:** Generate images using Flux models via Replicate API.

**Supported Variants:**
- `flux-pro`: Highest quality ($0.055), ~6s
- `flux-dev`: Production quality ($0.020), ~4s
- `flux-schnell`: Fast drafts ($0.010), ~2s

**Architecture:**
```python
class FluxModel:
    VARIANT_CONFIG = {
        'pro': {'model': 'black-forest-labs/flux-1.1-pro', 'cost': 0.055},
        'dev': {'model': 'black-forest-labs/flux-dev', 'cost': 0.020},
        'schnell': {'model': 'black-forest-labs/flux-schnell', 'cost': 0.010}
    }

    def generate(self, prompt: str, size: tuple, output_path: Path) -> Path:
        # 1. Validate inputs
        # 2. Call Replicate API via replicate.run()
        # 3. Download image from URL
        # 4. Save to output_path
        # 5. Return path
```

**Retry Logic:**
- Automatic retry on network/API failures (configurable: MAX_RETRIES, RETRY_DELAY_SECONDS)
- Exponential backoff between retries
- Failed generations saved to FAILED_OUTPUT_DIRECTORY if SAVE_FAILED_GENERATIONS=true

**API Call:**
```python
output = replicate.run(
    model_id,
    input={
        "prompt": prompt,
        "width": size[0],
        "height": size[1],
        "num_outputs": 1
    }
)
# Returns list of image URLs
```

**Test Coverage:** 100% unit tests (mocked), real API integration tests available with `--run-slow` flag

### Gemini/Imagen Integration (gemini.py:12-121)

**Purpose:** Generate images using Imagen via Google Vertex AI.

**Model:** `imagegeneration@006` (stable, production-ready)

**Cost:** $0.020 per generation

**Architecture:**
```python
class GeminiModel:
    def generate(self, prompt: str, size: tuple, output_path: Path) -> Path:
        # 1. Initialize Vertex AI client
        # 2. Load ImageGenerationModel
        # 3. Generate image with prompt
        # 4. Extract image bytes from response
        # 5. Save to output_path
        # 6. Return path
```

**API Initialization:**
```python
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

aiplatform.init(project=config.gcp_project_id, location=config.gcp_location)
model = ImageGenerationModel.from_pretrained('imagegeneration@006')
```

**Generation:**
```python
response = model.generate_images(
    prompt=prompt,
    number_of_images=1,
    aspect_ratio="16:9"  # Closest to 1920x1080
)
image = response.images[0]._pil_image
image.save(output_path)
```

**Limitations:**
- No direct size control (uses aspect ratios: 1:1, 16:9, 9:16, 4:3, 3:4)
- Generates at fixed resolution, may need resizing to exact dimensions

**Test Coverage:** 100% unit tests (mocked), real API integration tests available with `--run-slow` flag

### Quality Validator (quality_validator.py:12-93)

**Purpose:** Validate generated images using Gemini Vision with structured JSON feedback.

**Cost:** $0.001 per validation

**Architecture:**
```python
class QualityValidator:
    VALIDATION_COST = 0.001

    def validate(self, image_path: Path, prompt: str) -> ValidationResult:
        # 1. Load image as base64
        # 2. Send to Gemini Vision with validation prompt
        # 3. Parse JSON response
        # 4. Return ValidationResult (score, passed, feedback, cost)
```

**Validation Prompt Template:**
```
You are evaluating the quality of a generated hero image (1200x630px or similar).

Original prompt: {prompt}

Evaluate on these criteria:
1. Prompt Accuracy: Does it match the prompt?
2. Composition: Professional layout, balanced, good use of space?
3. Aesthetics: Visually appealing, color harmony, professional look?
4. Technical Quality: Sharp, no artifacts, good resolution?

Return JSON:
{
  "score": 0.0-1.0,
  "breakdown": {
    "prompt_accuracy": 0.0-1.0,
    "composition": 0.0-1.0,
    "aesthetics": 0.0-1.0,
    "technical_quality": 0.0-1.0
  },
  "issues": ["list of problems"],
  "strengths": ["list of strengths"],
  "recommendation": "accept/regenerate"
}
```

**ValidationResult:**
```python
@dataclass
class ValidationResult:
    score: float              # Overall score 0.0-1.0
    passed: bool              # score >= MIN_QUALITY_SCORE
    feedback: str             # Human-readable summary
    cost: float = 0.001       # Validation cost
    raw_response: Optional[Dict] = None  # Full JSON response
```

**Error Handling:**
- Non-JSON responses: Extract text feedback, score=0.0
- Missing image: Raise FileNotFoundError
- API failures: Propagate with context

**Test Coverage:** 100% (`tests/ai/test_quality_validator.py`)

### Cost Tracker (cost_tracker.py:9-67)

**Purpose:** Track and log API costs per session and cumulatively.

**Architecture:**
```python
class CostTracker:
    def __init__(self, log_file: Path, enabled: bool = True):
        self.session_total = 0.0
        self.log_file = log_file
        self.enabled = enabled

    def track(self, model: str, cost: float) -> None:
        self.session_total += cost
        if self.enabled:
            self._log_to_file(model, cost)

    def get_session_total(self) -> float:
        return self.session_total
```

**Log Format:**
```
2025-12-30 14:32:15 - Model: flux-pro, Cost: $0.055, Total Session: $0.055
2025-12-30 14:35:22 - Model: flux-schnell, Cost: $0.010, Total Session: $0.065
2025-12-30 14:38:45 - Validation Cost: $0.001, Total Session: $0.066
```

**Usage:**
```python
from hero_image_generator.ai import CostTracker, AIConfig

config = AIConfig.load()
tracker = CostTracker(config.cost_log_file, enabled=config.log_costs)

# After generation
tracker.track('flux-pro', 0.055)

# Get session total
print(f"Session cost: ${tracker.get_session_total():.3f}")
```

**Test Coverage:** 100% (`tests/ai/test_cost_tracker.py`)

### AI Wizard Integration (wizard/ai_wizard.py:13-246)

**Purpose:** Interactive CLI wizard for AI mode with prompt collection and model selection.

**Workflow:**
1. Collect prompt from user
2. Select model (Flux Pro/Dev/Schnell or Imagen)
3. Select size (small/medium/large)
4. Generate and preview
5. Refinement loop:
   - Regenerate with same settings
   - Modify prompt
   - Change model
   - Change size
6. Save final image

**Refinement Menu:**
```
[1] Regenerate (same prompt/model/size)
[2] Modify prompt
[3] Change model
[4] Change size
[5] Start over
[0] Save and exit
```

**Model Selection:**
```
Select AI model:
[1] Flux Pro - Highest quality ($0.055)
[2] Flux Dev - Production quality ($0.020)
[3] Flux Schnell - Fast drafts ($0.010)
[4] Imagen - Google Vertex AI ($0.020)
```

**Integration with Main Wizard:**
- Main wizard asks mode selection first
- If AI mode selected, delegates to AIWizardRunner
- Separate code paths, no mode mixing

**Test Coverage:** 90% (`tests/wizard/test_ai_wizard.py`)

### CLI Integration (cli.py:250-320)

**AI Mode Detection:**
```python
if args.ai:
    handle_ai_mode(args)
    return
```

**AI Mode Handler:**
```python
def handle_ai_mode(args):
    # 1. Load config
    config = AIConfig.load()

    # 2. Initialize cost tracker
    tracker = CostTracker(config.cost_log_file, config.log_costs)

    # 3. Select model
    if args.model == 'imagen':
        model = GeminiModel(config)
    else:
        model = FluxModel(config, variant=args.model.split('-')[1])

    # 4. Parse size
    size = config.size_presets[args.size]

    # 5. Generate
    result = model.generate(prompt=args.prompt, size=size, output_path=output_path)

    # 6. Track cost
    tracker.track(args.model, model.get_cost())

    # 7. Optional validation
    if args.validate and config.enable_quality_check:
        validator = QualityValidator(config)
        validation = validator.validate(result, args.prompt)
        tracker.track('validation', validation.cost)

    # 8. Display summary
    print(f"Generated: {result}")
    print(f"Cost: ${tracker.get_session_total():.3f}")
```

**Test Coverage:** 100% (`tests/test_cli.py`)

### Testing Strategy

**Unit Tests (Mocked APIs):**
- All AI module tests use mocks to avoid API costs
- Mock `replicate.run()` for Flux tests
- Mock `GenerativeModel` for Gemini tests
- 100% coverage for all AI modules

**Integration Tests (Real APIs):**
- Located in `tests/integration/`
- Require `--run-slow` flag to run
- Make real API calls (incur costs ~$0.04 per full run)
- Test full end-to-end workflows

**Pytest Markers:**
```python
@pytest.mark.slow              # Requires --run-slow flag
@pytest.mark.requires_api_keys # Needs real API credentials
@pytest.mark.integration       # Integration test
```

**Run Commands:**
```bash
# Unit tests only (free, fast)
pytest tests/ai/ -v

# All tests including integration (costs ~$0.04)
pytest tests/ --run-slow -v

# Only Flux integration tests
pytest tests/integration/test_flux_integration.py --run-slow -v
```

**Test Fixtures:**
```python
@pytest.fixture
def real_config():
    """Load real config from .env for integration tests"""
    return AIConfig.load()

@pytest.fixture
def mock_config():
    """Mock config for unit tests"""
    config = MagicMock()
    config.replicate_api_token = "test_token"
    config.gcp_project_id = "test-project"
    # ... all attributes
    return config
```

### Key Constraints

- **API Costs:** All generations incur real costs - track carefully
- **Rate Limits:** Replicate (50 concurrent, 600/min), Vertex AI (60/min)
- **No Fallback Between Modes:** User must explicitly choose programmatic OR AI
- **Quality Validation:** Requires GCP setup even if using only Flux models
- **Image Sizes:** AI models may not support exact dimensions, may require resizing
- **Retry Logic:** Automatic retries on failures to handle transient errors

### Extending AI Support

To add new AI providers:

1. Create new model class in `hero_image_generator/ai/` (e.g., `openai.py`)
2. Implement `generate(prompt, size, output_path)` method
3. Add cost constant and tracking
4. Update `AIConfig` with new provider env vars
5. Add to wizard model selection menu
6. Add CLI flag support
7. Write unit tests with mocks
8. Write integration test with `@pytest.mark.slow`
9. Update documentation (README, CLAUDE.md, setup guides)

Example template:
```python
class NewProviderModel:
    def __init__(self, config: AIConfig):
        self.api_key = config.new_provider_api_key
        self.cost_per_image = 0.03  # Example cost

    def generate(self, prompt: str, size: tuple, output_path: Path) -> Path:
        # Implementation
        return output_path

    def get_cost(self) -> float:
        return self.cost_per_image
```
