"""Tests for AI wizard flow."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from hero_image_generator.wizard.ai_wizard import AIWizardRunner


@pytest.fixture
def mock_config(monkeypatch, tmp_path):
    """Mock environment for AI wizard."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')
    monkeypatch.setenv('OUTPUT_DIRECTORY', str(tmp_path))
    return tmp_path


def test_ai_wizard_initialization(mock_config):
    """Test AI wizard initializes correctly."""
    wizard = AIWizardRunner()
    assert wizard.config is not None
    assert wizard.cost_tracker is not None


@patch('hero_image_generator.wizard.ai_wizard.input')
def test_collect_prompt(mock_input, mock_config):
    """Test prompt collection."""
    mock_input.return_value = 'Professional hero image for AI consultancy'

    wizard = AIWizardRunner()
    prompt = wizard._collect_prompt()

    assert prompt == 'Professional hero image for AI consultancy'


@patch('hero_image_generator.wizard.ai_wizard.input')
def test_select_model_flux_pro(mock_input, mock_config):
    """Test model selection for Flux Pro."""
    mock_input.return_value = '1'  # Flux Pro

    wizard = AIWizardRunner()
    model = wizard._select_model()

    assert model.name == 'Flux Pro'


@patch('hero_image_generator.wizard.ai_wizard.input')
def test_select_size_medium(mock_input, mock_config):
    """Test size selection."""
    mock_input.return_value = '2'  # Medium

    wizard = AIWizardRunner()
    size = wizard._select_size()

    assert size == (1920, 1080)


@patch('hero_image_generator.wizard.ai_wizard.input')
def test_refinement_regenerate(mock_input, mock_config):
    """Test refinement choice - regenerate."""
    mock_input.return_value = '1'

    wizard = AIWizardRunner()
    choice = wizard._show_refinement_menu()

    assert choice == 'regenerate'


@patch('hero_image_generator.wizard.ai_wizard.input')
def test_refinement_modify_prompt(mock_input, mock_config):
    """Test refinement choice - modify prompt."""
    mock_input.return_value = '2'

    wizard = AIWizardRunner()
    choice = wizard._show_refinement_menu()

    assert choice == 'modify_prompt'
