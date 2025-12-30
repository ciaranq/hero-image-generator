"""Flux model implementation using Replicate API."""
import os
import replicate
import requests
from pathlib import Path
from typing import Tuple

from .base import BaseAIModel, GenerationError
from .config import AIConfig


class FluxModel(BaseAIModel):
    """Flux image generation model via Replicate API.

    Supports three variants:
    - pro: Highest quality, $0.055 per image
    - dev: Good quality, $0.020 per image
    - schnell: Fast generation, $0.010 per image
    """

    # Cost per image in USD
    COSTS = {
        'pro': 0.055,
        'dev': 0.020,
        'schnell': 0.010
    }

    # Replicate model IDs
    MODEL_IDS = {
        'pro': 'black-forest-labs/flux-1.1-pro',
        'dev': 'black-forest-labs/flux-dev',
        'schnell': 'black-forest-labs/flux-schnell'
    }

    def __init__(self, config: AIConfig, variant: str = 'pro'):
        """Initialize Flux model with specific variant.

        Args:
            config: AIConfig instance with API credentials
            variant: Model variant ('pro', 'dev', or 'schnell')

        Raises:
            ValueError: If variant is not valid
        """
        super().__init__(config)

        if variant not in self.COSTS:
            raise ValueError(
                f"Invalid variant '{variant}'. Must be one of: {list(self.COSTS.keys())}"
            )

        self.variant = variant
        self.model_id = self.MODEL_IDS[variant]

        # Set Replicate API token
        os.environ['REPLICATE_API_TOKEN'] = config.replicate_api_token

    @property
    def name(self) -> str:
        """Human-readable model name."""
        return f'Flux {self.variant.capitalize()}'

    def get_cost_per_image(self) -> float:
        """Return cost in USD per image generation.

        Returns:
            Cost as float (e.g., 0.055 for $0.055)
        """
        return self.COSTS[self.variant]

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
        try:
            width, height = size

            # Call Replicate API
            output = replicate.run(
                self.model_id,
                input={
                    'prompt': prompt,
                    'width': width,
                    'height': height,
                    'output_format': 'png'
                }
            )

            # Download generated image
            image_url = output
            response = requests.get(image_url)

            # Save to output path
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.content)

            return output_path

        except Exception as e:
            raise GenerationError(f'Failed to generate image: {str(e)}') from e
