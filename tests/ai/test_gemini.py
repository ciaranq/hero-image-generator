"""Tests for Gemini/Imagen model integration."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from hero_image_generator.ai.gemini import GeminiModel
from hero_image_generator.ai.config import AIConfig
from hero_image_generator.ai.base import GenerationError


@pytest.fixture
def mock_config(monkeypatch):
    """Fixture providing valid AIConfig for testing."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token_123')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')
    monkeypatch.setenv('GCP_LOCATION', 'us-central1')
    return AIConfig.load()


@patch('hero_image_generator.ai.gemini.aiplatform.init')
def test_gemini_model_name(mock_aiplatform_init, mock_config):
    """Test Gemini model has correct name based on variant."""
    # Test Imagen variant
    imagen_model = GeminiModel(mock_config, use_imagen=True)
    assert imagen_model.name == 'Imagen'

    # Test Gemini 2.0 Flash variant
    flash_model = GeminiModel(mock_config, use_imagen=False)
    assert flash_model.name == 'Gemini 2.0 Flash'


@patch('hero_image_generator.ai.gemini.aiplatform.init')
def test_gemini_cost(mock_aiplatform_init, mock_config):
    """Test Gemini cost is correct."""
    model = GeminiModel(mock_config, use_imagen=True)
    assert model.get_cost_per_image() == 0.020


@patch('hero_image_generator.ai.gemini.aiplatform.init')
@patch('hero_image_generator.ai.gemini.ImageGenerationModel.from_pretrained')
def test_imagen_generate_success(mock_from_pretrained, mock_aiplatform_init, mock_config, tmp_path):
    """Test successful image generation with Imagen."""
    # Mock the model and response
    mock_model_instance = Mock()
    mock_from_pretrained.return_value = mock_model_instance

    # Mock generate_images response
    mock_image = Mock()
    mock_image._image_bytes = b'fake_image_data'
    mock_response = Mock()
    mock_response.images = [mock_image]
    mock_model_instance.generate_images.return_value = mock_response

    # Generate image
    model = GeminiModel(mock_config, use_imagen=True)
    output_path = tmp_path / 'output.png'
    result = model.generate(
        prompt='A beautiful sunset',
        size=(1200, 630),
        output_path=output_path
    )

    # Verify Vertex AI initialization
    mock_aiplatform_init.assert_called_once_with(
        project='test_project',
        location='us-central1'
    )

    # Verify model was loaded
    mock_from_pretrained.assert_called_once_with('imagegeneration@006')

    # Verify generate_images was called with correct parameters
    mock_model_instance.generate_images.assert_called_once()
    call_kwargs = mock_model_instance.generate_images.call_args[1]
    assert call_kwargs['prompt'] == 'A beautiful sunset'
    assert call_kwargs['number_of_images'] == 1
    assert 'aspect_ratio' in call_kwargs

    # Verify file was written
    assert result == output_path
    assert output_path.exists()
    assert output_path.read_bytes() == b'fake_image_data'


@patch('hero_image_generator.ai.gemini.aiplatform.init')
@patch('hero_image_generator.ai.gemini.ImageGenerationModel.from_pretrained')
def test_imagen_generate_api_failure(mock_from_pretrained, mock_aiplatform_init, mock_config, tmp_path):
    """Test handling of API failures."""
    # Mock API error
    mock_from_pretrained.side_effect = Exception('Vertex AI connection failed')

    model = GeminiModel(mock_config, use_imagen=True)
    output_path = tmp_path / 'output.png'

    with pytest.raises(GenerationError, match='Failed to generate image'):
        model.generate(
            prompt='Test prompt',
            size=(1200, 630),
            output_path=output_path
        )


@patch('hero_image_generator.ai.gemini.aiplatform.init')
def test_aspect_ratio_calculation(mock_aiplatform_init, mock_config):
    """Test aspect ratio calculation for different sizes."""
    model = GeminiModel(mock_config, use_imagen=True)

    # Test square (1:1)
    assert model._calculate_aspect_ratio(1000, 1000) == '1:1'

    # Test portrait (3:4)
    assert model._calculate_aspect_ratio(900, 1200) == '3:4'

    # Test landscape (4:3)
    assert model._calculate_aspect_ratio(1200, 900) == '4:3'

    # Test tall portrait (9:16)
    assert model._calculate_aspect_ratio(720, 1280) == '9:16'

    # Test wide landscape (16:9)
    assert model._calculate_aspect_ratio(1280, 720) == '16:9'

    # Test hero image size (closest to 16:9)
    assert model._calculate_aspect_ratio(1200, 630) == '16:9'
