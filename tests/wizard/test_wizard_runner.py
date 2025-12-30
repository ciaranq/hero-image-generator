from unittest import mock
from unittest.mock import patch
from hero_image_generator.wizard import WizardRunner


def test_wizard_runner_initialization():
    """Should initialize with all required components"""
    with mock.patch('hero_image_generator.wizard.config.ConfigManager'):
        with mock.patch('hero_image_generator.wizard.prompt.InputPrompter'):
            with mock.patch('hero_image_generator.wizard.preview.PreviewManager'):
                runner = WizardRunner()
                assert runner is not None


@patch('hero_image_generator.wizard.input')
def test_wizard_mode_selection_programmatic(mock_input):
    """Test selecting programmatic mode."""
    mock_input.return_value = '1'

    wizard = WizardRunner()
    mode = wizard._select_mode()

    assert mode == 'programmatic'


@patch('hero_image_generator.wizard.input')
def test_wizard_mode_selection_ai(mock_input):
    """Test selecting AI mode."""
    mock_input.return_value = '2'

    wizard = WizardRunner()
    mode = wizard._select_mode()

    assert mode == 'ai'
