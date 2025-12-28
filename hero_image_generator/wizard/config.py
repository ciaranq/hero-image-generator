"""Configuration persistence for wizard preferences."""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages wizard configuration persistence."""

    def get_config_path(self) -> Path:
        """
        Get platform-specific config file path.

        Returns:
            Path to last-used.json config file
        """
        if sys.platform == 'win32':
            # Windows: %APPDATA%/hero-image-generator/last-used.json
            base = Path(os.environ.get('APPDATA', str(Path.home())))
        else:
            # Linux/macOS: ~/.config/hero-image-generator/last-used.json
            base = Path.home() / '.config'

        config_dir = base / 'hero-image-generator'
        return config_dir / 'last-used.json'

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values.

        Returns:
            Dictionary with default settings
        """
        return {
            'accent_color': [139, 92, 246],  # Purple
            'gradient_start': [59, 130, 246],  # Blue
            'gradient_end': [139, 92, 246],  # Purple
            'title_font_size': 60,
            'subtitle_font_size': 32,
            'year_font_size': 36,
            'theme_override': None,
            'last_year': 2025,
        }

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file or return defaults.

        Returns:
            Configuration dictionary
        """
        config_path = self.get_config_path()

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                defaults = self.get_default_config()
                return {**defaults, **config}
        except (FileNotFoundError, json.JSONDecodeError):
            return self.get_default_config()

    def save(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration dictionary to save
        """
        config_path = self.get_config_path()

        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
