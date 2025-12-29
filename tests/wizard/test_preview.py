"""Tests for preview manager."""

import sys
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from hero_image_generator.wizard.preview import PreviewManager


def test_open_preview_macos(monkeypatch):
    """macOS should use 'open' command"""
    manager = PreviewManager()

    # Mock macOS platform
    monkeypatch.setattr(sys, 'platform', 'darwin')

    # Mock subprocess.run
    mock_run = MagicMock()
    monkeypatch.setattr(subprocess, 'run', mock_run)

    manager.open_preview('/path/to/image.png')

    # Verify 'open' was called with correct arguments
    mock_run.assert_called_once_with(['open', '/path/to/image.png'], check=True)


def test_open_preview_linux(monkeypatch):
    """Linux should use 'xdg-open' command"""
    manager = PreviewManager()

    # Mock Linux platform
    monkeypatch.setattr(sys, 'platform', 'linux')

    # Mock subprocess.run
    mock_run = MagicMock()
    monkeypatch.setattr(subprocess, 'run', mock_run)

    manager.open_preview('/path/to/image.png')

    # Verify 'xdg-open' was called with correct arguments
    mock_run.assert_called_once_with(['xdg-open', '/path/to/image.png'], check=True)


def test_open_preview_windows(monkeypatch):
    """Windows should use os.startfile()"""
    manager = PreviewManager()

    # Mock Windows platform
    monkeypatch.setattr(sys, 'platform', 'win32')

    # Mock os.startfile
    import os
    mock_startfile = MagicMock()
    monkeypatch.setattr(os, 'startfile', mock_startfile, raising=False)

    manager.open_preview(r'C:\path\to\image.png')

    # Verify os.startfile was called with correct path
    mock_startfile.assert_called_once_with(r'C:\path\to\image.png')


def test_open_preview_handles_subprocess_error(monkeypatch, capsys):
    """Should handle subprocess errors gracefully"""
    manager = PreviewManager()

    # Mock macOS platform
    monkeypatch.setattr(sys, 'platform', 'darwin')

    # Mock subprocess.run to raise an error
    def mock_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, 'open')

    monkeypatch.setattr(subprocess, 'run', mock_run)

    # Should not raise exception
    manager.open_preview('/path/to/image.png')

    # Should print error message
    captured = capsys.readouterr()
    assert 'Error opening image' in captured.out


def test_open_preview_handles_general_error(monkeypatch, capsys):
    """Should handle general errors gracefully"""
    manager = PreviewManager()

    # Mock macOS platform
    monkeypatch.setattr(sys, 'platform', 'darwin')

    # Mock subprocess.run to raise a general exception
    def mock_run(*args, **kwargs):
        raise Exception('Something went wrong')

    monkeypatch.setattr(subprocess, 'run', mock_run)

    # Should not raise exception
    manager.open_preview('/path/to/image.png')

    # Should print error message
    captured = capsys.readouterr()
    assert 'Error opening image' in captured.out


def test_ask_satisfied_yes(monkeypatch):
    """Should return True for 'y' input"""
    manager = PreviewManager()

    # Mock user input
    monkeypatch.setattr('builtins.input', lambda _: 'y')

    result = manager.ask_satisfied()
    assert result is True


def test_ask_satisfied_no(monkeypatch):
    """Should return False for 'n' input"""
    manager = PreviewManager()

    # Mock user input
    monkeypatch.setattr('builtins.input', lambda _: 'n')

    result = manager.ask_satisfied()
    assert result is False


def test_ask_satisfied_loops_on_invalid_input(monkeypatch):
    """Should loop until valid input is provided"""
    manager = PreviewManager()

    # Mock sequence of inputs: invalid, invalid, then valid
    inputs = iter(['maybe', '', 'Y'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    result = manager.ask_satisfied()
    assert result is True


def test_ask_satisfied_case_insensitive(monkeypatch):
    """Should accept uppercase Y/N"""
    manager = PreviewManager()

    # Test uppercase Y
    monkeypatch.setattr('builtins.input', lambda _: 'Y')
    assert manager.ask_satisfied() is True

    # Test uppercase N
    monkeypatch.setattr('builtins.input', lambda _: 'N')
    assert manager.ask_satisfied() is False


def test_show_refinement_menu_valid_choice(monkeypatch, capsys):
    """Should return valid menu choice"""
    manager = PreviewManager()

    # Mock user input
    monkeypatch.setattr('builtins.input', lambda _: '3')

    result = manager.show_refinement_menu()

    assert result == '3'

    # Verify menu was displayed
    captured = capsys.readouterr()
    assert 'Refinement Options' in captured.out
    assert '0. Save and exit' in captured.out
    assert '8. Start over' in captured.out


def test_show_refinement_menu_loops_on_invalid(monkeypatch):
    """Should loop until valid choice (0-8)"""
    manager = PreviewManager()

    # Mock sequence of inputs: invalid, then valid
    inputs = iter(['9', '-1', 'abc', '5'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    result = manager.show_refinement_menu()
    assert result == '5'


def test_prompt_output_filename_with_default(monkeypatch):
    """Should return default if user presses enter"""
    manager = PreviewManager()

    # Test returning default
    monkeypatch.setattr('builtins.input', lambda _: '')
    result = manager.prompt_output_filename('default.png')
    assert result == 'default.png'


def test_prompt_output_filename_custom_value(monkeypatch):
    """Should return custom value when provided"""
    manager = PreviewManager()

    # Test returning custom value
    monkeypatch.setattr('builtins.input', lambda _: 'custom.png')
    result = manager.prompt_output_filename('default.png')
    assert result == 'custom.png'


def test_prompt_output_filename_adds_png_extension(monkeypatch):
    """Should add .png extension if missing"""
    manager = PreviewManager()

    # Input without extension
    monkeypatch.setattr('builtins.input', lambda _: 'myfile')
    result = manager.prompt_output_filename('default.png')
    assert result == 'myfile.png'

    # Input with extension should not add another
    monkeypatch.setattr('builtins.input', lambda _: 'myfile.png')
    result = manager.prompt_output_filename('default.png')
    assert result == 'myfile.png'


def test_prompt_output_filename_loops_on_invalid(monkeypatch):
    """Should loop until non-empty filename when no default"""
    manager = PreviewManager()

    # Mock sequence: empty, whitespace, then valid
    inputs = iter(['', '   ', 'valid.png'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    result = manager.prompt_output_filename()
    assert result == 'valid.png'


def test_prompt_output_directory_with_default(monkeypatch):
    """Should return default if user presses enter"""
    manager = PreviewManager()

    # Test returning default
    monkeypatch.setattr('builtins.input', lambda _: '')
    result = manager.prompt_output_directory('/default/path')
    assert result == '/default/path'


def test_prompt_output_directory_custom_value(monkeypatch, tmp_path):
    """Should return custom value when provided"""
    manager = PreviewManager()

    # Create a real directory
    custom_dir = tmp_path / 'custom'
    custom_dir.mkdir()

    # Test returning custom value
    monkeypatch.setattr('builtins.input', lambda _: str(custom_dir))
    result = manager.prompt_output_directory('/default/path')
    assert result == str(custom_dir)


def test_prompt_output_directory_validates_existence(monkeypatch, tmp_path):
    """Should validate that directory exists"""
    manager = PreviewManager()

    # Create a real directory
    valid_dir = tmp_path / 'valid'
    valid_dir.mkdir()

    # Mock sequence: non-existent dir, then valid dir
    inputs = iter(['/nonexistent/path', str(valid_dir)])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    result = manager.prompt_output_directory()
    assert result == str(valid_dir)


def test_prompt_output_directory_loops_on_invalid(monkeypatch, tmp_path):
    """Should loop until valid directory when no default"""
    manager = PreviewManager()

    valid_dir = tmp_path / 'valid'
    valid_dir.mkdir()

    # Mock sequence: empty, whitespace, non-existent, then valid
    inputs = iter(['', '   ', '/fake/dir', str(valid_dir)])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    result = manager.prompt_output_directory()
    assert result == str(valid_dir)
