# Interactive CLI Wizard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an interactive CLI wizard that launches when run without arguments, providing step-by-step prompts with live preview and iterative refinement.

**Architecture:** Modular wizard package (`hero_image_generator/wizard/`) with four components: ConfigManager (persistence), InputPrompter (user input), PreviewManager (preview/refinement), and WizardRunner (orchestration). Integrates into existing CLI via no-args detection.

**Tech Stack:** Python 3.8+, Pillow, pytest, subprocess (for preview), json (for config), pathlib (for cross-platform paths)

---

## Task 1: Fix Existing Test Imports

**Files:**
- Modify: `tests/test_theme_detector.py`
- Modify: `tests/test_subtitle_generator.py`
- Modify: `tests/test_visual_renderer.py`
- Modify: `tests/test_image_generation.py`
- Modify: `tests/test_tag_icons.py`

**Step 1: Fix test_theme_detector.py imports**

Replace lines 1-3:
```python
from hero_image_generator.theme_detector import ThemeDetector, Theme
```

**Step 2: Fix test_subtitle_generator.py imports**

Replace line 3:
```python
from hero_image_generator.subtitle_generator import SubtitleGenerator
```

**Step 3: Fix test_visual_renderer.py imports**

Replace lines 1-4:
```python
from PIL import Image
from hero_image_generator.visual_renderer import VisualRenderer
from hero_image_generator.theme_detector import Theme
```

**Step 4: Fix test_image_generation.py imports**

Replace line 4:
```python
from hero_image_generator.image_generator import HeroImageGenerator
```

**Step 5: Fix test_tag_icons.py imports**

Check if `tag_icons.py` module exists. If not, delete this test file (appears to be for non-existent module).

**Step 6: Run all tests to verify baseline**

```bash
pytest tests/ -v
```

Expected: Tests pass or fail for valid reasons (not import errors)

**Step 7: Commit**

```bash
git add tests/
git commit -m "fix: correct test imports to use package name"
```

---

## Task 2: ConfigManager - Configuration Persistence

**Files:**
- Create: `hero_image_generator/wizard/__init__.py`
- Create: `hero_image_generator/wizard/config.py`
- Create: `tests/wizard/__init__.py`
- Create: `tests/wizard/test_config.py`

**Step 1: Create wizard package structure**

```bash
mkdir -p hero_image_generator/wizard
mkdir -p tests/wizard
touch hero_image_generator/wizard/__init__.py
touch tests/wizard/__init__.py
```

**Step 2: Write failing test for ConfigManager.get_config_path**

Create `tests/wizard/test_config.py`:
```python
import os
from pathlib import Path
from hero_image_generator.wizard.config import ConfigManager


def test_get_config_path_returns_path_object():
    """Config path should be a Path object"""
    manager = ConfigManager()
    path = manager.get_config_path()
    assert isinstance(path, Path)


def test_get_config_path_contains_hero_image_generator():
    """Config path should contain app name"""
    manager = ConfigManager()
    path = manager.get_config_path()
    assert 'hero-image-generator' in str(path)


def test_get_config_path_ends_with_last_used_json():
    """Config file should be named last-used.json"""
    manager = ConfigManager()
    path = manager.get_config_path()
    assert path.name == 'last-used.json'
```

**Step 3: Run test to verify failure**

```bash
pytest tests/wizard/test_config.py -v
```

Expected: ModuleNotFoundError: No module named 'hero_image_generator.wizard.config'

**Step 4: Write minimal ConfigManager with get_config_path**

Create `hero_image_generator/wizard/config.py`:
```python
"""Configuration persistence for wizard preferences."""

import json
import sys
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages wizard configuration persistence."""

    def get_config_path(self) -> Path:
        """
        Get platform-specific config file path.

        Returns:
            Path to last-used.json config file
        """
        if sys.platform == 'win32':
            # Windows: %APPDATA%/hero-image-generator/last-used.json
            base = Path(os.environ.get('APPDATA', '~'))
        else:
            # Linux/macOS: ~/.config/hero-image-generator/last-used.json
            base = Path.home() / '.config'

        config_dir = base / 'hero-image-generator'
        return config_dir / 'last-used.json'

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values.

        Returns:
            Dictionary with default settings
        """
        return {
            'accent_color': [139, 92, 246],  # Purple
            'gradient_start': [59, 130, 246],  # Blue
            'gradient_end': [139, 92, 246],  # Purple
            'title_font_size': 60,
            'subtitle_font_size': 32,
            'year_font_size': 36,
            'theme_override': None,
            'last_year': 2025,
        }

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file or return defaults.

        Returns:
            Configuration dictionary
        """
        config_path = self.get_config_path()

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                defaults = self.get_default_config()
                return {**defaults, **config}
        except (FileNotFoundError, json.JSONDecodeError):
            return self.get_default_config()

    def save(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration dictionary to save
        """
        config_path = self.get_config_path()

        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
```

**Step 5: Add missing import**

Add to top of `config.py`:
```python
import os
```

**Step 6: Run test to verify pass**

```bash
pytest tests/wizard/test_config.py::test_get_config_path_returns_path_object -v
pytest tests/wizard/test_config.py::test_get_config_path_contains_hero_image_generator -v
pytest tests/wizard/test_config.py::test_get_config_path_ends_with_last_used_json -v
```

Expected: All PASS

**Step 7: Write test for load and save**

Add to `tests/wizard/test_config.py`:
```python
import tempfile
import json


def test_load_returns_defaults_when_file_missing(tmp_path, monkeypatch):
    """Should return defaults if config file doesn't exist"""
    # Mock config path to use temp directory
    manager = ConfigManager()
    fake_path = tmp_path / "missing" / "last-used.json"
    monkeypatch.setattr(manager, 'get_config_path', lambda: fake_path)

    config = manager.load()

    assert config['accent_color'] == [139, 92, 246]
    assert config['last_year'] == 2025
    assert 'gradient_start' in config


def test_load_returns_defaults_when_file_corrupted(tmp_path, monkeypatch):
    """Should return defaults if JSON is invalid"""
    manager = ConfigManager()
    fake_path = tmp_path / "last-used.json"
    monkeypatch.setattr(manager, 'get_config_path', lambda: fake_path)

    # Write invalid JSON
    fake_path.write_text("{invalid json")

    config = manager.load()

    assert config['accent_color'] == [139, 92, 246]


def test_save_and_load_roundtrip(tmp_path, monkeypatch):
    """Should save and load config correctly"""
    manager = ConfigManager()
    fake_path = tmp_path / "last-used.json"
    monkeypatch.setattr(manager, 'get_config_path', lambda: fake_path)

    # Save custom config
    custom_config = {
        'accent_color': [255, 0, 0],
        'last_year': 2024,
        'gradient_start': [100, 100, 100],
        'gradient_end': [200, 200, 200],
        'title_font_size': 70,
        'subtitle_font_size': 40,
        'year_font_size': 38,
        'theme_override': 'ai_ml',
    }
    manager.save(custom_config)

    # Load it back
    loaded = manager.load()

    assert loaded['accent_color'] == [255, 0, 0]
    assert loaded['last_year'] == 2024
    assert loaded['theme_override'] == 'ai_ml'
```

**Step 8: Run tests to verify pass**

```bash
pytest tests/wizard/test_config.py -v
```

Expected: All PASS

**Step 9: Commit**

```bash
git add hero_image_generator/wizard/config.py tests/wizard/
git commit -m "feat(wizard): add ConfigManager for preference persistence"
```

---

## Task 3: InputPrompter - User Input and Validation

**Files:**
- Create: `hero_image_generator/wizard/prompt.py`
- Create: `tests/wizard/test_prompt.py`

**Step 1: Write failing test for color validation**

Create `tests/wizard/test_prompt.py`:
```python
import pytest
from hero_image_generator.wizard.prompt import InputPrompter


def test_validate_hex_color_with_hash():
    """Should accept hex with #"""
    prompter = InputPrompter()
    result = prompter.validate_hex_color('#8B5CF6')
    assert result == (139, 92, 246)


def test_validate_hex_color_without_hash():
    """Should accept hex without #"""
    prompter = InputPrompter()
    result = prompter.validate_hex_color('8B5CF6')
    assert result == (139, 92, 246)


def test_validate_hex_color_invalid_returns_none():
    """Should return None for invalid hex"""
    prompter = InputPrompter()
    assert prompter.validate_hex_color('invalid') is None
    assert prompter.validate_hex_color('#GGG') is None
    assert prompter.validate_hex_color('12345') is None  # Too short


def test_validate_rgb_color():
    """Should accept RGB format"""
    prompter = InputPrompter()
    result = prompter.validate_rgb_color('139,92,246')
    assert result == (139, 92, 246)


def test_validate_rgb_color_with_spaces():
    """Should accept RGB with spaces"""
    prompter = InputPrompter()
    result = prompter.validate_rgb_color('139, 92, 246')
    assert result == (139, 92, 246)


def test_validate_rgb_color_invalid_returns_none():
    """Should return None for invalid RGB"""
    prompter = InputPrompter()
    assert prompter.validate_rgb_color('invalid') is None
    assert prompter.validate_rgb_color('256,100,100') is None  # Out of range
    assert prompter.validate_rgb_color('100,100') is None  # Too few values
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/wizard/test_prompt.py -v
```

Expected: ModuleNotFoundError

**Step 3: Write InputPrompter with validation methods**

Create `hero_image_generator/wizard/prompt.py`:
```python
"""User input prompts and validation for wizard."""

import re
from typing import Optional, Tuple, List


class InputPrompter:
    """Handles user input with validation."""

    # Color presets for quick selection
    COLOR_PRESETS = {
        '1': ('purple', (139, 92, 246)),
        '2': ('green', (34, 197, 94)),
        '3': ('orange', (249, 115, 22)),
        '4': ('cyan', (6, 182, 212)),
        '5': ('red', (239, 68, 68)),
        '6': ('blue', (59, 130, 246)),
    }

    def validate_hex_color(self, hex_str: str) -> Optional[Tuple[int, int, int]]:
        """
        Validate and convert hex color string to RGB tuple.

        Args:
            hex_str: Hex color string (with or without #)

        Returns:
            RGB tuple or None if invalid
        """
        # Remove # if present
        hex_str = hex_str.lstrip('#')

        # Check format
        if not re.match(r'^[0-9A-Fa-f]{6}$', hex_str):
            return None

        # Convert to RGB
        try:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return (r, g, b)
        except ValueError:
            return None

    def validate_rgb_color(self, rgb_str: str) -> Optional[Tuple[int, int, int]]:
        """
        Validate and convert RGB string to tuple.

        Args:
            rgb_str: RGB string like "139,92,246" or "139, 92, 246"

        Returns:
            RGB tuple or None if invalid
        """
        try:
            # Split by comma and strip whitespace
            parts = [p.strip() for p in rgb_str.split(',')]

            if len(parts) != 3:
                return None

            # Convert to integers
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])

            # Validate range
            if not all(0 <= val <= 255 for val in [r, g, b]):
                return None

            return (r, g, b)
        except (ValueError, AttributeError):
            return None

    def validate_year(self, year_str: str) -> Optional[int]:
        """
        Validate year input.

        Args:
            year_str: Year as string

        Returns:
            Year as integer or None if invalid
        """
        try:
            year = int(year_str)
            if 1900 <= year <= 2099:
                return year
            return None
        except ValueError:
            return None

    def prompt_title(self) -> str:
        """
        Prompt for image title.

        Returns:
            Non-empty title string
        """
        while True:
            title = input("Enter image title: ").strip()
            if title:
                if len(title) > 60:
                    print("⚠️  Long titles may wrap to 3+ lines")
                if len(title) > 100:
                    print("❌ Title too long (max 100 characters)")
                    continue
                return title
            print("❌ Title cannot be empty")

    def prompt_tags(self) -> List[str]:
        """
        Prompt for tags.

        Returns:
            List of tags (lowercase, stripped)
        """
        while True:
            tags_str = input("Enter tags (comma-separated): ").strip()
            if tags_str:
                tags = [t.strip().lower() for t in tags_str.split(',')]
                tags = [t for t in tags if t]  # Remove empty
                if tags:
                    return tags
            print("❌ At least one tag is required")

    def prompt_year(self, default: int = 2025) -> int:
        """
        Prompt for year with default.

        Args:
            default: Default year value

        Returns:
            Valid year integer
        """
        while True:
            year_str = input(f"Year [{default}]: ").strip()

            if not year_str:
                return default

            year = self.validate_year(year_str)
            if year is not None:
                return year

            print("❌ Invalid year (must be between 1900-2099)")

    def prompt_color(self, name: str, default: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Prompt for color with presets and custom option.

        Args:
            name: Display name for the color
            default: Default RGB tuple

        Returns:
            RGB tuple
        """
        print(f"\n{name}:")
        print("[1] purple  [2] green  [3] orange  [4] cyan")
        print("[5] red     [6] blue   [7] custom")

        while True:
            choice = input(f"Choice [1]: ").strip() or '1'

            if choice in self.COLOR_PRESETS:
                return self.COLOR_PRESETS[choice][1]

            if choice == '7':
                return self._prompt_custom_color(name, default)

            print("❌ Invalid choice (1-7)")

    def _prompt_custom_color(self, name: str, default: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Prompt for custom color in hex or RGB format."""
        while True:
            color_str = input(f"Enter hex or RGB (e.g., #8B5CF6 or 139,92,246): ").strip()

            if not color_str:
                return default

            # Try hex first
            rgb = self.validate_hex_color(color_str)
            if rgb:
                return rgb

            # Try RGB
            rgb = self.validate_rgb_color(color_str)
            if rgb:
                return rgb

            print("❌ Invalid format. Use hex (#8B5CF6) or RGB (139,92,246)")
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/wizard/test_prompt.py -v
```

Expected: All PASS

**Step 5: Write tests for year validation**

Add to `tests/wizard/test_prompt.py`:
```python
def test_validate_year_valid():
    """Should accept valid years"""
    prompter = InputPrompter()
    assert prompter.validate_year('2025') == 2025
    assert prompter.validate_year('1900') == 1900
    assert prompter.validate_year('2099') == 2099


def test_validate_year_invalid():
    """Should reject invalid years"""
    prompter = InputPrompter()
    assert prompter.validate_year('1899') is None  # Too old
    assert prompter.validate_year('2100') is None  # Too new
    assert prompter.validate_year('invalid') is None  # Not a number
    assert prompter.validate_year('') is None  # Empty
```

**Step 6: Run tests to verify pass**

```bash
pytest tests/wizard/test_prompt.py -v
```

Expected: All PASS

**Step 7: Commit**

```bash
git add hero_image_generator/wizard/prompt.py tests/wizard/test_prompt.py
git commit -m "feat(wizard): add InputPrompter with validation"
```

---

## Task 4: PreviewManager - Preview and Refinement

**Files:**
- Create: `hero_image_generator/wizard/preview.py`
- Create: `tests/wizard/test_preview.py`

**Step 1: Write failing test for platform detection**

Create `tests/wizard/test_preview.py`:
```python
import sys
from unittest import mock
from hero_image_generator.wizard.preview import PreviewManager


def test_open_preview_macos(tmp_path):
    """Should use 'open' command on macOS"""
    manager = PreviewManager()
    test_image = tmp_path / "test.png"
    test_image.write_text("fake image")

    with mock.patch('sys.platform', 'darwin'):
        with mock.patch('subprocess.run') as mock_run:
            manager.open_preview(str(test_image))
            mock_run.assert_called_once_with(['open', str(test_image)])


def test_open_preview_linux(tmp_path):
    """Should use 'xdg-open' command on Linux"""
    manager = PreviewManager()
    test_image = tmp_path / "test.png"
    test_image.write_text("fake image")

    with mock.patch('sys.platform', 'linux'):
        with mock.patch('subprocess.run') as mock_run:
            manager.open_preview(str(test_image))
            mock_run.assert_called_once_with(['xdg-open', str(test_image)])


def test_open_preview_windows(tmp_path):
    """Should use os.startfile on Windows"""
    manager = PreviewManager()
    test_image = tmp_path / "test.png"
    test_image.write_text("fake image")

    with mock.patch('sys.platform', 'win32'):
        with mock.patch('os.startfile') as mock_startfile:
            manager.open_preview(str(test_image))
            mock_startfile.assert_called_once_with(str(test_image))


def test_open_preview_handles_failure_gracefully(tmp_path):
    """Should print error message but not crash on failure"""
    manager = PreviewManager()
    test_image = tmp_path / "test.png"
    test_image.write_text("fake image")

    with mock.patch('subprocess.run', side_effect=Exception("Command failed")):
        # Should not raise exception
        manager.open_preview(str(test_image))
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/wizard/test_preview.py -v
```

Expected: ModuleNotFoundError

**Step 3: Write PreviewManager implementation**

Create `hero_image_generator/wizard/preview.py`:
```python
"""Preview and refinement management for wizard."""

import sys
import os
import subprocess
from typing import Optional


class PreviewManager:
    """Manages image preview and refinement workflow."""

    def open_preview(self, image_path: str) -> None:
        """
        Open image in system default viewer.

        Args:
            image_path: Path to image file
        """
        try:
            if sys.platform == 'darwin':
                subprocess.run(['open', image_path])
            elif sys.platform == 'win32':
                os.startfile(image_path)
            else:
                subprocess.run(['xdg-open', image_path])
        except Exception as e:
            print(f"⚠️  Could not auto-open preview: {e}")
            print(f"📁 Image saved at: {image_path}")
            print("   Open manually to view")

    def ask_satisfied(self) -> bool:
        """
        Ask if user is satisfied with the image.

        Returns:
            True if satisfied, False otherwise
        """
        while True:
            response = input("\nSatisfied with this image? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            print("❌ Please enter 'y' or 'n'")

    def show_refinement_menu(self) -> str:
        """
        Show refinement options menu.

        Returns:
            Menu choice as string
        """
        print("\nWhat would you like to change?")
        print("[1] Title")
        print("[2] Tags (will re-detect theme)")
        print("[3] Year badge")
        print("[4] Override theme")
        print("[5] Accent color")
        print("[6] Gradient colors")
        print("[7] Font sizes")
        print("[8] Start over")
        print("[0] Cancel (keep current image)")

        while True:
            choice = input("\nChoice: ").strip()
            if choice in ['0', '1', '2', '3', '4', '5', '6', '7', '8']:
                return choice
            print("❌ Invalid choice (0-8)")

    def prompt_output_filename(self, default: str) -> str:
        """
        Prompt for output filename.

        Args:
            default: Default filename

        Returns:
            Output filename
        """
        filename = input(f"\nSave as [{default}]: ").strip()
        return filename if filename else default

    def prompt_output_directory(self, default: str) -> str:
        """
        Prompt for output directory.

        Args:
            default: Default directory

        Returns:
            Output directory path
        """
        directory = input(f"Output directory [{default}]: ").strip()
        return directory if directory else default
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/wizard/test_preview.py -v
```

Expected: All PASS

**Step 5: Commit**

```bash
git add hero_image_generator/wizard/preview.py tests/wizard/test_preview.py
git commit -m "feat(wizard): add PreviewManager for image preview"
```

---

## Task 5: WizardRunner - Main Orchestration

**Files:**
- Modify: `hero_image_generator/wizard/__init__.py`
- Create: `tests/wizard/test_wizard_runner.py`

**Step 1: Write integration test for WizardRunner**

Create `tests/wizard/test_wizard_runner.py`:
```python
from unittest import mock
from hero_image_generator.wizard import WizardRunner


def test_wizard_runner_initialization():
    """Should initialize with all required components"""
    with mock.patch('hero_image_generator.wizard.config.ConfigManager'):
        with mock.patch('hero_image_generator.wizard.prompt.InputPrompter'):
            with mock.patch('hero_image_generator.wizard.preview.PreviewManager'):
                runner = WizardRunner()
                assert runner is not None
```

**Step 2: Run test to verify failure**

```bash
pytest tests/wizard/test_wizard_runner.py -v
```

Expected: ImportError or AttributeError

**Step 3: Write WizardRunner class**

Update `hero_image_generator/wizard/__init__.py`:
```python
"""Interactive CLI wizard for hero image generation."""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional

from ..image_generator import HeroImageGenerator
from ..theme_detector import ThemeDetector
from .config import ConfigManager
from .prompt import InputPrompter
from .preview import PreviewManager


class WizardRunner:
    """Main wizard orchestration class."""

    def __init__(self):
        """Initialize wizard components."""
        self.config_manager = ConfigManager()
        self.prompter = InputPrompter()
        self.preview_manager = PreviewManager()
        self.generator = HeroImageGenerator()
        self.theme_detector = ThemeDetector()

        # Current state
        self.config: Dict[str, Any] = {}
        self.title: str = ""
        self.tags: list = []
        self.year: int = 2025
        self.theme_override: Optional[str] = None
        self.output_path: str = ""

    def run(self) -> None:
        """Run the interactive wizard."""
        try:
            print("\n🎨 Hero Image Generator - Interactive Wizard\n")

            # Load saved preferences
            self.config = self.config_manager.load()
            if self.config != self.config_manager.get_default_config():
                print("✓ Using saved preferences from last session\n")

            # Initial input collection
            self._collect_initial_inputs()

            # Generate and preview
            self._generate_and_preview()

            # Refinement loop
            while not self.preview_manager.ask_satisfied():
                choice = self.preview_manager.show_refinement_menu()

                if choice == '0':
                    print("\n👋 Keeping current image")
                    break
                elif choice == '8':
                    self._collect_initial_inputs()
                    self._generate_and_preview()
                else:
                    self._handle_refinement(choice)
                    self._generate_and_preview()

            # Save final image
            self._save_final_image()

            # Save configuration
            self._save_config()

            print("\n✅ Done!\n")

        except KeyboardInterrupt:
            print("\n\n👋 Wizard cancelled\n")
            return

    def _collect_initial_inputs(self) -> None:
        """Collect initial user inputs."""
        # Title
        self.title = self.prompter.prompt_title()

        # Tags
        self.tags = self.prompter.prompt_tags()

        # Show detected theme
        theme = self.theme_detector.get_theme(self.tags)
        print(f"✓ Detected theme: {theme.name.replace('_', '/').upper()}")

        # Year
        self.year = self.prompter.prompt_year(self.config.get('last_year', 2025))

        # Ask about customization
        customize = input("\nCustomize colors/fonts? (y/n) [n]: ").strip().lower()

        if customize in ['y', 'yes']:
            self._collect_customizations()

    def _collect_customizations(self) -> None:
        """Collect color and font customizations."""
        # Accent color
        self.config['accent_color'] = self.prompter.prompt_color(
            "Accent color",
            tuple(self.config['accent_color'])
        )

        # Gradient colors
        customize_gradient = input("\nCustomize gradient? (y/n) [n]: ").strip().lower()
        if customize_gradient in ['y', 'yes']:
            self.config['gradient_start'] = self.prompter.prompt_color(
                "Gradient start",
                tuple(self.config['gradient_start'])
            )
            self.config['gradient_end'] = self.prompter.prompt_color(
                "Gradient end",
                tuple(self.config['gradient_end'])
            )

        # Font sizes
        customize_fonts = input("\nCustomize font sizes? (y/n) [n]: ").strip().lower()
        if customize_fonts in ['y', 'yes']:
            self._collect_font_sizes()

    def _collect_font_sizes(self) -> None:
        """Collect font size customizations."""
        print("\nCurrent font sizes:")
        print(f"  Title: {self.config['title_font_size']}px")
        print(f"  Subtitle: {self.config['subtitle_font_size']}px")
        print(f"  Year badge: {self.config['year_font_size']}px")

        change = input("\nChange font sizes? (y/n) [n]: ").strip().lower()
        if change not in ['y', 'yes']:
            return

        # Title font
        title_size = input(f"Title font size [{self.config['title_font_size']}]: ").strip()
        if title_size:
            self.config['title_font_size'] = int(title_size)

        # Subtitle font
        subtitle_size = input(f"Subtitle font size [{self.config['subtitle_font_size']}]: ").strip()
        if subtitle_size:
            self.config['subtitle_font_size'] = int(subtitle_size)

        # Year font
        year_size = input(f"Year badge font size [{self.config['year_font_size']}]: ").strip()
        if year_size:
            self.config['year_font_size'] = int(year_size)

    def _generate_and_preview(self) -> None:
        """Generate image and show preview."""
        # Generate temporary preview
        temp_filename = "temp-preview.png"

        print(f"\n⏳ Generating image...")
        self.output_path = self.generator.generate(
            self.title,
            self.tags,
            self.year,
            temp_filename
        )

        print(f"✅ Generated: {self.output_path}")
        print("🖼️  Opening preview...")

        self.preview_manager.open_preview(self.output_path)

    def _handle_refinement(self, choice: str) -> None:
        """Handle refinement menu choice."""
        if choice == '1':
            self.title = self.prompter.prompt_title()
        elif choice == '2':
            self.tags = self.prompter.prompt_tags()
            theme = self.theme_detector.get_theme(self.tags)
            print(f"✓ Detected theme: {theme.name.replace('_', '/').upper()}")
        elif choice == '3':
            self.year = self.prompter.prompt_year(self.year)
        elif choice == '4':
            print("\n[1] ai_ml  [2] seo_analytics  [3] automation  [4] strategy  [5] default")
            # TODO: Implement theme override
        elif choice == '5':
            self.config['accent_color'] = self.prompter.prompt_color(
                "Accent color",
                tuple(self.config['accent_color'])
            )
        elif choice == '6':
            self.config['gradient_start'] = self.prompter.prompt_color(
                "Gradient start",
                tuple(self.config['gradient_start'])
            )
            self.config['gradient_end'] = self.prompter.prompt_color(
                "Gradient end",
                tuple(self.config['gradient_end'])
            )
        elif choice == '7':
            self._collect_font_sizes()

    def _slugify(self, text: str) -> str:
        """Convert text to filename-safe slug."""
        # Convert to lowercase
        text = text.lower()
        # Replace spaces and special chars with hyphens
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        # Remove leading/trailing hyphens
        return text.strip('-')

    def _save_final_image(self) -> None:
        """Save the final image with user-specified name."""
        # Generate default filename from title
        default_filename = f"{self._slugify(self.title)}-hero.png"

        # Prompt for custom filename
        filename = self.preview_manager.prompt_output_filename(default_filename)

        # Ensure .png extension
        if not filename.endswith('.png'):
            filename += '.png'

        # Prompt for output directory
        output_dir = self.preview_manager.prompt_output_directory('public/images')

        # Generate final image
        self.generator.output_dir = output_dir
        final_path = self.generator.generate(
            self.title,
            self.tags,
            self.year,
            filename
        )

        print(f"\n✅ Saved: {final_path}")

    def _save_config(self) -> None:
        """Save configuration for next session."""
        # Update year
        self.config['last_year'] = self.year

        # Save
        self.config_manager.save(self.config)
        print("💾 Preferences saved for next session")


__all__ = ['WizardRunner']
```

**Step 4: Run test to verify pass**

```bash
pytest tests/wizard/test_wizard_runner.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add hero_image_generator/wizard/__init__.py tests/wizard/test_wizard_runner.py
git commit -m "feat(wizard): add WizardRunner orchestration class"
```

---

## Task 6: CLI Integration

**Files:**
- Modify: `hero_image_generator/cli.py:157-226`

**Step 1: Update CLI to detect no-args mode**

Modify `cli.py` function `main()` (around line 157):

Replace the current `main()` function with:
```python
def main():
    parser = argparse.ArgumentParser(
        description='Generate professional hero images with theme-based visual systems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive wizard (no arguments)
  %(prog)s

  # Generate single image
  %(prog)s --title "My Blog Post" --tags ai,ml --year 2025 --output my-hero.png

  # Generate preview samples
  %(prog)s --preview

  # Generate from metadata file
  %(prog)s --metadata posts.json

  # Generate with custom output directory
  %(prog)s --preview --output-dir ./images
        """
    )

    # Single image generation
    parser.add_argument('--title', help='Image title text')
    parser.add_argument('--tags', help='Comma-separated tags for theme detection (e.g., ai,ml,platform)')
    parser.add_argument('--year', type=int, default=2025, help='Year for badge (default: 2025)')
    parser.add_argument('--output', help='Output filename (e.g., my-hero.png)')

    # Batch generation
    parser.add_argument('--metadata', help='Generate from JSON metadata file')
    parser.add_argument('--filter-year', type=int, help='Only generate images for specific year')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without creating files')

    # Preview mode
    parser.add_argument('--preview', action='store_true', help='Generate preview samples for each theme')

    # Output options
    parser.add_argument('--output-dir', help='Output directory (default: public/images)')

    args = parser.parse_args()

    # NEW: No arguments = interactive wizard mode
    if len(sys.argv) == 1:
        from .wizard import WizardRunner
        wizard = WizardRunner()
        wizard.run()
        return

    # Preview mode
    if args.preview:
        generate_preview_samples(output_dir=args.output_dir)

    # Single image generation
    elif args.title and args.tags and args.output:
        tags = [tag.strip() for tag in args.tags.split(',')]
        generate_single_image(
            args.title,
            tags,
            args.year,
            args.output,
            output_dir=args.output_dir
        )

    # Batch generation from metadata
    elif args.metadata:
        generate_from_metadata(
            args.metadata,
            filter_year=args.filter_year,
            dry_run=args.dry_run,
            output_dir=args.output_dir
        )

    # Show help if no valid mode specified
    else:
        parser.print_help()
```

**Step 2: Test wizard launches with no args**

```bash
# This should launch wizard (will need Ctrl+C to exit for now)
python -m hero_image_generator
```

Expected: Wizard prompt appears

**Step 3: Test existing CLI still works**

```bash
python -m hero_image_generator --preview
```

Expected: Preview images generated (existing behavior)

**Step 4: Commit**

```bash
git add hero_image_generator/cli.py
git commit -m "feat(wizard): integrate wizard into CLI no-args mode"
```

---

## Task 7: Fix Test Imports and Verify All Tests Pass

**Files:**
- Previously modified in Task 1
- Run full test suite

**Step 1: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests pass (wizard and existing tests)

**Step 2: Generate test coverage report**

```bash
pytest tests/ --cov=hero_image_generator --cov-report=html
```

Expected: Coverage report generated in htmlcov/

**Step 3: Review coverage and add any missing tests**

Open `htmlcov/index.html` and check coverage for wizard modules.

**Step 4: Commit any additional tests**

```bash
git add tests/
git commit -m "test: add missing test coverage for wizard"
```

---

## Task 8: Manual Testing and Documentation

**Files:**
- Update: `README.md` (add wizard documentation)
- Update: `CLAUDE.md` (add wizard info)

**Step 1: Manual test - Complete wizard flow**

```bash
python -m hero_image_generator
```

Test checklist:
- [ ] Wizard launches
- [ ] Enter title, tags, year
- [ ] Theme detected and shown
- [ ] Image generates
- [ ] Preview opens (macOS/Linux/Windows specific)
- [ ] Answer "no" to satisfied
- [ ] Change title via refinement menu
- [ ] Image regenerates
- [ ] Answer "yes" to satisfied
- [ ] Save with custom filename
- [ ] Config saved to ~/.config/hero-image-generator/last-used.json
- [ ] Run wizard again, verify last year is default

**Step 2: Update README.md**

Add section after "Quick Start":

```markdown
### Interactive Wizard (Recommended)

Run without arguments to launch the interactive wizard:

```bash
python -m hero_image_generator
```

The wizard will:
1. Prompt for title, tags, and year
2. Auto-detect theme from tags
3. Generate and preview the image
4. Let you refine and regenerate until satisfied
5. Save your preferences for next time

Features:
- Live preview in your default image viewer
- Iterative refinement (change title, colors, fonts)
- Auto-saved preferences between sessions
- Color presets with custom hex/RGB support
```

**Step 3: Update CLAUDE.md**

Add to "Development Commands" section:

```markdown
### Interactive Wizard
```bash
# Launch wizard (no arguments)
python -m hero_image_generator

# Wizard will prompt for inputs and show live preview
# Config saved to ~/.config/hero-image-generator/last-used.json
```
```

**Step 4: Commit documentation**

```bash
git add README.md CLAUDE.md
git commit -m "docs: add interactive wizard documentation"
```

---

## Task 9: Final Integration and Cleanup

**Files:**
- Clean up temp files
- Final test run

**Step 1: Remove temp preview files if any**

```bash
rm -f public/images/temp-preview.png
```

**Step 2: Run full test suite one more time**

```bash
pytest tests/ -v --cov=hero_image_generator
```

Expected: All tests pass with good coverage

**Step 3: Test all CLI modes**

```bash
# Wizard mode
python -m hero_image_generator
# (Press Ctrl+C after it starts)

# Preview mode
python -m hero_image_generator --preview

# Single image mode
python -m hero_image_generator --title "Test" --tags ai,ml --output test.png

# Help
python -m hero_image_generator --help
```

**Step 4: Final commit**

```bash
git add .
git commit -m "feat: complete interactive wizard implementation

- ConfigManager for preference persistence
- InputPrompter with validation and color presets
- PreviewManager with platform-specific preview
- WizardRunner orchestration with refinement loop
- CLI integration via no-args detection
- Comprehensive test coverage
- Updated documentation

Closes #1"
```

**Step 5: Push to remote**

```bash
git push -u origin feature/interactive-wizard
```

---

## Success Criteria

- [ ] Wizard launches when run without arguments
- [ ] All existing CLI functionality unchanged
- [ ] Preview auto-opens on macOS, Linux, Windows
- [ ] Refinement loop allows changes and regeneration
- [ ] Preferences persist between sessions
- [ ] Color presets work, custom colors accepted
- [ ] Graceful error handling for all edge cases
- [ ] 90%+ test coverage for wizard modules
- [ ] Manual testing completed
- [ ] Documentation updated

## Next Steps

After implementation:
1. Create pull request to merge feature/interactive-wizard → main
2. Review code and test manually
3. Merge to main
4. Tag release (e.g., v1.1.0)
5. Update PyPI package
