"""Tests for CLI entry point"""

import sys
from unittest.mock import MagicMock
import pytest


def test_main_no_args_launches_wizard(monkeypatch):
    """When called with no arguments, main() launches interactive wizard"""
    # Mock sys.argv to have just program name
    monkeypatch.setattr('sys.argv', ['hero-image-generator'])

    # Mock WizardRunner to track instantiation and run() calls
    wizard_run_called = []

    class MockWizardRunner:
        def __init__(self):
            pass

        def run(self):
            wizard_run_called.append(True)

    # Patch WizardRunner in the wizard module (where it's imported from)
    import hero_image_generator.wizard
    monkeypatch.setattr('hero_image_generator.wizard.WizardRunner', MockWizardRunner)

    # Import and call main
    from hero_image_generator.cli import main
    main()

    # Verify wizard.run() was called
    assert len(wizard_run_called) == 1


def test_main_with_preview_flag_still_works(monkeypatch, capsys):
    """Existing --preview flag should still work, not launch wizard"""
    monkeypatch.setattr('sys.argv', ['hero-image-generator', '--preview'])

    # Mock the generate_preview_samples function
    preview_called = []
    def mock_preview(output_dir=None):
        preview_called.append(True)

    from hero_image_generator import cli
    monkeypatch.setattr('hero_image_generator.cli.generate_preview_samples', mock_preview)

    # Call main
    cli.main()

    # Verify preview was called, not wizard
    assert len(preview_called) == 1


def test_main_with_title_tags_output_still_works(monkeypatch):
    """Existing single image generation should still work"""
    monkeypatch.setattr('sys.argv', [
        'hero-image-generator',
        '--title', 'Test Title',
        '--tags', 'ai,ml',
        '--output', 'test.png'
    ])

    # Mock generate_single_image
    single_called = []
    def mock_single(title, tags, year, output, output_dir=None):
        single_called.append((title, tags))
        return '/fake/path/test.png'

    from hero_image_generator import cli
    monkeypatch.setattr('hero_image_generator.cli.generate_single_image', mock_single)

    # Call main
    cli.main()

    # Verify single image generation was called
    assert len(single_called) == 1
    assert single_called[0][0] == 'Test Title'
    assert single_called[0][1] == ['ai', 'ml']
