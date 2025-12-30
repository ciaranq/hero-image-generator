"""Tests for CLI entry point"""

import sys
from unittest.mock import MagicMock, Mock, patch
from pathlib import Path
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


@patch('hero_image_generator.cli.CostTracker')
@patch('hero_image_generator.cli.FluxModel')
@patch('hero_image_generator.cli.AIConfig')
def test_cli_ai_mode_flag(mock_config, mock_flux, mock_cost_tracker, monkeypatch):
    """Test --ai flag generates with AI model."""
    monkeypatch.setattr('sys.argv', [
        'hero-image-generator',
        '--ai',
        '--prompt', 'Test prompt',
        '--model', 'flux-pro',
        '--size', 'medium',
        '--output', 'test.png'
    ])

    # Mock config
    mock_config_instance = Mock()
    mock_config_instance.size_medium = (1920, 1080)
    mock_config_instance.cost_log_file = '/tmp/cost.log'
    mock_config_instance.log_costs = False
    mock_config_instance.enable_quality_check = False
    mock_config_instance.output_directory = '/tmp'
    mock_config.load.return_value = mock_config_instance

    # Mock model
    mock_model_instance = Mock()
    mock_model_instance.name = 'Flux Pro'
    mock_model_instance.generate.return_value = Path('test.png')
    mock_model_instance.get_cost_per_image.return_value = 0.055
    mock_flux.return_value = mock_model_instance

    # Mock cost tracker
    mock_tracker_instance = Mock()
    mock_tracker_instance.display_summary.return_value = 'Cost summary'
    mock_cost_tracker.return_value = mock_tracker_instance

    # Import main here to avoid premature imports
    from hero_image_generator.cli import main

    # Run CLI
    main()

    # Verify
    mock_flux.assert_called_once()
    mock_model_instance.generate.assert_called_once()
