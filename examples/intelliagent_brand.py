#!/usr/bin/env python3
"""
IntelliAgent Brand Configuration

Example of how to customize the hero image generator for your brand.
This file demonstrates IntelliAgent's brand colors and settings.
"""

import sys
from pathlib import Path

# Add parent directory to path to import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from hero_image_generator import HeroImageGenerator, ThemeDetector, Theme


class IntelliAgentGenerator(HeroImageGenerator):
    """Hero image generator with IntelliAgent branding"""

    def __init__(self):
        super().__init__()

        # IntelliAgent brand colors
        self.bg_color_start = (30, 58, 138)   # Deep blue
        self.bg_color_end = (59, 130, 246)    # Bright blue
        self.text_color = (255, 255, 255)     # White
        self.badge_color = (34, 197, 94)      # Green accent

        # Custom output directory
        self.output_dir = 'output/images'


class IntelliAgentThemeDetector(ThemeDetector):
    """Theme detector with IntelliAgent-specific themes"""

    def __init__(self):
        super().__init__()

        # Add custom themes specific to IntelliAgent's content
        self.theme_map['customer-service'] = {
            'tags': ['customer-service', 'support', 'cx'],
            'accent': (59, 130, 246)  # Bright blue
        }

        self.theme_map['consulting'] = {
            'tags': ['consulting', 'advisory', 'transformation'],
            'accent': (6, 182, 212)  # Cyan
        }


def generate_intelliagent_sample():
    """Generate a sample image with IntelliAgent branding"""

    # Create generator with IntelliAgent branding
    generator = IntelliAgentGenerator()

    # Override theme detector
    generator.theme_detector = IntelliAgentThemeDetector()

    # Generate sample image
    output_path = generator.generate(
        title="AI Agent Orchestration Platform",
        tags=["ai", "agent", "platform"],
        year=2025,
        output_filename="intelliagent-sample.png"
    )

    print(f"✅ Generated IntelliAgent branded image: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_intelliagent_sample()
