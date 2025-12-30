"""Gemini/Imagen model implementation using Google Vertex AI."""
from pathlib import Path
from typing import Tuple
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

from .base import BaseAIModel, GenerationError
from .config import AIConfig


class GeminiModel(BaseAIModel):
    """Gemini/Imagen image generation model via Google Vertex AI.

    Supports two variants:
    - Imagen: Image generation model, $0.020 per image
    - Gemini 2.0 Flash: Multimodal model with image generation, $0.020 per image
    """

    # Cost per image in USD
    COST_PER_IMAGE = 0.020

    def __init__(self, config: AIConfig, use_imagen: bool = True):
        """Initialize Gemini model with specific variant.

        Args:
            config: AIConfig instance with API credentials
            use_imagen: If True, use Imagen; if False, use Gemini 2.0 Flash

        Raises:
            GenerationError: If Vertex AI initialization fails
        """
        super().__init__(config)
        self.use_imagen = use_imagen

        # Initialize Vertex AI
        try:
            aiplatform.init(
                project=config.gcp_project_id,
                location=config.gcp_location
            )
        except Exception as e:
            raise GenerationError(f'Failed to initialize Vertex AI: {str(e)}') from e

    @property
    def name(self) -> str:
        """Human-readable model name."""
        return 'Imagen' if self.use_imagen else 'Gemini 2.0 Flash'

    def get_cost_per_image(self) -> float:
        """Return cost in USD per image generation.

        Returns:
            Cost as float (0.020 for both variants)
        """
        return self.COST_PER_IMAGE

    def _calculate_aspect_ratio(self, width: int, height: int) -> str:
        """Calculate closest supported aspect ratio.

        Vertex AI Imagen supports: 1:1, 3:4, 4:3, 9:16, 16:9

        Args:
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            Aspect ratio string (e.g., '16:9')
        """
        # Calculate actual ratio
        ratio = width / height

        # Map to closest supported ratio
        ratios = {
            '1:1': 1.0,
            '3:4': 0.75,
            '4:3': 1.333,
            '9:16': 0.5625,
            '16:9': 1.778
        }

        # Find closest ratio
        closest = min(ratios.items(), key=lambda x: abs(x[1] - ratio))
        return closest[0]

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

            # Load the model
            model = ImageGenerationModel.from_pretrained('imagegeneration@006')

            # Calculate aspect ratio
            aspect_ratio = self._calculate_aspect_ratio(width, height)

            # Generate image
            response = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio=aspect_ratio
            )

            # Get the first image
            image = response.images[0]

            # Save to output path
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(image._image_bytes)

            return output_path

        except Exception as e:
            raise GenerationError(f'Failed to generate image: {str(e)}') from e
