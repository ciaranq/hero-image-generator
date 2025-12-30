"""Tests for AI configuration management."""
import os
import pytest
from unittest.mock import patch
from hero_image_generator.ai.config import AIConfig, ConfigurationError


def clear_all_env_vars(monkeypatch):
    """Clear all AI-related environment variables for test isolation."""
    env_vars = [
        'REPLICATE_API_TOKEN', 'GCP_PROJECT_ID', 'GCP_LOCATION',
        'GOOGLE_APPLICATION_CREDENTIALS', 'DEFAULT_MODEL', 'FALLBACK_MODEL',
        'ENABLE_QUALITY_CHECK', 'MIN_QUALITY_SCORE', 'SIZE_SMALL',
        'SIZE_MEDIUM', 'SIZE_LARGE', 'OUTPUT_DIRECTORY', 'FAILED_OUTPUT_DIRECTORY',
        'SAVE_FAILED_GENERATIONS', 'LOG_COSTS', 'COST_LOG_FILE',
        'MAX_RETRIES', 'RETRY_DELAY_SECONDS'
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)


@patch('hero_image_generator.ai.config.load_dotenv')
def test_load_config_with_all_env_vars(mock_load_dotenv, monkeypatch):
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


@patch('hero_image_generator.ai.config.load_dotenv')
def test_load_config_missing_replicate_token(mock_load_dotenv, monkeypatch):
    """Test config fails when Replicate token is missing."""
    clear_all_env_vars(monkeypatch)

    with pytest.raises(ConfigurationError, match='REPLICATE_API_TOKEN'):
        AIConfig.load()


@patch('hero_image_generator.ai.config.load_dotenv')
def test_load_config_missing_gcp_project_id(mock_load_dotenv, monkeypatch):
    """Test config fails when GCP project ID is missing."""
    clear_all_env_vars(monkeypatch)
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token')

    with pytest.raises(ConfigurationError, match='GCP_PROJECT_ID'):
        AIConfig.load()


@patch('hero_image_generator.ai.config.load_dotenv')
def test_config_default_values(mock_load_dotenv, monkeypatch):
    """Test config uses sensible defaults."""
    clear_all_env_vars(monkeypatch)
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')

    config = AIConfig.load()

    assert config.gcp_location == 'us-central1'
    assert config.default_model == 'flux-pro'
    assert config.fallback_model == 'imagen'
    assert config.enable_quality_check is True
    assert config.min_quality_score == 0.6


@patch('hero_image_generator.ai.config.load_dotenv')
def test_config_size_parsing(mock_load_dotenv, monkeypatch):
    """Test image size parsing from strings."""
    clear_all_env_vars(monkeypatch)
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test')
    monkeypatch.setenv('SIZE_SMALL', '800x450')
    monkeypatch.setenv('SIZE_MEDIUM', '1920x1080')
    monkeypatch.setenv('SIZE_LARGE', '2560x1440')

    config = AIConfig.load()

    assert config.size_small == (800, 450)
    assert config.size_medium == (1920, 1080)
    assert config.size_large == (2560, 1440)


@patch('hero_image_generator.ai.config.load_dotenv')
def test_config_invalid_size_format(mock_load_dotenv, monkeypatch):
    """Test config fails with invalid size format."""
    clear_all_env_vars(monkeypatch)
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test')
    monkeypatch.setenv('SIZE_SMALL', 'invalid')

    with pytest.raises(ConfigurationError, match='Invalid size format'):
        AIConfig.load()


@patch('hero_image_generator.ai.config.load_dotenv')
def test_config_invalid_quality_score(mock_load_dotenv, monkeypatch):
    """Test config fails with invalid quality score."""
    clear_all_env_vars(monkeypatch)
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test')
    monkeypatch.setenv('MIN_QUALITY_SCORE', 'not_a_number')

    with pytest.raises(ConfigurationError, match='MIN_QUALITY_SCORE must be a number'):
        AIConfig.load()


@patch('hero_image_generator.ai.config.load_dotenv')
def test_config_invalid_max_retries(mock_load_dotenv, monkeypatch):
    """Test config fails with invalid max retries."""
    clear_all_env_vars(monkeypatch)
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test')
    monkeypatch.setenv('MAX_RETRIES', 'not_a_number')

    with pytest.raises(ConfigurationError, match='MAX_RETRIES must be an integer'):
        AIConfig.load()
