# Integration Tests

These tests make real API calls to Replicate and Google Vertex AI.

## Prerequisites

1. Set up `.env` file with real credentials:
   - `REPLICATE_API_TOKEN`
   - `GCP_PROJECT_ID`
   - `GOOGLE_APPLICATION_CREDENTIALS`

2. Ensure you have API credits available

## Running Tests

```bash
# Run all integration tests (will incur API costs)
pytest tests/integration/ --run-slow -v

# Run only Flux tests
pytest tests/integration/test_flux_integration.py --run-slow -v

# Run only Gemini tests
pytest tests/integration/test_gemini_integration.py --run-slow -v
```

## Costs

Approximate costs per test run:
- Flux Schnell test: $0.01
- Flux Pro test: $0.055 (skipped by default)
- Imagen test: $0.02
- Quality validation test: $0.021 (generation + validation)

Total (with Flux Pro skipped): ~$0.04 per full test run
