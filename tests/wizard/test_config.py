import os
import sys
from pathlib import Path
import tempfile
import json
from hero_image_generator.wizard.config import ConfigManager


def test_get_config_path_returns_path_object():
    """Config path should be a Path object"""
    manager = ConfigManager()
    path = manager.get_config_path()
    assert isinstance(path, Path)


def test_get_config_path_contains_hero_image_generator():
    """Config path should contain app name"""
    manager = ConfigManager()
    path = manager.get_config_path()
    assert 'hero-image-generator' in str(path)


def test_get_config_path_ends_with_last_used_json():
    """Config file should be named last-used.json"""
    manager = ConfigManager()
    path = manager.get_config_path()
    assert path.name == 'last-used.json'


def test_get_config_path_windows(monkeypatch):
    """Windows should use APPDATA environment variable"""
    manager = ConfigManager()

    # Mock Windows platform and APPDATA
    monkeypatch.setattr(sys, 'platform', 'win32')
    monkeypatch.setenv('APPDATA', r'C:\Users\TestUser\AppData\Roaming')

    path = manager.get_config_path()

    assert 'AppData' in str(path) or 'APPDATA' in str(path).upper()
    assert path.name == 'last-used.json'
    assert 'hero-image-generator' in str(path)


def test_get_config_path_windows_fallback(monkeypatch):
    """Windows without APPDATA should fallback to home directory"""
    manager = ConfigManager()

    # Mock Windows platform without APPDATA
    monkeypatch.setattr(sys, 'platform', 'win32')
    monkeypatch.delenv('APPDATA', raising=False)

    path = manager.get_config_path()

    # Should still return a valid Path object
    assert isinstance(path, Path)
    assert path.name == 'last-used.json'
    assert 'hero-image-generator' in str(path)


def test_load_returns_defaults_when_file_missing(tmp_path, monkeypatch):
    """Should return defaults if config file doesn't exist"""
    manager = ConfigManager()
    fake_path = tmp_path / "missing" / "last-used.json"
    monkeypatch.setattr(manager, 'get_config_path', lambda: fake_path)

    config = manager.load()

    assert config['accent_color'] == [139, 92, 246]
    assert config['last_year'] == 2025
    assert 'gradient_start' in config


def test_load_returns_defaults_when_file_corrupted(tmp_path, monkeypatch):
    """Should return defaults if JSON is invalid"""
    manager = ConfigManager()
    fake_path = tmp_path / "last-used.json"
    monkeypatch.setattr(manager, 'get_config_path', lambda: fake_path)

    # Write invalid JSON
    fake_path.write_text("{invalid json")

    config = manager.load()

    assert config['accent_color'] == [139, 92, 246]


def test_save_and_load_roundtrip(tmp_path, monkeypatch):
    """Should save and load config correctly"""
    manager = ConfigManager()
    fake_path = tmp_path / "last-used.json"
    monkeypatch.setattr(manager, 'get_config_path', lambda: fake_path)

    # Save custom config
    custom_config = {
        'accent_color': [255, 0, 0],
        'last_year': 2024,
        'gradient_start': [100, 100, 100],
        'gradient_end': [200, 200, 200],
        'title_font_size': 70,
        'subtitle_font_size': 40,
        'year_font_size': 38,
        'theme_override': 'ai_ml',
    }
    manager.save(custom_config)

    # Load it back
    loaded = manager.load()

    assert loaded['accent_color'] == [255, 0, 0]
    assert loaded['last_year'] == 2024
    assert loaded['theme_override'] == 'ai_ml'
