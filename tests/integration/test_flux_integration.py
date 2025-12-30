"""Integration tests for Flux API.

These tests make real API calls and are skipped by default.
Run with: pytest tests/integration/test_flux_integration.py --run-slow
"""
import pytest
from pathlib import Path
from hero_image_generator.ai import AIConfig, FluxModel, GenerationError


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
def test_flux_schnell_real_generation(real_config, tmp_path):
    """Test real Flux Schnell generation (cheapest/fastest for testing)."""
    model = FluxModel(real_config, variant='schnell')
    output_path = tmp_path / 'flux_test.png'

    result = model.generate(
        prompt='Simple geometric hero image with blue and purple gradients',
        size=(800, 450),  # Small size for speed
        output_path=output_path
    )

    assert result.exists()
    assert result.stat().st_size > 0
    print(f'Generated image: {result}')
    print(f'Cost: ${model.get_cost_per_image()}')


@pytest.mark.slow
@pytest.mark.requires_api_keys
@pytest.mark.integration
def test_flux_pro_real_generation(real_config, tmp_path):
    """Test real Flux Pro generation (expensive - only run manually)."""
    pytest.skip('Expensive test - only run manually')

    model = FluxModel(real_config, variant='pro')
    output_path = tmp_path / 'flux_pro_test.png'

    result = model.generate(
        prompt='Professional hero image for AI consultancy, modern design',
        size=(1920, 1080),
        output_path=output_path
    )

    assert result.exists()
    print(f'Generated image: {result}')
    print(f'Cost: ${model.get_cost_per_image()}')
