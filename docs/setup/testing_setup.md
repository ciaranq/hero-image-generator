# Testing Setup Guide

Guide for running tests in the hero-image-generator project.

## Test Structure

```
tests/
├── ai/                        # Unit tests for AI module (mocked)
│   ├── test_config.py
│   ├── test_flux.py
│   ├── test_gemini.py
│   ├── test_cost_tracker.py
│   └── test_quality_validator.py
├── integration/               # Integration tests (real APIs)
│   ├── test_flux_integration.py
│   └── test_gemini_integration.py
├── wizard/                    # Wizard tests
│   ├── test_ai_wizard.py
│   └── ...
└── test_cli.py               # CLI tests
```

## Running Unit Tests

Unit tests use mocked APIs and run quickly without incurring costs.

```bash
# Run all unit tests
pytest tests/ -v

# Run specific module
pytest tests/ai/ -v

# Run with coverage report
pytest tests/ --cov=hero_image_generator --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Running Integration Tests

Integration tests make real API calls and incur costs.

### Prerequisites

1. Complete [Replicate Setup](replicate_setup.md)
2. Complete [GCP Setup](gcp_setup.md)
3. Ensure `.env` has valid credentials

### Run Integration Tests

```bash
# Run all integration tests (~$0.04 cost)
pytest tests/integration/ --run-slow -v

# Run only Flux tests (~$0.01)
pytest tests/integration/test_flux_integration.py --run-slow -v

# Run only Gemini tests (~$0.02)
pytest tests/integration/test_gemini_integration.py --run-slow -v
```

### Cost Breakdown

| Test | API Calls | Cost |
|------|-----------|------|
| Flux Schnell | 1 generation | $0.01 |
| Flux Pro | 1 generation | $0.055 (skipped by default) |
| Imagen | 1 generation | $0.02 |
| Quality validation | 1 generation + 1 validation | $0.021 |

**Total per full run:** ~$0.04 (with expensive tests skipped)

## Test Markers

Tests use pytest markers for categorization:

```python
@pytest.mark.slow              # Slow tests (integration)
@pytest.mark.requires_api_keys # Needs real API keys
@pytest.mark.integration       # Integration test
```

### Run Only Unit Tests

```bash
pytest tests/ -v -m "not slow"
```

### Run Only Integration Tests

```bash
pytest tests/ -v -m "integration"
```

## Test Configuration

See `pytest.ini`:

```ini
[pytest]
markers =
    slow: marks tests as slow (requires --run-slow flag)
    requires_api_keys: marks tests that need real API keys
    integration: marks integration tests
```

## Continuous Integration

For CI/CD pipelines:

```yaml
# .github/workflows/test.yml example
- name: Run unit tests
  run: pytest tests/ -v -m "not slow"

# Only run integration tests manually or on release
- name: Run integration tests
  if: github.event_name == 'release'
  run: pytest tests/integration/ --run-slow -v
  env:
    REPLICATE_API_TOKEN: ${{ secrets.REPLICATE_API_TOKEN }}
    GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
```

## Troubleshooting

### Tests fail with "Configuration error"
- Check that `.env` exists in project root
- Verify all required env vars are set
- Run: `python -c "from hero_image_generator.ai import AIConfig; print(AIConfig.load())"`

### Integration tests skipped
- Add `--run-slow` flag
- Check that API credentials are valid

### Import errors
- Ensure package is installed: `pip install -e .`
- Or install with dev dependencies: `pip install -e ".[dev]"`

### Mocking errors in unit tests
- Unit tests should NEVER make real API calls
- Check that mocks are set up correctly
- Look for `@patch` decorators

## Writing New Tests

### Unit Test Template

```python
from unittest.mock import Mock, patch
import pytest

@patch('module.external_api')
def test_feature(mock_api):
    # Setup mock
    mock_api.return_value = 'expected'

    # Run code
    result = function_under_test()

    # Assert
    assert result == 'expected'
    mock_api.assert_called_once()
```

### Integration Test Template

```python
import pytest

@pytest.mark.slow
@pytest.mark.requires_api_keys
@pytest.mark.integration
def test_real_api_call(real_config, tmp_path):
    # Real API call here
    result = make_real_call()

    # Verify
    assert result.exists()
```

## Next Steps

- See [Replicate Setup](replicate_setup.md) for API configuration
- See [GCP Setup](gcp_setup.md) for Vertex AI configuration
