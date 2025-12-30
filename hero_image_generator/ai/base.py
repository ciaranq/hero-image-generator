"""Base abstraction for AI image generation models."""
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from pathlib import Path


class GenerationError(Exception):
    """Raised when image generation fails."""
    pass


class BaseAIModel(ABC):
    """Abstract base class for AI image generation models."""

    def __init__(self, config: 'AIConfig'):
        """Initialize model with configuration.

        Args:
            config: AIConfig instance with API credentials
        """
        self.config = config

    @abstractmethod
    def generate(
        self,
        prompt: str,
        size: Tuple[int, int],
        output_path: Path
    ) -> Path:
        """Generate image from prompt and save to output_path.

        Args:
            prompt: Text description of desired image
            size: (width, height) tuple
            output_path: Path to save generated image

        Returns:
            Path to saved image file

        Raises:
            GenerationError: If generation fails
        """
        pass

    @abstractmethod
    def get_cost_per_image(self) -> float:
        """Return cost in USD per image generation.

        Returns:
            Cost as float (e.g., 0.055 for $0.055)
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable model name."""
        pass
