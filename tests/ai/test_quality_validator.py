"""Tests for quality validation using Gemini Vision."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from hero_image_generator.ai.quality_validator import QualityValidator, ValidationResult
from hero_image_generator.ai.config import AIConfig


@pytest.fixture
def mock_config(monkeypatch):
    """Create mock AIConfig for testing."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')
    monkeypatch.setenv('MIN_QUALITY_SCORE', '0.6')
    return AIConfig.load()


def test_validation_result_pass():
    """Test ValidationResult for passing validation."""
    result = ValidationResult(
        passed=True,
        score=0.85,
        feedback='Good match',
        cost=0.001
    )

    assert result.passed is True
    assert result.score == 0.85
    assert result.feedback == 'Good match'
    assert result.cost == 0.001


def test_validation_result_fail():
    """Test ValidationResult for failing validation."""
    result = ValidationResult(
        passed=False,
        score=0.45,
        feedback='Poor match',
        cost=0.001
    )

    assert result.passed is False
    assert result.score == 0.45


@patch('hero_image_generator.ai.quality_validator.aiplatform')
@patch('hero_image_generator.ai.quality_validator.GenerativeModel')
def test_validate_image_success(mock_gen_model, mock_aiplatform, mock_config, tmp_path):
    """Test successful image validation."""
    # Create fake image
    image_path = tmp_path / 'test.png'
    image_path.write_bytes(b'fake_image_data')

    # Mock Vertex AI initialization
    mock_aiplatform.init = Mock()

    # Mock Gemini response with JSON
    mock_response = Mock()
    mock_response.text = '{"score": 0.85, "breakdown": {"subject": 0.35, "style": 0.25, "quality": 0.25}, "issues": []}'

    mock_model_instance = Mock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_gen_model.return_value = mock_model_instance

    # Validate
    validator = QualityValidator(mock_config)
    result = validator.validate(image_path, 'Test prompt')

    # Verify
    assert result.passed is True
    assert result.score == 0.85
    assert result.cost == 0.001
    mock_aiplatform.init.assert_called_once()


@patch('hero_image_generator.ai.quality_validator.aiplatform')
@patch('hero_image_generator.ai.quality_validator.GenerativeModel')
def test_validate_image_fail(mock_gen_model, mock_aiplatform, mock_config, tmp_path):
    """Test image validation failure."""
    image_path = tmp_path / 'test.png'
    image_path.write_bytes(b'fake_image_data')

    mock_aiplatform.init = Mock()

    # Mock low score response
    mock_response = Mock()
    mock_response.text = '{"score": 0.45, "breakdown": {"subject": 0.15, "style": 0.15, "quality": 0.15}, "issues": ["Poor subject match"]}'

    mock_model_instance = Mock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_gen_model.return_value = mock_model_instance

    # Validate
    validator = QualityValidator(mock_config)
    result = validator.validate(image_path, 'Test prompt')

    # Verify
    assert result.passed is False
    assert result.score == 0.45
    assert 'Poor subject match' in result.feedback


@patch('hero_image_generator.ai.quality_validator.aiplatform')
@patch('hero_image_generator.ai.quality_validator.GenerativeModel')
def test_validate_handles_non_json_response(mock_gen_model, mock_aiplatform, mock_config, tmp_path):
    """Test validation handles non-JSON response gracefully."""
    image_path = tmp_path / 'test.png'
    image_path.write_bytes(b'fake_image_data')

    mock_aiplatform.init = Mock()

    # Mock non-JSON response
    mock_response = Mock()
    mock_response.text = 'This image is great! Score: 0.85'

    mock_model_instance = Mock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_gen_model.return_value = mock_model_instance

    # Validate
    validator = QualityValidator(mock_config)
    result = validator.validate(image_path, 'Test prompt')

    # Should extract score from text
    assert result.score == 0.85
    assert result.passed is True


def test_validate_missing_image(mock_config):
    """Test validation with missing image file."""
    validator = QualityValidator(mock_config)

    with pytest.raises(FileNotFoundError):
        validator.validate(Path('nonexistent.png'), 'Test prompt')
