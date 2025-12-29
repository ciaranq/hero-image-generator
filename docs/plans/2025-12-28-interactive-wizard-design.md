# Interactive CLI Wizard Design

**Date:** 2025-12-28
**Feature:** Interactive CLI wizard for hero image generation
**Status:** Approved for implementation

## Overview

Add an interactive CLI wizard that launches when the tool is run without arguments. The wizard provides step-by-step prompts for creating hero images with live preview, iterative refinement, and auto-saved preferences.

## User Experience

### Invocation
- `python -m hero_image_generator` (no arguments) → launches wizard
- All existing CLI flags continue to work unchanged (backward compatible)

### Workflow
1. User runs command without arguments
2. Wizard loads last-used preferences (if available)
3. Step-by-step prompts collect: title, tags, year, optional theme override, optional color/font customization
4. Generate image and auto-open in system default viewer
5. Ask "Satisfied? (y/n)"
   - If yes: Save with custom filename, persist preferences, exit
   - If no: Show refinement menu, allow selective changes, regenerate, repeat
6. Save final image and preferences

### Key Features
- **Auto-open preview**: Image opens in default viewer (Preview on macOS, etc.)
- **Iterative refinement**: Change title, tags, colors, fonts and regenerate until satisfied
- **Auto-save preferences**: Visual settings (colors, fonts) persist between sessions
- **Named color presets**: Quick selection (purple, green, orange, etc.) with custom hex/RGB option
- **Smart defaults**: Last-used settings offered as defaults

## Architecture

### File Structure
```
hero_image_generator/
├── wizard/
│   ├── __init__.py          # WizardRunner class
│   ├── prompt.py            # InputPrompter class
│   ├── config.py            # ConfigManager class
│   └── preview.py           # PreviewManager class
├── cli.py                   # Modified: detect no-args mode
└── ...
```

### Core Classes

#### 1. WizardRunner (`wizard/__init__.py`)
Orchestrates the entire wizard flow.

**Responsibilities:**
- Load configuration on startup
- Run input prompts
- Generate image and trigger preview
- Handle refinement loop
- Save configuration on successful completion

**Key methods:**
- `run()` - Main entry point
- `_initial_generation()` - First image creation
- `_refinement_loop()` - Handle changes and regeneration

#### 2. InputPrompter (`wizard/prompt.py`)
Handles all user input with validation.

**Prompts:**
- Title (required, max 100 chars)
- Tags (comma-separated, auto-detects theme)
- Year (validated 1900-2099, default from config)
- Theme override (numbered menu, shows detected theme)
- Advanced customization gate (y/n)
- Color pickers (named presets + custom hex/RGB)
- Font sizes (if requested)

**Key methods:**
- `prompt_title()` - Returns validated title string
- `prompt_tags()` - Returns list of tags, shows detected theme
- `prompt_year(default)` - Returns year integer
- `prompt_theme_override(detected)` - Returns theme name or None
- `prompt_color(name, default)` - Returns RGB tuple
- `prompt_font_size(name, default)` - Returns integer

#### 3. ConfigManager (`wizard/config.py`)
Manages configuration persistence.

**Storage location:**
- `~/.config/hero-image-generator/last-used.json` (Linux/macOS)
- `%APPDATA%/hero-image-generator/last-used.json` (Windows)

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

**NOT saved:**
- Title (always fresh)
- Tags (content-specific)
- Output filename

**Key methods:**
- `load()` - Returns config dict or defaults
- `save(config)` - Persists to JSON file
- `get_config_path()` - Platform-specific path resolution

#### 4. PreviewManager (`wizard/preview.py`)
Handles image preview and refinement.

**Responsibilities:**
- Open image in system default viewer
- Present refinement menu
- Coordinate regeneration

**Key methods:**
- `open_preview(image_path)` - Platform-specific viewer launch
- `show_refinement_menu()` - Display options, return choice
- `prompt_for_change(field, current_value)` - Get new value for specific field

### CLI Integration

**Modified `cli.py`:**
```python
def main():
    parser = argparse.ArgumentParser(...)
    args = parser.parse_args()

    # NEW: No arguments = wizard mode
    if len(sys.argv) == 1:
        from .wizard import WizardRunner
        wizard = WizardRunner()
        wizard.run()
        return

    # Existing CLI behavior unchanged
    if args.preview:
        generate_preview_samples(...)
    elif args.metadata:
        generate_from_metadata(...)
    # ...
```

**Backward compatibility:**
- All existing flags work exactly as before
- Only change: running without args launches wizard instead of showing help

## Input Flow

### Initial Prompts
1. **Title**: `Enter image title: _`
2. **Tags**: `Enter tags (comma-separated): _` → Shows detected theme
3. **Year**: `Year [2025]: _` → Default from config
4. **Theme override**: Numbered menu with detected theme as default
5. **Customization gate**: `Customize colors/fonts? (y/n) [n]: _`
6. **If customization = yes**:
   - Accent color (named presets + custom)
   - Gradient colors (named presets + custom)
   - Font sizes (optional sub-gate)

### Refinement Menu
```
What would you like to change?
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

After each change: regenerate → preview → "Satisfied?" → loop

## Error Handling

### Preview Opening Failures
- Try platform-specific command (`open`, `xdg-open`, `os.startfile`)
- On failure: show error + file path for manual opening
- Continue wizard (non-fatal)

### Config File Issues
- Missing file: use defaults silently
- Corrupted JSON: show warning, use defaults
- Partial config: merge with defaults

### Invalid Input
- Year: re-prompt if not numeric or out of range
- Colors: validate hex format or RGB tuple, re-prompt if invalid
- Empty required fields: loop until non-empty
- Optional fields: Enter = keep default

### Keyboard Interrupt (Ctrl+C)
- Clean exit with message: "👋 Wizard cancelled"
- No stack trace shown

### File Write Failures
- Permission denied: actionable error message
- Disk full / OSError: specific error message

## Testing Strategy

### Unit Tests

**`test_wizard_config.py`:**
- Round-trip persistence
- Missing file handling
- Corrupted JSON handling
- Directory creation
- Partial config merging

**`test_wizard_prompt.py`:**
- Year validation (range checks)
- Hex color validation (`#8B5CF6`, `8B5CF6`)
- RGB validation (`139,92,246`)
- Tag parsing (spaces, case)
- Theme detection display
- Mock `input()` for automation

**`test_wizard_preview.py`:**
- Platform-specific preview commands
- Subprocess failure handling
- Mock `subprocess.run()`

**`test_wizard_integration.py`:**
- Full wizard flow simulation
- Refinement loop
- Config persistence
- Mock `input()` and file operations

### Manual Testing
- [ ] Test on macOS, Linux, Windows
- [ ] Verify preview opens on each platform
- [ ] Config persists between sessions
- [ ] All refinement options work
- [ ] Ctrl+C handling
- [ ] Invalid inputs handled
- [ ] Corrupted config recovery
- [ ] File overwrite prompts

## Implementation Notes

### Dependencies
- No new external dependencies required
- Uses stdlib: `subprocess`, `json`, `pathlib`, `sys`, `os`

### Color Presets
```python
COLOR_PRESETS = {
    'purple': (139, 92, 246),
    'green': (34, 197, 94),
    'orange': (249, 115, 22),
    'cyan': (6, 182, 212),
    'red': (239, 68, 68),
    'blue': (59, 130, 246),
}
```

### Platform Detection
```python
if sys.platform == 'darwin':
    subprocess.run(['open', image_path])
elif sys.platform == 'win32':
    os.startfile(image_path)
else:  # Linux and others
    subprocess.run(['xdg-open', image_path])
```

### File Naming
- Auto-generate from title: slugify (`"AI Agent Platform"` → `ai-agent-platform-hero.png`)
- Allow override: `Save as [ai-agent-platform-hero.png]: _`
- Check existence, prompt to overwrite if needed

## Success Criteria

- [ ] Wizard launches when run without arguments
- [ ] All existing CLI functionality unchanged
- [ ] Preview auto-opens on macOS, Linux, Windows
- [ ] Refinement loop allows changes and regeneration
- [ ] Preferences persist between sessions
- [ ] Color presets work, custom colors accepted
- [ ] Graceful error handling for all edge cases
- [ ] 90%+ test coverage for wizard modules
- [ ] Manual testing completed on all platforms

## Future Enhancements (Out of Scope)

- Web-based UI
- Batch wizard mode (multiple images in one session)
- Template/preset management UI
- Undo/redo in refinement
- Side-by-side comparison of variations
