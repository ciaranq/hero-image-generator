"""Integration tests for Gemini/Imagen API.

These tests make real API calls and are skipped by default.
Run with: pytest tests/integration/test_gemini_integration.py --run-slow
"""
import pytest
from pathlib import Path
from hero_image_generator.ai import AIConfig, GeminiModel, QualityValidator


@pytest.fixture
def real_config():
    """Load real AIConfig from environment."""
    try:
        return AIConfig.load()
    except Exception as e:
        pytest.skip(f'Could not load AI config: {e}')


@pytest.mark.slow
@pytest.mark.requires_api_keys
@pytest.mark.integration
def test_imagen_real_generation(real_config, tmp_path):
    """Test real Imagen generation."""
    model = GeminiModel(real_config, use_imagen=True)
    output_path = tmp_path / 'imagen_test.png'

    result = model.generate(
        prompt='Professional hero image with abstract technology patterns',
        size=(1920, 1080),
        output_path=output_path
    )

    assert result.exists()
    assert result.stat().st_size > 0
    print(f'Generated image: {result}')
    print(f'Cost: ${model.get_cost_per_image()}')


@pytest.mark.slow
@pytest.mark.requires_api_keys
@pytest.mark.integration
def test_quality_validation_real(real_config, tmp_path):
    """Test real quality validation with Gemini Vision."""
    # First generate an image
    model = GeminiModel(real_config, use_imagen=True)
    image_path = tmp_path / 'test.png'

    prompt = 'Professional hero image with blue gradients'
    model.generate(prompt, (800, 450), image_path)

    # Validate it
    validator = QualityValidator(real_config)
    result = validator.validate(image_path, prompt)

    assert result.score >= 0.0
    assert result.score <= 1.0
    assert result.cost > 0
    print(f'Validation score: {result.score}')
    print(f'Feedback: {result.feedback}')
    print(f'Passed: {result.passed}')
