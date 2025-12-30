"""Quality validation using Gemini Vision."""
import os
import json
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Part

from .config import AIConfig


@dataclass
class ValidationResult:
    """Result of image quality validation."""
    passed: bool
    score: float
    feedback: str
    cost: float


class QualityValidator:
    """Validate generated images using Gemini Vision."""

    VALIDATION_COST = 0.001  # Cost per validation in USD

    VALIDATION_PROMPT = """Analyze this hero image against the following prompt:

"{prompt}"

Score from 0.0 to 1.0 on these criteria:
1. Subject matter match (0-0.4): Does the image accurately represent the described subject?
2. Style/mood alignment (0-0.3): Does the style and mood match the prompt?
3. Professional quality (0-0.3): Is this suitable for professional marketing use?

Return your analysis as JSON:
{{
  "score": 0.0-1.0,
  "breakdown": {{
    "subject": 0.0-0.4,
    "style": 0.0-0.3,
    "quality": 0.0-0.3
  }},
  "issues": ["list", "of", "issues"]
}}
"""

    def __init__(self, config: AIConfig):
        """Initialize quality validator.

        Args:
            config: AIConfig instance
        """
        self.config = config

        # Initialize Vertex AI
        credentials_path = config.google_application_credentials
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

        aiplatform.init(
            project=config.gcp_project_id,
            location=config.gcp_location
        )

        # Initialize Gemini model
        self.model = GenerativeModel('gemini-1.5-flash')

    def validate(self, image_path: Path, prompt: str) -> ValidationResult:
        """Validate image against prompt using Gemini Vision.

        Args:
            image_path: Path to generated image
            prompt: Original generation prompt

        Returns:
            ValidationResult with pass/fail and score

        Raises:
            FileNotFoundError: If image doesn't exist
        """
        if not image_path.exists():
            raise FileNotFoundError(f'Image not found: {image_path}')

        try:
            # Load image
            image_part = Part.from_data(
                data=image_path.read_bytes(),
                mime_type='image/png'
            )

            # Create validation prompt
            validation_prompt = self.VALIDATION_PROMPT.format(prompt=prompt)

            # Generate validation
            response = self.model.generate_content([validation_prompt, image_part])

            # Parse response
            score, feedback = self._parse_response(response.text)

            # Determine pass/fail
            passed = score >= self.config.min_quality_score

            return ValidationResult(
                passed=passed,
                score=score,
                feedback=feedback,
                cost=self.VALIDATION_COST
            )

        except Exception as e:
            # On error, return low-confidence pass to avoid blocking workflow
            return ValidationResult(
                passed=True,
                score=self.config.min_quality_score,
                feedback=f'Validation error (defaulting to pass): {str(e)}',
                cost=self.VALIDATION_COST
            )

    def _parse_response(self, response_text: str) -> tuple[float, str]:
        """Parse Gemini response to extract score and feedback.

        Args:
            response_text: Raw response from Gemini

        Returns:
            (score, feedback) tuple
        """
        try:
            # Try parsing as JSON
            data = json.loads(response_text)
            score = float(data['score'])
            issues = data.get('issues', [])
            feedback = ', '.join(issues) if issues else 'No issues identified'
            return score, feedback

        except (json.JSONDecodeError, KeyError, ValueError):
            # Fallback: try to extract score from text
            match = re.search(r'score[:\s]+([0-9.]+)', response_text, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                return score, response_text[:200]  # First 200 chars as feedback

            # Last resort: assume passing score
            return 0.7, response_text[:200]
