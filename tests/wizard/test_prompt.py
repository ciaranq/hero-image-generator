"""Tests for InputPrompter user input and validation."""

import unittest
from unittest.mock import patch
from hero_image_generator.wizard.prompt import (
    InputPrompter,
    validate_hex_color,
    validate_rgb_color,
    validate_year,
)


class TestColorValidation(unittest.TestCase):
    """Test color validation functions."""

    def test_validate_hex_color_with_hash(self):
        """Test hex color validation with # prefix."""
        result = validate_hex_color('#8b5cf6')
        self.assertEqual(result, (139, 92, 246))

    def test_validate_hex_color_without_hash(self):
        """Test hex color validation without # prefix."""
        result = validate_hex_color('8b5cf6')
        self.assertEqual(result, (139, 92, 246))

    def test_validate_hex_color_uppercase(self):
        """Test hex color validation with uppercase."""
        result = validate_hex_color('#8B5CF6')
        self.assertEqual(result, (139, 92, 246))

    def test_validate_hex_color_invalid_length(self):
        """Test hex color validation with invalid length."""
        result = validate_hex_color('#8b5c')
        self.assertIsNone(result)

    def test_validate_hex_color_invalid_chars(self):
        """Test hex color validation with invalid characters."""
        result = validate_hex_color('#gggggg')
        self.assertIsNone(result)

    def test_validate_hex_color_empty(self):
        """Test hex color validation with empty string."""
        result = validate_hex_color('')
        self.assertIsNone(result)

    def test_validate_rgb_color_with_spaces(self):
        """Test RGB color validation with spaces."""
        result = validate_rgb_color('139, 92, 246')
        self.assertEqual(result, (139, 92, 246))

    def test_validate_rgb_color_without_spaces(self):
        """Test RGB color validation without spaces."""
        result = validate_rgb_color('139,92,246')
        self.assertEqual(result, (139, 92, 246))

    def test_validate_rgb_color_out_of_range(self):
        """Test RGB color validation with values out of range."""
        result = validate_rgb_color('300, 92, 246')
        self.assertIsNone(result)
        result = validate_rgb_color('139, -5, 246')
        self.assertIsNone(result)

    def test_validate_rgb_color_invalid_format(self):
        """Test RGB color validation with invalid format."""
        result = validate_rgb_color('139,92')
        self.assertIsNone(result)
        result = validate_rgb_color('not a color')
        self.assertIsNone(result)

    def test_validate_rgb_color_empty(self):
        """Test RGB color validation with empty string."""
        result = validate_rgb_color('')
        self.assertIsNone(result)


class TestYearValidation(unittest.TestCase):
    """Test year validation function."""

    def test_validate_year_valid(self):
        """Test year validation with valid years."""
        self.assertEqual(validate_year('2025'), 2025)
        self.assertEqual(validate_year('1900'), 1900)
        self.assertEqual(validate_year('2099'), 2099)

    def test_validate_year_out_of_range_low(self):
        """Test year validation with year too low."""
        result = validate_year('1899')
        self.assertIsNone(result)

    def test_validate_year_out_of_range_high(self):
        """Test year validation with year too high."""
        result = validate_year('2100')
        self.assertIsNone(result)

    def test_validate_year_non_numeric(self):
        """Test year validation with non-numeric input."""
        result = validate_year('not a year')
        self.assertIsNone(result)

    def test_validate_year_empty(self):
        """Test year validation with empty string."""
        result = validate_year('')
        self.assertIsNone(result)


class TestInputPrompter(unittest.TestCase):
    """Test InputPrompter methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.prompter = InputPrompter()

    @patch('builtins.input', return_value='My Test Title')
    def test_prompt_title_valid(self, mock_input):
        """Test prompting for a valid title."""
        result = self.prompter.prompt_title()
        self.assertEqual(result, 'My Test Title')

    @patch('builtins.input', side_effect=['', '   ', 'Valid Title'])
    def test_prompt_title_empty_then_valid(self, mock_input):
        """Test prompting for title with empty inputs first."""
        result = self.prompter.prompt_title()
        self.assertEqual(result, 'Valid Title')
        self.assertEqual(mock_input.call_count, 3)

    @patch('builtins.input', return_value='x' * 150)
    @patch('builtins.print')
    def test_prompt_title_too_long(self, mock_print, mock_input):
        """Test prompting for title that's too long (>100 chars)."""
        with patch('builtins.input', side_effect=['x' * 150, 'Valid Title']):
            result = self.prompter.prompt_title()
            self.assertEqual(result, 'Valid Title')

    @patch('builtins.input', return_value='x' * 65)
    @patch('builtins.print')
    def test_prompt_title_warning(self, mock_print, mock_input):
        """Test prompting for title that triggers warning (>60 chars)."""
        result = self.prompter.prompt_title()
        self.assertEqual(result, 'x' * 65)
        # Verify warning was printed
        warning_printed = any(
            'Warning' in str(call) or 'recommended' in str(call).lower()
            for call in mock_print.call_args_list
        )
        self.assertTrue(warning_printed)

    @patch('builtins.input', return_value='ai, ml, automation')
    def test_prompt_tags_valid(self, mock_input):
        """Test prompting for valid tags."""
        result = self.prompter.prompt_tags()
        self.assertEqual(result, ['ai', 'ml', 'automation'])

    @patch('builtins.input', return_value='AI, ML, Automation')
    def test_prompt_tags_uppercase(self, mock_input):
        """Test prompting for tags with uppercase (should lowercase)."""
        result = self.prompter.prompt_tags()
        self.assertEqual(result, ['ai', 'ml', 'automation'])

    @patch('builtins.input', return_value=' ai ,  ml , automation ')
    def test_prompt_tags_extra_spaces(self, mock_input):
        """Test prompting for tags with extra spaces."""
        result = self.prompter.prompt_tags()
        self.assertEqual(result, ['ai', 'ml', 'automation'])

    @patch('builtins.input', side_effect=['', 'ai, ml'])
    def test_prompt_tags_empty_then_valid(self, mock_input):
        """Test prompting for tags with empty input first."""
        result = self.prompter.prompt_tags()
        self.assertEqual(result, ['ai', 'ml'])

    @patch('builtins.input', return_value='2025')
    def test_prompt_year_valid(self, mock_input):
        """Test prompting for a valid year."""
        result = self.prompter.prompt_year()
        self.assertEqual(result, 2025)

    @patch('builtins.input', return_value='')
    def test_prompt_year_default(self, mock_input):
        """Test prompting for year with default value."""
        result = self.prompter.prompt_year(default=2024)
        self.assertEqual(result, 2024)

    @patch('builtins.input', side_effect=['1899', '2100', 'invalid', '2025'])
    def test_prompt_year_invalid_then_valid(self, mock_input):
        """Test prompting for year with invalid inputs first."""
        result = self.prompter.prompt_year()
        self.assertEqual(result, 2025)
        self.assertEqual(mock_input.call_count, 4)

    @patch('builtins.input', return_value='1')
    def test_prompt_color_preset(self, mock_input):
        """Test prompting for a preset color."""
        result = self.prompter.prompt_color()
        # Should return the first preset (purple)
        self.assertEqual(result, (139, 92, 246))

    @patch('builtins.input', side_effect=['7', '#8b5cf6'])
    def test_prompt_color_custom_hex(self, mock_input):
        """Test prompting for a custom hex color."""
        result = self.prompter.prompt_color()
        self.assertEqual(result, (139, 92, 246))

    @patch('builtins.input', side_effect=['7', '139,92,246'])
    def test_prompt_color_custom_rgb(self, mock_input):
        """Test prompting for a custom RGB color."""
        result = self.prompter.prompt_color()
        self.assertEqual(result, (139, 92, 246))

    @patch('builtins.input', side_effect=['invalid', '1'])
    def test_prompt_color_invalid_then_valid(self, mock_input):
        """Test prompting for color with invalid input first."""
        result = self.prompter.prompt_color()
        self.assertEqual(result, (139, 92, 246))


if __name__ == '__main__':
    unittest.main()
