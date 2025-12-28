"""Preview manager for image preview and refinement workflow."""

import sys
import os
import subprocess
from pathlib import Path
from typing import Optional


class PreviewManager:
    """Handles image preview and refinement workflow."""

    def open_preview(self, image_path: str) -> None:
        """
        Open image in system default viewer.

        Args:
            image_path: Path to the image file

        Platform-specific implementations:
        - macOS: Uses 'open' command
        - Linux: Uses 'xdg-open' command
        - Windows: Uses os.startfile()
        """
        try:
            if sys.platform == 'darwin':
                # macOS
                subprocess.run(['open', image_path], check=True)
            elif sys.platform == 'win32':
                # Windows
                os.startfile(image_path)
            else:
                # Linux and other Unix-like systems
                subprocess.run(['xdg-open', image_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f'Error opening image: {e}')
            print('Please open the image manually to preview.')
        except Exception as e:
            print(f'Error opening image: {e}')
            print('Please open the image manually to preview.')

    def ask_satisfied(self) -> bool:
        """
        Ask if user is satisfied with the image.

        Returns:
            True if satisfied (y), False if not (n)
        """
        while True:
            response = input('Are you satisfied with this image? (y/n): ').strip().lower()

            if response == 'y':
                return True
            elif response == 'n':
                return False
            else:
                print('Error: Please enter y or n.')

    def show_refinement_menu(self) -> str:
        """
        Show refinement menu options.

        Returns:
            User's choice as string (0-8)
        """
        print('\nRefinement Options:')
        print('  0. Save and exit')
        print('  1. Change title')
        print('  2. Change tags')
        print('  3. Change year')
        print('  4. Change accent color')
        print('  5. Change gradient colors')
        print('  6. Adjust font sizes')
        print('  7. Override theme')
        print('  8. Start over')

        while True:
            choice = input('Enter choice (0-8): ').strip()

            # Validate choice is a number between 0 and 8
            try:
                choice_num = int(choice)
                if 0 <= choice_num <= 8:
                    return choice
                else:
                    print('Error: Choice must be between 0 and 8.')
            except ValueError:
                print('Error: Please enter a number between 0 and 8.')

    def prompt_output_filename(self, default: Optional[str] = None) -> str:
        """
        Prompt for output filename.

        Args:
            default: Default filename if user presses enter

        Returns:
            Filename (guaranteed to have .png extension)
        """
        prompt_text = 'Enter output filename'
        if default:
            prompt_text += f' (default: {default})'
        prompt_text += ': '

        while True:
            filename = input(prompt_text).strip()

            # Use default if empty and default provided
            if not filename and default:
                return default

            # Require non-empty input if no default
            if not filename:
                print('Error: Filename cannot be empty.')
                continue

            # Add .png extension if missing
            if not filename.endswith('.png'):
                filename += '.png'

            return filename

    def prompt_output_directory(self, default: Optional[str] = None) -> str:
        """
        Prompt for output directory.

        Args:
            default: Default directory if user presses enter

        Returns:
            Directory path (validated to exist)
        """
        prompt_text = 'Enter output directory'
        if default:
            prompt_text += f' (default: {default})'
        prompt_text += ': '

        while True:
            directory = input(prompt_text).strip()

            # Use default if empty and default provided
            if not directory and default:
                return default

            # Require non-empty input if no default
            if not directory:
                print('Error: Directory cannot be empty.')
                continue

            # Validate directory exists
            if not Path(directory).is_dir():
                print(f'Error: Directory does not exist: {directory}')
                continue

            return directory
