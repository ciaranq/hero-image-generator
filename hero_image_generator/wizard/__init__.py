"""Interactive CLI wizard for hero image generation."""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional

from ..image_generator import HeroImageGenerator
from ..theme_detector import ThemeDetector
from .config import ConfigManager
from .prompt import InputPrompter
from .preview import PreviewManager


class WizardRunner:
    """Main wizard orchestration class."""

    def __init__(self):
        """Initialize wizard components."""
        self.config_manager = ConfigManager()
        self.prompter = InputPrompter()
        self.preview_manager = PreviewManager()
        self.generator = HeroImageGenerator()
        self.theme_detector = ThemeDetector()

        # Current state
        self.config: Dict[str, Any] = {}
        self.title: str = ""
        self.tags: list = []
        self.year: int = 2025
        self.theme_override: Optional[str] = None
        self.output_path: str = ""

    def run(self) -> None:
        """Run the interactive wizard."""
        try:
            print("\n🎨 Hero Image Generator - Interactive Wizard\n")

            # Load saved preferences
            self.config = self.config_manager.load()
            if self.config != self.config_manager.get_default_config():
                print("✓ Using saved preferences from last session\n")

            # Initial input collection
            self._collect_initial_inputs()

            # Generate and preview
            self._generate_and_preview()

            # Refinement loop
            while not self.preview_manager.ask_satisfied():
                choice = self.preview_manager.show_refinement_menu()

                if choice == '0':
                    print("\n👋 Keeping current image")
                    break
                elif choice == '8':
                    self._collect_initial_inputs()
                    self._generate_and_preview()
                else:
                    self._handle_refinement(choice)
                    self._generate_and_preview()

            # Save final image
            self._save_final_image()

            # Save configuration
            self._save_config()

            print("\n✅ Done!\n")

        except KeyboardInterrupt:
            print("\n\n👋 Wizard cancelled\n")
            return

    def _collect_initial_inputs(self) -> None:
        """Collect initial user inputs."""
        # Title
        self.title = self.prompter.prompt_title()

        # Tags
        self.tags = self.prompter.prompt_tags()

        # Show detected theme
        theme = self.theme_detector.get_theme(self.tags)
        print(f"✓ Detected theme: {theme.name.replace('_', '/').upper()}")

        # Year
        self.year = self.prompter.prompt_year(self.config.get('last_year', 2025))

        # Ask about customization
        customize = input("\nCustomize colors/fonts? (y/n) [n]: ").strip().lower()

        if customize in ['y', 'yes']:
            self._collect_customizations()

    def _collect_customizations(self) -> None:
        """Collect color and font customizations."""
        # Accent color
        self.config['accent_color'] = self.prompter.prompt_color(
            "Accent color",
            tuple(self.config['accent_color'])
        )

        # Gradient colors
        customize_gradient = input("\nCustomize gradient? (y/n) [n]: ").strip().lower()
        if customize_gradient in ['y', 'yes']:
            self.config['gradient_start'] = self.prompter.prompt_color(
                "Gradient start",
                tuple(self.config['gradient_start'])
            )
            self.config['gradient_end'] = self.prompter.prompt_color(
                "Gradient end",
                tuple(self.config['gradient_end'])
            )

        # Font sizes
        customize_fonts = input("\nCustomize font sizes? (y/n) [n]: ").strip().lower()
        if customize_fonts in ['y', 'yes']:
            self._collect_font_sizes()

    def _collect_font_sizes(self) -> None:
        """Collect font size customizations."""
        print("\nCurrent font sizes:")
        print(f"  Title: {self.config['title_font_size']}px")
        print(f"  Subtitle: {self.config['subtitle_font_size']}px")
        print(f"  Year badge: {self.config['year_font_size']}px")

        change = input("\nChange font sizes? (y/n) [n]: ").strip().lower()
        if change not in ['y', 'yes']:
            return

        # Title font
        title_size = input(f"Title font size [{self.config['title_font_size']}]: ").strip()
        if title_size:
            self.config['title_font_size'] = int(title_size)

        # Subtitle font
        subtitle_size = input(f"Subtitle font size [{self.config['subtitle_font_size']}]: ").strip()
        if subtitle_size:
            self.config['subtitle_font_size'] = int(subtitle_size)

        # Year font
        year_size = input(f"Year badge font size [{self.config['year_font_size']}]: ").strip()
        if year_size:
            self.config['year_font_size'] = int(year_size)

    def _generate_and_preview(self) -> None:
        """Generate image and show preview."""
        # Generate temporary preview
        temp_filename = "temp-preview.png"

        print(f"\n⏳ Generating image...")
        self.output_path = self.generator.generate(
            self.title,
            self.tags,
            self.year,
            temp_filename
        )

        print(f"✅ Generated: {self.output_path}")
        print("🖼️  Opening preview...")

        self.preview_manager.open_preview(self.output_path)

    def _handle_refinement(self, choice: str) -> None:
        """Handle refinement menu choice."""
        if choice == '1':
            self.title = self.prompter.prompt_title()
        elif choice == '2':
            self.tags = self.prompter.prompt_tags()
            theme = self.theme_detector.get_theme(self.tags)
            print(f"✓ Detected theme: {theme.name.replace('_', '/').upper()}")
        elif choice == '3':
            self.year = self.prompter.prompt_year(self.year)
        elif choice == '4':
            print("\n[1] ai_ml  [2] seo_analytics  [3] automation  [4] strategy  [5] default")
            # TODO: Implement theme override
        elif choice == '5':
            self.config['accent_color'] = self.prompter.prompt_color(
                "Accent color",
                tuple(self.config['accent_color'])
            )
        elif choice == '6':
            self.config['gradient_start'] = self.prompter.prompt_color(
                "Gradient start",
                tuple(self.config['gradient_start'])
            )
            self.config['gradient_end'] = self.prompter.prompt_color(
                "Gradient end",
                tuple(self.config['gradient_end'])
            )
        elif choice == '7':
            self._collect_font_sizes()

    def _slugify(self, text: str) -> str:
        """Convert text to filename-safe slug."""
        # Convert to lowercase
        text = text.lower()
        # Replace spaces and special chars with hyphens
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        # Remove leading/trailing hyphens
        return text.strip('-')

    def _save_final_image(self) -> None:
        """Save the final image with user-specified name."""
        # Generate default filename from title
        default_filename = f"{self._slugify(self.title)}-hero.png"

        # Prompt for custom filename
        filename = self.preview_manager.prompt_output_filename(default_filename)

        # Ensure .png extension
        if not filename.endswith('.png'):
            filename += '.png'

        # Prompt for output directory
        output_dir = self.preview_manager.prompt_output_directory('public/images')

        # Generate final image
        self.generator.output_dir = output_dir
        final_path = self.generator.generate(
            self.title,
            self.tags,
            self.year,
            filename
        )

        print(f"\n✅ Saved: {final_path}")

    def _save_config(self) -> None:
        """Save configuration for next session."""
        # Update year
        self.config['last_year'] = self.year

        # Save
        self.config_manager.save(self.config)
        print("💾 Preferences saved for next session")


__all__ = ['WizardRunner']
