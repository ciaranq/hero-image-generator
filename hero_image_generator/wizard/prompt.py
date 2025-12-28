"""User input prompting and validation for wizard."""

from typing import Optional, Tuple, List


# Color presets for quick selection
COLOR_PRESETS = {
    1: ('Purple (AI/ML)', (139, 92, 246)),
    2: ('Green (SEO)', (34, 197, 94)),
    3: ('Orange (Automation)', (249, 115, 22)),
    4: ('Cyan (Strategy)', (6, 182, 212)),
    5: ('Red', (239, 68, 68)),
    6: ('Blue', (59, 130, 246)),
}


def validate_hex_color(hex_str: str) -> Optional[Tuple[int, int, int]]:
    """
    Validate and convert hex color string to RGB tuple.

    Args:
        hex_str: Hex color string (with or without # prefix)

    Returns:
        RGB tuple (r, g, b) if valid, None otherwise
    """
    if not hex_str:
        return None

    # Remove # prefix if present
    hex_str = hex_str.lstrip('#')

    # Check if valid hex (6 characters, valid hex digits)
    if len(hex_str) != 6:
        return None

    try:
        # Convert hex to RGB
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return (r, g, b)
    except ValueError:
        return None


def validate_rgb_color(rgb_str: str) -> Optional[Tuple[int, int, int]]:
    """
    Validate and convert RGB color string to RGB tuple.

    Args:
        rgb_str: RGB color string in format "R,G,B" or "R, G, B"

    Returns:
        RGB tuple (r, g, b) if valid, None otherwise
    """
    if not rgb_str:
        return None

    try:
        # Split by comma and strip whitespace
        parts = [p.strip() for p in rgb_str.split(',')]

        if len(parts) != 3:
            return None

        # Convert to integers
        r, g, b = int(parts[0]), int(parts[1]), int(parts[2])

        # Validate range (0-255)
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            return None

        return (r, g, b)
    except (ValueError, IndexError):
        return None


def validate_year(year_str: str) -> Optional[int]:
    """
    Validate year string.

    Args:
        year_str: Year as string

    Returns:
        Year as integer if valid (1900-2099), None otherwise
    """
    if not year_str:
        return None

    try:
        year = int(year_str)
        if 1900 <= year <= 2099:
            return year
        return None
    except ValueError:
        return None


class InputPrompter:
    """Handles user input prompting with validation."""

    def prompt_title(self) -> str:
        """
        Prompt user for title with validation.

        Returns:
            Valid title string
        """
        while True:
            title = input('Enter title: ').strip()

            if not title:
                print('Error: Title cannot be empty.')
                continue

            if len(title) > 100:
                print('Error: Title too long (max 100 characters).')
                continue

            if len(title) > 60:
                print('Warning: Title over 60 characters may not display optimally.')

            return title

    def prompt_tags(self) -> List[str]:
        """
        Prompt user for comma-separated tags.

        Returns:
            List of lowercase tag strings
        """
        while True:
            tags_input = input('Enter tags (comma-separated): ').strip()

            if not tags_input:
                print('Error: At least one tag is required.')
                continue

            # Split by comma, strip whitespace, convert to lowercase
            tags = [tag.strip().lower() for tag in tags_input.split(',')]
            tags = [tag for tag in tags if tag]  # Remove empty strings

            if not tags:
                print('Error: At least one tag is required.')
                continue

            return tags

    def prompt_year(self, default: Optional[int] = None) -> int:
        """
        Prompt user for year with optional default.

        Args:
            default: Default year if user presses enter

        Returns:
            Valid year integer
        """
        prompt_text = 'Enter year'
        if default:
            prompt_text += f' (default: {default})'
        prompt_text += ': '

        while True:
            year_input = input(prompt_text).strip()

            # Use default if empty and default provided
            if not year_input and default:
                return default

            year = validate_year(year_input)
            if year is not None:
                return year

            print('Error: Year must be between 1900 and 2099.')

    def prompt_color(self) -> Tuple[int, int, int]:
        """
        Prompt user for color with presets or custom input.

        Returns:
            RGB color tuple
        """
        print('\nChoose a color:')
        for num, (name, _) in COLOR_PRESETS.items():
            print(f'  {num}. {name}')
        print('  7. Custom color')

        while True:
            choice = input('Enter choice (1-7): ').strip()

            # Check if preset choice
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= 6:
                    _, rgb = COLOR_PRESETS[choice_num]
                    return rgb
                elif choice_num == 7:
                    return self._prompt_custom_color()
                else:
                    print('Error: Choice must be between 1 and 7.')
            except ValueError:
                print('Error: Invalid choice. Please enter a number 1-7.')

    def _prompt_custom_color(self) -> Tuple[int, int, int]:
        """
        Prompt user for custom color in hex or RGB format.

        Returns:
            RGB color tuple
        """
        print('\nEnter custom color:')
        print('  Format: #8b5cf6 (hex) or 139,92,246 (RGB)')

        while True:
            color_input = input('Color: ').strip()

            # Try hex first
            if '#' in color_input or len(color_input) == 6:
                rgb = validate_hex_color(color_input)
                if rgb:
                    return rgb

            # Try RGB format
            rgb = validate_rgb_color(color_input)
            if rgb:
                return rgb

            print('Error: Invalid color format. Use #RRGGBB or R,G,B format.')
