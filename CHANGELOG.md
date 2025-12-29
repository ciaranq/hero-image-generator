# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-29

### Added

#### Interactive CLI Wizard
- Interactive wizard launched when running without arguments
- Step-by-step prompts for title, tags, year, and customization options
- Live preview functionality that auto-opens images in system default viewer
- Iterative refinement loop allowing users to modify any aspect and regenerate
- Preference persistence system saving settings to `~/.config/hero-image-generator/last-used.json`
- Color preset system with 6 built-in colors plus custom hex/RGB input
- Cross-platform preview support (macOS, Linux, Windows)
- Smart filename generation from title with custom override option
- Graceful error handling with non-fatal preview failures

#### Wizard Components
- **ConfigManager** - Preference persistence with platform-specific paths
- **InputPrompter** - User input validation for titles, tags, colors, fonts
- **PreviewManager** - Cross-platform image preview and refinement workflow
- **WizardRunner** - Main orchestration class coordinating all components

#### Documentation
- Comprehensive wizard documentation in CLAUDE.md
- Interactive wizard section in README.md
- Demo screenshots for all 4 themes (AI/ML, SEO, Automation, Strategy)
- Complete wizard walkthrough in `docs/screenshots/WIZARD_DEMO.md`
- Architecture Decision Record (ADR-001)
- Implementation plan and design documents

#### Testing
- 59 new wizard tests (72 tests total)
- 62% overall code coverage
- 94-100% coverage for core wizard modules
- Cross-platform test coverage with platform mocking
- CLI integration tests for backward compatibility

### Changed
- CLI behavior: Running without arguments launches wizard instead of showing help
- All existing CLI flags remain unchanged and fully functional

### Technical Details
- 759 lines of new wizard code
- Modular architecture with 4 components
- Test-first development methodology
- Platform abstraction for cross-platform support
- Lazy-loaded wizard to minimize CLI startup overhead

## [1.0.0] - 2025-12-28

### Added
- Initial release of Hero Image Generator
- Theme-based visual system with 4 pre-defined themes:
  - AI/ML (purple, connected node networks)
  - SEO/Analytics (green, rising charts)
  - Automation (orange, interlocking gears)
  - Strategy (cyan, hierarchical org charts)
- Automatic theme detection from tags
- 1200x630px Open Graph optimized image generation
- CLI with three modes:
  - Single image generation (`--title --tags --output`)
  - Preview mode (`--preview`) for theme samples
  - Batch mode (`--metadata`) from JSON metadata
- Cross-platform font fallback system
- 13 core tests with basic coverage

### Technical Details
- Python 3.8+ support
- Pillow 10.0.0+ as only runtime dependency
- 7-step image generation pipeline
- Theme-specific visual renderers
- Configurable output directory

---

## Release Links

- [v1.1.0](https://github.com/ciaranq/hero-image-generator/releases/tag/v1.1.0) - Interactive CLI Wizard
- v1.0.0 - Initial Release

## Upgrade Guide

### Upgrading to v1.1.0 from v1.0.0

No breaking changes. All existing commands work exactly as before.

**New feature to try:**
```bash
# Just run without arguments to launch the wizard
python -m hero_image_generator
```

**Existing commands still work:**
```bash
# These all continue to work unchanged
python -m hero_image_generator --preview
python -m hero_image_generator --title "My Title" --tags ai,ml --output hero.png
python -m hero_image_generator --metadata content.json
```

The only change: Running without arguments launches the wizard instead of showing help. Use `--help` to show help.

## Contributing

When adding entries to this changelog:
- Use present tense ("Add feature" not "Added feature")
- Reference PR numbers and issues where applicable
- Group changes by type: Added, Changed, Deprecated, Removed, Fixed, Security
- Link to migration guides for breaking changes
