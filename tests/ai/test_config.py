"""Tests for AI configuration management."""
import os
import pytest
from hero_image_generator.ai.config import AIConfig, ConfigurationError


def test_load_config_with_all_env_vars(monkeypatch):
    """Test loading config when all env vars are present."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')
    monkeypatch.setenv('GCP_LOCATION', 'us-central1')
    monkeypatch.setenv('DEFAULT_MODEL', 'flux-pro')
    monkeypatch.setenv('FALLBACK_MODEL', 'imagen')

    config = AIConfig.load()

    assert config.replicate_api_token == 'test_token'
    assert config.gcp_project_id == 'test_project'
    assert config.gcp_location == 'us-central1'
    assert config.default_model == 'flux-pro'
    assert config.fallback_model == 'imagen'


def test_load_config_missing_replicate_token(monkeypatch):
    """Test config fails when Replicate token is missing."""
    monkeypatch.delenv('REPLICATE_API_TOKEN', raising=False)

    with pytest.raises(ConfigurationError, match='REPLICATE_API_TOKEN'):
        AIConfig.load()


def test_config_default_values(monkeypatch):
    """Test config uses sensible defaults."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')

    config = AIConfig.load()

    assert config.gcp_location == 'us-central1'
    assert config.default_model == 'flux-pro'
    assert config.fallback_model == 'imagen'
    assert config.enable_quality_check is True
    assert config.min_quality_score == 0.6


def test_config_size_parsing():
    """Test image size parsing from strings."""
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test')
    monkeypatch.setenv('SIZE_SMALL', '800x450')
    monkeypatch.setenv('SIZE_MEDIUM', '1920x1080')
    monkeypatch.setenv('SIZE_LARGE', '2560x1440')

    config = AIConfig.load()

    assert config.size_small == (800, 450)
    assert config.size_medium == (1920, 1080)
    assert config.size_large == (2560, 1440)
