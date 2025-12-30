"""Tests for Flux model integration."""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from hero_image_generator.ai.flux import FluxModel
from hero_image_generator.ai.config import AIConfig
from hero_image_generator.ai.base import GenerationError


@pytest.fixture
def mock_config(monkeypatch):
    """Fixture providing valid AIConfig for testing."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token_123')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')
    return AIConfig.load()


def test_flux_pro_model_name(mock_config):
    """Test Flux Pro model has correct name."""
    model = FluxModel(mock_config, variant='pro')
    assert model.name == 'Flux Pro'


def test_flux_dev_model_name(mock_config):
    """Test Flux Dev model has correct name."""
    model = FluxModel(mock_config, variant='dev')
    assert model.name == 'Flux Dev'


def test_flux_schnell_model_name(mock_config):
    """Test Flux Schnell model has correct name."""
    model = FluxModel(mock_config, variant='schnell')
    assert model.name == 'Flux Schnell'


def test_flux_pro_cost(mock_config):
    """Test Flux Pro cost is correct."""
    model = FluxModel(mock_config, variant='pro')
    assert model.get_cost_per_image() == 0.055


def test_flux_dev_cost(mock_config):
    """Test Flux Dev cost is correct."""
    model = FluxModel(mock_config, variant='dev')
    assert model.get_cost_per_image() == 0.020


def test_flux_schnell_cost(mock_config):
    """Test Flux Schnell cost is correct."""
    model = FluxModel(mock_config, variant='schnell')
    assert model.get_cost_per_image() == 0.010


@patch('hero_image_generator.ai.flux.requests.get')
@patch('hero_image_generator.ai.flux.replicate.run')
def test_flux_generate_success(mock_replicate_run, mock_requests_get, mock_config, tmp_path):
    """Test successful image generation."""
    # Mock Replicate API returning image URL
    mock_replicate_run.return_value = 'https://example.com/generated.png'

    # Mock requests.get returning image bytes
    mock_response = Mock()
    mock_response.content = b'fake_image_data'
    mock_requests_get.return_value = mock_response

    # Generate image
    model = FluxModel(mock_config, variant='pro')
    output_path = tmp_path / 'output.png'
    result = model.generate(
        prompt='A beautiful sunset',
        size=(1200, 630),
        output_path=output_path
    )

    # Verify API calls
    mock_replicate_run.assert_called_once()
    call_args = mock_replicate_run.call_args
    assert 'black-forest-labs/flux-1.1-pro' in call_args[0][0]
    assert call_args[1]['input']['prompt'] == 'A beautiful sunset'
    assert call_args[1]['input']['width'] == 1200
    assert call_args[1]['input']['height'] == 630

    mock_requests_get.assert_called_once_with('https://example.com/generated.png')

    # Verify file was written
    assert result == output_path
    assert output_path.exists()
    assert output_path.read_bytes() == b'fake_image_data'


@patch('hero_image_generator.ai.flux.replicate.run')
def test_flux_generate_api_failure(mock_replicate_run, mock_config, tmp_path):
    """Test handling of API failures."""
    # Mock API error
    mock_replicate_run.side_effect = Exception('API connection failed')

    model = FluxModel(mock_config, variant='dev')
    output_path = tmp_path / 'output.png'

    with pytest.raises(GenerationError, match='Failed to generate image'):
        model.generate(
            prompt='Test prompt',
            size=(1200, 630),
            output_path=output_path
        )


def test_flux_invalid_variant(mock_config):
    """Test invalid variant raises ValueError."""
    with pytest.raises(ValueError, match='Invalid variant'):
        FluxModel(mock_config, variant='invalid')
