# Flux/Gemini AI Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add AI-generated hero images using Flux (Replicate) and Gemini/Imagen (Vertex AI) with quality validation and cost tracking, while maintaining full backward compatibility with v1.1.0 programmatic generation.

**Architecture:** Option A (Separate Modes) - Wizard asks upfront whether to use programmatic themes or AI models. Two completely separate code paths after initial choice. New `hero_image_generator/ai/` module with base abstractions, Flux/Gemini implementations, cost tracking, and quality validation.

**Tech Stack:** Python 3.8+, Pillow, Replicate SDK, Google Cloud AI Platform, python-dotenv

---

## Prerequisites

- Replicate API token (sign up at replicate.com)
- Google Cloud project with Vertex AI enabled
- Service account JSON key with Vertex AI User role

---

## Task 1: Create AI Module Base Structure

**Files:**
- Create: `hero_image_generator/ai/__init__.py`
- Create: `hero_image_generator/ai/base.py`
- Create: `hero_image_generator/ai/config.py`
- Create: `.env.example`
- Modify: `.gitignore`
- Create: `tests/ai/__init__.py`
- Create: `tests/ai/test_config.py`

### Step 1: Write failing test for config loader

Create `tests/ai/__init__.py`:
```python
"""Tests for AI module."""
```

Create `tests/ai/test_config.py`:
```python
"""Tests for AI configuration management."""
import os
import pytest
from hero_image_generator.ai.config import AIConfig, ConfigurationError


def test_load_config_with_all_env_vars(monkeypatch):
    """Test loading config when all env vars are present."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')
    monkeypatch.setenv('GCP_LOCATION', 'us-central1')
    monkeypatch.setenv('DEFAULT_MODEL', 'flux-pro')
    monkeypatch.setenv('FALLBACK_MODEL', 'imagen')

    config = AIConfig.load()

    assert config.replicate_api_token == 'test_token'
    assert config.gcp_project_id == 'test_project'
    assert config.gcp_location == 'us-central1'
    assert config.default_model == 'flux-pro'
    assert config.fallback_model == 'imagen'


def test_load_config_missing_replicate_token(monkeypatch):
    """Test config fails when Replicate token is missing."""
    monkeypatch.delenv('REPLICATE_API_TOKEN', raising=False)

    with pytest.raises(ConfigurationError, match='REPLICATE_API_TOKEN'):
        AIConfig.load()


def test_config_default_values(monkeypatch):
    """Test config uses sensible defaults."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')

    config = AIConfig.load()

    assert config.gcp_location == 'us-central1'
    assert config.default_model == 'flux-pro'
    assert config.fallback_model == 'imagen'
    assert config.enable_quality_check is True
    assert config.min_quality_score == 0.6


def test_config_size_parsing():
    """Test image size parsing from strings."""
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test')
    monkeypatch.setenv('SIZE_SMALL', '800x450')
    monkeypatch.setenv('SIZE_MEDIUM', '1920x1080')
    monkeypatch.setenv('SIZE_LARGE', '2560x1440')

    config = AIConfig.load()

    assert config.size_small == (800, 450)
    assert config.size_medium == (1920, 1080)
    assert config.size_large == (2560, 1440)
```

### Step 2: Run test to verify it fails

```bash
pytest tests/ai/test_config.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'hero_image_generator.ai'`

### Step 3: Create AI module structure

Create `hero_image_generator/ai/__init__.py`:
```python
"""AI-powered hero image generation module.

This module provides AI-generated hero images using:
- Flux models (via Replicate API)
- Gemini/Imagen models (via Google Vertex AI)
- Quality validation with Gemini Vision
- Cost tracking and reporting
"""

from .config import AIConfig, ConfigurationError
from .base import BaseAIModel, GenerationError

__all__ = ['AIConfig', 'ConfigurationError', 'BaseAIModel', 'GenerationError']
```

Create `hero_image_generator/ai/base.py`:
```python
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
```

Create `hero_image_generator/ai/config.py`:
```python
"""Configuration management for AI module."""
import os
from typing import Tuple, Optional
from pathlib import Path
from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when configuration is invalid or incomplete."""
    pass


class AIConfig:
    """AI module configuration loaded from environment variables."""

    def __init__(
        self,
        replicate_api_token: str,
        gcp_project_id: str,
        gcp_location: str = 'us-central1',
        google_application_credentials: Optional[str] = None,
        default_model: str = 'flux-pro',
        fallback_model: str = 'imagen',
        enable_quality_check: bool = True,
        min_quality_score: float = 0.6,
        size_small: Tuple[int, int] = (800, 450),
        size_medium: Tuple[int, int] = (1920, 1080),
        size_large: Tuple[int, int] = (2560, 1440),
        output_directory: str = 'public/images',
        failed_output_directory: str = 'public/images/failed',
        save_failed_generations: bool = True,
        log_costs: bool = True,
        cost_log_file: str = 'generation_costs.log',
        max_retries: int = 2,
        retry_delay_seconds: int = 5
    ):
        self.replicate_api_token = replicate_api_token
        self.gcp_project_id = gcp_project_id
        self.gcp_location = gcp_location
        self.google_application_credentials = google_application_credentials
        self.default_model = default_model
        self.fallback_model = fallback_model
        self.enable_quality_check = enable_quality_check
        self.min_quality_score = min_quality_score
        self.size_small = size_small
        self.size_medium = size_medium
        self.size_large = size_large
        self.output_directory = output_directory
        self.failed_output_directory = failed_output_directory
        self.save_failed_generations = save_failed_generations
        self.log_costs = log_costs
        self.cost_log_file = cost_log_file
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    @classmethod
    def load(cls, env_file: Optional[Path] = None) -> 'AIConfig':
        """Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file. If None, looks for .env in current directory.

        Returns:
            AIConfig instance

        Raises:
            ConfigurationError: If required env vars are missing
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()  # Load from .env in current directory

        # Required variables
        replicate_token = os.getenv('REPLICATE_API_TOKEN')
        if not replicate_token:
            raise ConfigurationError(
                'REPLICATE_API_TOKEN environment variable is required. '
                'Get your token at https://replicate.com/account/api-tokens'
            )

        gcp_project = os.getenv('GCP_PROJECT_ID')
        if not gcp_project:
            raise ConfigurationError(
                'GCP_PROJECT_ID environment variable is required. '
                'Create a project at https://console.cloud.google.com'
            )

        # Optional variables with defaults
        gcp_location = os.getenv('GCP_LOCATION', 'us-central1')
        gcp_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        default_model = os.getenv('DEFAULT_MODEL', 'flux-pro')
        fallback_model = os.getenv('FALLBACK_MODEL', 'imagen')

        enable_qc = os.getenv('ENABLE_QUALITY_CHECK', 'true').lower() == 'true'
        min_quality = float(os.getenv('MIN_QUALITY_SCORE', '0.6'))

        # Parse sizes
        size_small = cls._parse_size(os.getenv('SIZE_SMALL', '800x450'))
        size_medium = cls._parse_size(os.getenv('SIZE_MEDIUM', '1920x1080'))
        size_large = cls._parse_size(os.getenv('SIZE_LARGE', '2560x1440'))

        output_dir = os.getenv('OUTPUT_DIRECTORY', 'public/images')
        failed_dir = os.getenv('FAILED_OUTPUT_DIRECTORY', 'public/images/failed')
        save_failed = os.getenv('SAVE_FAILED_GENERATIONS', 'true').lower() == 'true'

        log_costs = os.getenv('LOG_COSTS', 'true').lower() == 'true'
        cost_log = os.getenv('COST_LOG_FILE', 'generation_costs.log')

        max_retries = int(os.getenv('MAX_RETRIES', '2'))
        retry_delay = int(os.getenv('RETRY_DELAY_SECONDS', '5'))

        return cls(
            replicate_api_token=replicate_token,
            gcp_project_id=gcp_project,
            gcp_location=gcp_location,
            google_application_credentials=gcp_creds,
            default_model=default_model,
            fallback_model=fallback_model,
            enable_quality_check=enable_qc,
            min_quality_score=min_quality,
            size_small=size_small,
            size_medium=size_medium,
            size_large=size_large,
            output_directory=output_dir,
            failed_output_directory=failed_dir,
            save_failed_generations=save_failed,
            log_costs=log_costs,
            cost_log_file=cost_log,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay
        )

    @staticmethod
    def _parse_size(size_str: str) -> Tuple[int, int]:
        """Parse size string like '1920x1080' into (width, height) tuple."""
        try:
            width, height = size_str.split('x')
            return (int(width), int(height))
        except (ValueError, AttributeError):
            raise ConfigurationError(f'Invalid size format: {size_str}. Expected format: WIDTHxHEIGHT')
```

### Step 4: Update .gitignore

Append to `.gitignore`:
```
# AI module
.env
*.json
generation_costs.log
public/images/failed/
```

### Step 5: Create .env.example

Create `.env.example`:
```bash
# Replicate API Configuration
REPLICATE_API_TOKEN=your_token_here

# Google Cloud Platform Configuration
GCP_PROJECT_ID=your_project_id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Model Selection
DEFAULT_MODEL=flux-pro
FALLBACK_MODEL=imagen

# Quality Validation
ENABLE_QUALITY_CHECK=true
MIN_QUALITY_SCORE=0.6

# Image Sizes (WIDTHxHEIGHT)
SIZE_SMALL=800x450
SIZE_MEDIUM=1920x1080
SIZE_LARGE=2560x1440

# Output Configuration
OUTPUT_DIRECTORY=public/images
FAILED_OUTPUT_DIRECTORY=public/images/failed
SAVE_FAILED_GENERATIONS=true

# Cost Tracking
LOG_COSTS=true
COST_LOG_FILE=generation_costs.log

# Retry Logic
MAX_RETRIES=2
RETRY_DELAY_SECONDS=5
```

### Step 6: Run tests to verify they pass

```bash
pytest tests/ai/test_config.py -v
```

Expected: PASS (all 4 tests)

### Step 7: Commit

```bash
git add hero_image_generator/ai/ tests/ai/ .gitignore .env.example
git commit -m "feat: add AI module base structure and config loader (#2)"
```

---

## Task 2: Implement Flux Model Integration

**Files:**
- Create: `hero_image_generator/ai/flux.py`
- Create: `tests/ai/test_flux.py`
- Modify: `requirements.txt`
- Modify: `hero_image_generator/ai/__init__.py`

### Step 1: Add Replicate dependency

Modify `requirements.txt`:
```
Pillow>=10.0.0
replicate>=0.25.0
python-dotenv>=1.0.0
```

Install:
```bash
pip install -r requirements.txt
```

### Step 2: Write failing test for Flux model

Create `tests/ai/test_flux.py`:
```python
"""Tests for Flux model integration."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from hero_image_generator.ai.flux import FluxModel
from hero_image_generator.ai.config import AIConfig
from hero_image_generator.ai.base import GenerationError


@pytest.fixture
def mock_config(monkeypatch):
    """Create mock AIConfig for testing."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')
    return AIConfig.load()


def test_flux_pro_model_name(mock_config):
    """Test Flux Pro model has correct name."""
    model = FluxModel(mock_config, variant='pro')
    assert model.name == 'Flux Pro'


def test_flux_dev_model_name(mock_config):
    """Test Flux Dev model has correct name."""
    model = FluxModel(mock_config, variant='dev')
    assert model.name == 'Flux Dev'


def test_flux_schnell_model_name(mock_config):
    """Test Flux Schnell model has correct name."""
    model = FluxModel(mock_config, variant='schnell')
    assert model.name == 'Flux Schnell'


def test_flux_pro_cost(mock_config):
    """Test Flux Pro returns correct cost."""
    model = FluxModel(mock_config, variant='pro')
    assert model.get_cost_per_image() == 0.055


def test_flux_dev_cost(mock_config):
    """Test Flux Dev returns correct cost."""
    model = FluxModel(mock_config, variant='dev')
    assert model.get_cost_per_image() == 0.020


def test_flux_schnell_cost(mock_config):
    """Test Flux Schnell returns correct cost."""
    model = FluxModel(mock_config, variant='schnell')
    assert model.get_cost_per_image() == 0.010


@patch('hero_image_generator.ai.flux.replicate')
@patch('hero_image_generator.ai.flux.requests')
def test_flux_generate_success(mock_requests, mock_replicate, mock_config, tmp_path):
    """Test successful image generation with Flux."""
    # Mock Replicate API response
    mock_output = Mock()
    mock_output.__getitem__ = Mock(return_value='https://example.com/image.png')
    mock_replicate.run.return_value = mock_output

    # Mock image download
    mock_response = Mock()
    mock_response.content = b'fake_image_data'
    mock_response.raise_for_status = Mock()
    mock_requests.get.return_value = mock_response

    # Generate image
    model = FluxModel(mock_config, variant='pro')
    output_path = tmp_path / 'output.png'

    result = model.generate(
        prompt='Test prompt',
        size=(1920, 1080),
        output_path=output_path
    )

    # Verify
    assert result == output_path
    assert output_path.exists()
    mock_replicate.run.assert_called_once()
    mock_requests.get.assert_called_once_with('https://example.com/image.png', timeout=60)


@patch('hero_image_generator.ai.flux.replicate')
def test_flux_generate_api_failure(mock_replicate, mock_config, tmp_path):
    """Test generation fails gracefully on API error."""
    mock_replicate.run.side_effect = Exception('API Error')

    model = FluxModel(mock_config, variant='pro')
    output_path = tmp_path / 'output.png'

    with pytest.raises(GenerationError, match='Flux generation failed'):
        model.generate('Test prompt', (1920, 1080), output_path)


def test_flux_invalid_variant(mock_config):
    """Test invalid variant raises error."""
    with pytest.raises(ValueError, match='Invalid Flux variant'):
        FluxModel(mock_config, variant='invalid')
```

### Step 3: Run test to verify it fails

```bash
pytest tests/ai/test_flux.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'hero_image_generator.ai.flux'`

### Step 4: Implement Flux model

Create `hero_image_generator/ai/flux.py`:
```python
"""Flux model integration via Replicate API."""
import os
from pathlib import Path
from typing import Tuple
import replicate
import requests

from .base import BaseAIModel, GenerationError
from .config import AIConfig


class FluxModel(BaseAIModel):
    """Flux image generation model via Replicate.

    Supports three variants:
    - pro: Highest quality, ~$0.055 per image
    - dev: Good quality, ~$0.020 per image
    - schnell: Fastest, ~$0.010 per image
    """

    COSTS = {
        'pro': 0.055,
        'dev': 0.020,
        'schnell': 0.010
    }

    MODEL_IDS = {
        'pro': 'black-forest-labs/flux-pro',
        'dev': 'black-forest-labs/flux-dev',
        'schnell': 'black-forest-labs/flux-schnell'
    }

    def __init__(self, config: AIConfig, variant: str = 'pro'):
        """Initialize Flux model.

        Args:
            config: AIConfig instance
            variant: One of 'pro', 'dev', 'schnell'

        Raises:
            ValueError: If variant is invalid
        """
        super().__init__(config)

        if variant not in self.COSTS:
            raise ValueError(
                f'Invalid Flux variant: {variant}. '
                f'Must be one of: {", ".join(self.COSTS.keys())}'
            )

        self.variant = variant

        # Set Replicate API token
        os.environ['REPLICATE_API_TOKEN'] = config.replicate_api_token

    @property
    def name(self) -> str:
        """Human-readable model name."""
        return f'Flux {self.variant.capitalize()}'

    def get_cost_per_image(self) -> float:
        """Return cost in USD per image."""
        return self.COSTS[self.variant]

    def generate(
        self,
        prompt: str,
        size: Tuple[int, int],
        output_path: Path
    ) -> Path:
        """Generate image using Flux model.

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

            # Run Flux generation
            output = replicate.run(
                self.MODEL_IDS[self.variant],
                input={
                    'prompt': prompt,
                    'width': width,
                    'height': height,
                    'num_outputs': 1,
                    'guidance_scale': 7.5,
                    'num_inference_steps': 50 if self.variant == 'pro' else 28
                }
            )

            # Output is a list of URLs
            image_url = output[0]

            # Download image
            response = requests.get(image_url, timeout=60)
            response.raise_for_status()

            # Save to output path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.content)

            return output_path

        except Exception as e:
            raise GenerationError(f'Flux generation failed: {str(e)}') from e
```

### Step 5: Update AI module exports

Modify `hero_image_generator/ai/__init__.py`:
```python
"""AI-powered hero image generation module.

This module provides AI-generated hero images using:
- Flux models (via Replicate API)
- Gemini/Imagen models (via Google Vertex AI)
- Quality validation with Gemini Vision
- Cost tracking and reporting
"""

from .config import AIConfig, ConfigurationError
from .base import BaseAIModel, GenerationError
from .flux import FluxModel

__all__ = [
    'AIConfig',
    'ConfigurationError',
    'BaseAIModel',
    'GenerationError',
    'FluxModel'
]
```

### Step 6: Run tests to verify they pass

```bash
pytest tests/ai/test_flux.py -v
```

Expected: PASS (all 9 tests)

### Step 7: Commit

```bash
git add hero_image_generator/ai/flux.py tests/ai/test_flux.py requirements.txt hero_image_generator/ai/__init__.py
git commit -m "feat: implement Flux model integration via Replicate (#2)"
```

---

## Task 3: Implement Gemini/Imagen Model Integration

**Files:**
- Create: `hero_image_generator/ai/gemini.py`
- Create: `tests/ai/test_gemini.py`
- Modify: `requirements.txt`
- Modify: `hero_image_generator/ai/__init__.py`

### Step 1: Add Google Cloud dependency

Modify `requirements.txt`:
```
Pillow>=10.0.0
replicate>=0.25.0
python-dotenv>=1.0.0
google-cloud-aiplatform>=1.38.0
```

Install:
```bash
pip install -r requirements.txt
```

### Step 2: Write failing test for Gemini/Imagen model

Create `tests/ai/test_gemini.py`:
```python
"""Tests for Gemini/Imagen model integration."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from hero_image_generator.ai.gemini import GeminiModel
from hero_image_generator.ai.config import AIConfig
from hero_image_generator.ai.base import GenerationError


@pytest.fixture
def mock_config(monkeypatch):
    """Create mock AIConfig for testing."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')
    monkeypatch.setenv('GCP_LOCATION', 'us-central1')
    return AIConfig.load()


def test_gemini_model_name(mock_config):
    """Test Gemini model has correct name."""
    model = GeminiModel(mock_config, use_imagen=True)
    assert model.name == 'Imagen'

    model_flash = GeminiModel(mock_config, use_imagen=False)
    assert model_flash.name == 'Gemini 2.0 Flash'


def test_gemini_cost(mock_config):
    """Test Gemini returns correct cost."""
    model = GeminiModel(mock_config)
    assert model.get_cost_per_image() == 0.020


@patch('hero_image_generator.ai.gemini.aiplatform')
@patch('hero_image_generator.ai.gemini.ImageGenerationModel')
def test_imagen_generate_success(mock_img_gen_model, mock_aiplatform, mock_config, tmp_path):
    """Test successful image generation with Imagen."""
    # Mock Vertex AI initialization
    mock_aiplatform.init = Mock()

    # Mock image generation response
    mock_image = Mock()
    mock_image._pil_image = Mock()
    mock_image._pil_image.save = Mock()

    mock_response = Mock()
    mock_response.images = [mock_image]

    mock_model_instance = Mock()
    mock_model_instance.generate_images.return_value = mock_response
    mock_img_gen_model.from_pretrained.return_value = mock_model_instance

    # Generate image
    model = GeminiModel(mock_config, use_imagen=True)
    output_path = tmp_path / 'output.png'

    result = model.generate(
        prompt='Test prompt',
        size=(1920, 1080),
        output_path=output_path
    )

    # Verify
    assert result == output_path
    mock_aiplatform.init.assert_called_once()
    mock_model_instance.generate_images.assert_called_once()
    mock_image._pil_image.save.assert_called_once()


@patch('hero_image_generator.ai.gemini.aiplatform')
@patch('hero_image_generator.ai.gemini.ImageGenerationModel')
def test_imagen_generate_api_failure(mock_img_gen_model, mock_aiplatform, mock_config, tmp_path):
    """Test generation fails gracefully on API error."""
    mock_aiplatform.init = Mock()
    mock_model_instance = Mock()
    mock_model_instance.generate_images.side_effect = Exception('API Error')
    mock_img_gen_model.from_pretrained.return_value = mock_model_instance

    model = GeminiModel(mock_config, use_imagen=True)
    output_path = tmp_path / 'output.png'

    with pytest.raises(GenerationError, match='Gemini/Imagen generation failed'):
        model.generate('Test prompt', (1920, 1080), output_path)


def test_aspect_ratio_calculation(mock_config):
    """Test aspect ratio calculation for different sizes."""
    model = GeminiModel(mock_config)

    assert model._calculate_aspect_ratio((1920, 1080)) == '16:9'
    assert model._calculate_aspect_ratio((1200, 630)) == '1:1'  # Closest match
    assert model._calculate_aspect_ratio((800, 800)) == '1:1'
    assert model._calculate_aspect_ratio((1600, 900)) == '16:9'
```

### Step 3: Run test to verify it fails

```bash
pytest tests/ai/test_gemini.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'hero_image_generator.ai.gemini'`

### Step 4: Implement Gemini/Imagen model

Create `hero_image_generator/ai/gemini.py`:
```python
"""Gemini/Imagen model integration via Google Vertex AI."""
import os
from pathlib import Path
from typing import Tuple
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

from .base import BaseAIModel, GenerationError
from .config import AIConfig


class GeminiModel(BaseAIModel):
    """Gemini/Imagen image generation via Vertex AI.

    Supports:
    - Imagen (imagegeneration@006): Stable, production-ready
    - Gemini 2.0 Flash: Experimental image generation

    Cost: ~$0.020 per image
    """

    COST_PER_IMAGE = 0.020

    def __init__(self, config: AIConfig, use_imagen: bool = True):
        """Initialize Gemini/Imagen model.

        Args:
            config: AIConfig instance
            use_imagen: If True, use stable Imagen. If False, use experimental Gemini 2.0 Flash
        """
        super().__init__(config)
        self.use_imagen = use_imagen

        # Initialize Vertex AI
        credentials_path = config.google_application_credentials
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

        aiplatform.init(
            project=config.gcp_project_id,
            location=config.gcp_location
        )

    @property
    def name(self) -> str:
        """Human-readable model name."""
        return 'Imagen' if self.use_imagen else 'Gemini 2.0 Flash'

    def get_cost_per_image(self) -> float:
        """Return cost in USD per image."""
        return self.COST_PER_IMAGE

    def generate(
        self,
        prompt: str,
        size: Tuple[int, int],
        output_path: Path
    ) -> Path:
        """Generate image using Gemini/Imagen.

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
            # Calculate aspect ratio
            aspect_ratio = self._calculate_aspect_ratio(size)

            # Load model
            model = ImageGenerationModel.from_pretrained('imagegeneration@006')

            # Generate image
            response = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio=aspect_ratio,
                safety_filter_level='block_some',
                person_generation='allow_adult'
            )

            # Get first image
            image = response.images[0]

            # Save image
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image._pil_image.save(str(output_path))

            return output_path

        except Exception as e:
            raise GenerationError(f'Gemini/Imagen generation failed: {str(e)}') from e

    def _calculate_aspect_ratio(self, size: Tuple[int, int]) -> str:
        """Calculate closest supported aspect ratio.

        Supported ratios: 1:1, 3:4, 4:3, 9:16, 16:9

        Args:
            size: (width, height) tuple

        Returns:
            Aspect ratio string like '16:9'
        """
        width, height = size
        ratio = width / height

        # Map to closest supported ratio
        if abs(ratio - 1.0) < 0.2:  # Close to 1:1
            return '1:1'
        elif abs(ratio - 0.75) < 0.2:  # Close to 3:4
            return '3:4'
        elif abs(ratio - 1.333) < 0.2:  # Close to 4:3
            return '4:3'
        elif abs(ratio - 0.5625) < 0.2:  # Close to 9:16
            return '9:16'
        else:  # Default to 16:9
            return '16:9'
```

### Step 5: Update AI module exports

Modify `hero_image_generator/ai/__init__.py`:
```python
"""AI-powered hero image generation module.

This module provides AI-generated hero images using:
- Flux models (via Replicate API)
- Gemini/Imagen models (via Google Vertex AI)
- Quality validation with Gemini Vision
- Cost tracking and reporting
"""

from .config import AIConfig, ConfigurationError
from .base import BaseAIModel, GenerationError
from .flux import FluxModel
from .gemini import GeminiModel

__all__ = [
    'AIConfig',
    'ConfigurationError',
    'BaseAIModel',
    'GenerationError',
    'FluxModel',
    'GeminiModel'
]
```

### Step 6: Run tests to verify they pass

```bash
pytest tests/ai/test_gemini.py -v
```

Expected: PASS (all 5 tests)

### Step 7: Commit

```bash
git add hero_image_generator/ai/gemini.py tests/ai/test_gemini.py requirements.txt hero_image_generator/ai/__init__.py
git commit -m "feat: implement Gemini/Imagen model integration via Vertex AI (#2)"
```

---

## Task 4: Implement Cost Tracking Utility

**Files:**
- Create: `hero_image_generator/ai/cost_tracker.py`
- Create: `tests/ai/test_cost_tracker.py`
- Modify: `hero_image_generator/ai/__init__.py`

### Step 1: Write failing test for cost tracker

Create `tests/ai/test_cost_tracker.py`:
```python
"""Tests for cost tracking utility."""
import pytest
from pathlib import Path
from datetime import datetime
from hero_image_generator.ai.cost_tracker import CostTracker


def test_track_single_generation(tmp_path):
    """Test tracking a single generation."""
    log_file = tmp_path / 'costs.log'
    tracker = CostTracker(log_file)

    tracker.track(
        model='flux-pro',
        cost=0.055,
        status='success',
        image_path='test.png',
        size=(1920, 1080)
    )

    assert tracker.get_session_total() == 0.055
    assert log_file.exists()


def test_track_multiple_generations(tmp_path):
    """Test tracking multiple generations."""
    log_file = tmp_path / 'costs.log'
    tracker = CostTracker(log_file)

    tracker.track('flux-pro', 0.055, 'success', 'test1.png', (1920, 1080))
    tracker.track('imagen', 0.020, 'success', 'test2.png', (1920, 1080))
    tracker.track('flux-dev', 0.020, 'retry', 'test3.png', (1920, 1080))

    assert tracker.get_session_total() == 0.095


def test_track_with_validation_cost(tmp_path):
    """Test tracking generation with quality validation."""
    log_file = tmp_path / 'costs.log'
    tracker = CostTracker(log_file)

    tracker.track(
        'flux-pro',
        0.055,
        'success',
        'test.png',
        (1920, 1080),
        validation_cost=0.001
    )

    assert tracker.get_session_total() == 0.056


def test_log_file_format(tmp_path):
    """Test log file has correct format."""
    log_file = tmp_path / 'costs.log'
    tracker = CostTracker(log_file)

    tracker.track('flux-pro', 0.055, 'success', 'hero_001.png', (1920, 1080))

    content = log_file.read_text()
    assert 'hero_001.png' in content
    assert 'flux-pro' in content
    assert '1920x1080' in content
    assert '$0.055' in content
    assert 'success' in content


def test_session_cost_breakdown(tmp_path):
    """Test getting cost breakdown by model."""
    log_file = tmp_path / 'costs.log'
    tracker = CostTracker(log_file)

    tracker.track('flux-pro', 0.055, 'success', 'test1.png', (1920, 1080))
    tracker.track('flux-pro', 0.055, 'success', 'test2.png', (1920, 1080))
    tracker.track('imagen', 0.020, 'success', 'test3.png', (1920, 1080))

    breakdown = tracker.get_breakdown()

    assert breakdown['flux-pro'] == 0.110
    assert breakdown['imagen'] == 0.020
    assert breakdown['total'] == 0.130


def test_cost_tracker_no_logging(tmp_path):
    """Test cost tracker with logging disabled."""
    tracker = CostTracker(None)  # No log file

    tracker.track('flux-pro', 0.055, 'success', 'test.png', (1920, 1080))

    # Should still track session total even without file logging
    assert tracker.get_session_total() == 0.055
```

### Step 2: Run test to verify it fails

```bash
pytest tests/ai/test_cost_tracker.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'hero_image_generator.ai.cost_tracker'`

### Step 3: Implement cost tracker

Create `hero_image_generator/ai/cost_tracker.py`:
```python
"""Cost tracking for AI image generation."""
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime
from collections import defaultdict


class CostTracker:
    """Track and log costs for AI image generation."""

    def __init__(self, log_file: Optional[Path] = None):
        """Initialize cost tracker.

        Args:
            log_file: Path to log file. If None, logging is disabled.
        """
        self.log_file = Path(log_file) if log_file else None
        self.session_costs: Dict[str, float] = defaultdict(float)
        self.session_total = 0.0

        # Create log file with header if it doesn't exist
        if self.log_file and not self.log_file.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self.log_file.write_text(
                '# AI Hero Image Generation Cost Log\n'
                '# Format: [timestamp] Image | Model | Size | Cost | Status\n\n'
            )

    def track(
        self,
        model: str,
        cost: float,
        status: str,
        image_path: str,
        size: Tuple[int, int],
        validation_cost: float = 0.0
    ) -> None:
        """Track a generation cost.

        Args:
            model: Model name (e.g., 'flux-pro', 'imagen')
            cost: Generation cost in USD
            status: Status string (e.g., 'success', 'retry', 'failed')
            image_path: Path to generated image
            size: (width, height) tuple
            validation_cost: Optional quality validation cost
        """
        total_cost = cost + validation_cost

        # Update session tracking
        self.session_costs[model] += total_cost
        self.session_total += total_cost

        # Log to file if enabled
        if self.log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            width, height = size

            log_entry = (
                f'[{timestamp}] '
                f'{image_path} | '
                f'Model: {model} | '
                f'Size: {width}x{height} | '
                f'Cost: ${total_cost:.3f}'
            )

            if validation_cost > 0:
                log_entry += f' (gen: ${cost:.3f}, validation: ${validation_cost:.3f})'

            log_entry += f' | Status: {status}\n'

            # Append to log file
            with self.log_file.open('a') as f:
                f.write(log_entry)

    def get_session_total(self) -> float:
        """Get total cost for current session.

        Returns:
            Total cost in USD
        """
        return self.session_total

    def get_breakdown(self) -> Dict[str, float]:
        """Get cost breakdown by model.

        Returns:
            Dictionary with model names as keys and costs as values,
            plus 'total' key with session total
        """
        breakdown = dict(self.session_costs)
        breakdown['total'] = self.session_total
        return breakdown

    def display_summary(self) -> str:
        """Generate human-readable cost summary.

        Returns:
            Formatted string with cost breakdown
        """
        if self.session_total == 0:
            return 'No generations tracked in this session.'

        lines = ['Cost Summary:', '-' * 40]

        for model, cost in sorted(self.session_costs.items()):
            lines.append(f'  {model}: ${cost:.3f}')

        lines.append('-' * 40)
        lines.append(f'  Total: ${self.session_total:.3f}')

        return '\n'.join(lines)
```

### Step 4: Update AI module exports

Modify `hero_image_generator/ai/__init__.py`:
```python
"""AI-powered hero image generation module.

This module provides AI-generated hero images using:
- Flux models (via Replicate API)
- Gemini/Imagen models (via Google Vertex AI)
- Quality validation with Gemini Vision
- Cost tracking and reporting
"""

from .config import AIConfig, ConfigurationError
from .base import BaseAIModel, GenerationError
from .flux import FluxModel
from .gemini import GeminiModel
from .cost_tracker import CostTracker

__all__ = [
    'AIConfig',
    'ConfigurationError',
    'BaseAIModel',
    'GenerationError',
    'FluxModel',
    'GeminiModel',
    'CostTracker'
]
```

### Step 5: Run tests to verify they pass

```bash
pytest tests/ai/test_cost_tracker.py -v
```

Expected: PASS (all 7 tests)

### Step 6: Commit

```bash
git add hero_image_generator/ai/cost_tracker.py tests/ai/test_cost_tracker.py hero_image_generator/ai/__init__.py
git commit -m "feat: implement cost tracking utility (#2)"
```

---

## Task 5: Implement Quality Validator with Gemini Vision

**Files:**
- Create: `hero_image_generator/ai/quality_validator.py`
- Create: `tests/ai/test_quality_validator.py`
- Modify: `hero_image_generator/ai/__init__.py`

### Step 1: Write failing test for quality validator

Create `tests/ai/test_quality_validator.py`:
```python
"""Tests for quality validation using Gemini Vision."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from hero_image_generator.ai.quality_validator import QualityValidator, ValidationResult
from hero_image_generator.ai.config import AIConfig


@pytest.fixture
def mock_config(monkeypatch):
    """Create mock AIConfig for testing."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')
    monkeypatch.setenv('MIN_QUALITY_SCORE', '0.6')
    return AIConfig.load()


def test_validation_result_pass():
    """Test ValidationResult for passing validation."""
    result = ValidationResult(
        passed=True,
        score=0.85,
        feedback='Good match',
        cost=0.001
    )

    assert result.passed is True
    assert result.score == 0.85
    assert result.feedback == 'Good match'
    assert result.cost == 0.001


def test_validation_result_fail():
    """Test ValidationResult for failing validation."""
    result = ValidationResult(
        passed=False,
        score=0.45,
        feedback='Poor match',
        cost=0.001
    )

    assert result.passed is False
    assert result.score == 0.45


@patch('hero_image_generator.ai.quality_validator.aiplatform')
@patch('hero_image_generator.ai.quality_validator.GenerativeModel')
def test_validate_image_success(mock_gen_model, mock_aiplatform, mock_config, tmp_path):
    """Test successful image validation."""
    # Create fake image
    image_path = tmp_path / 'test.png'
    image_path.write_bytes(b'fake_image_data')

    # Mock Vertex AI initialization
    mock_aiplatform.init = Mock()

    # Mock Gemini response with JSON
    mock_response = Mock()
    mock_response.text = '{"score": 0.85, "breakdown": {"subject": 0.35, "style": 0.25, "quality": 0.25}, "issues": []}'

    mock_model_instance = Mock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_gen_model.return_value = mock_model_instance

    # Validate
    validator = QualityValidator(mock_config)
    result = validator.validate(image_path, 'Test prompt')

    # Verify
    assert result.passed is True
    assert result.score == 0.85
    assert result.cost == 0.001
    mock_aiplatform.init.assert_called_once()


@patch('hero_image_generator.ai.quality_validator.aiplatform')
@patch('hero_image_generator.ai.quality_validator.GenerativeModel')
def test_validate_image_fail(mock_gen_model, mock_aiplatform, mock_config, tmp_path):
    """Test image validation failure."""
    image_path = tmp_path / 'test.png'
    image_path.write_bytes(b'fake_image_data')

    mock_aiplatform.init = Mock()

    # Mock low score response
    mock_response = Mock()
    mock_response.text = '{"score": 0.45, "breakdown": {"subject": 0.15, "style": 0.15, "quality": 0.15}, "issues": ["Poor subject match"]}'

    mock_model_instance = Mock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_gen_model.return_value = mock_model_instance

    # Validate
    validator = QualityValidator(mock_config)
    result = validator.validate(image_path, 'Test prompt')

    # Verify
    assert result.passed is False
    assert result.score == 0.45
    assert 'Poor subject match' in result.feedback


@patch('hero_image_generator.ai.quality_validator.aiplatform')
@patch('hero_image_generator.ai.quality_validator.GenerativeModel')
def test_validate_handles_non_json_response(mock_gen_model, mock_aiplatform, mock_config, tmp_path):
    """Test validation handles non-JSON response gracefully."""
    image_path = tmp_path / 'test.png'
    image_path.write_bytes(b'fake_image_data')

    mock_aiplatform.init = Mock()

    # Mock non-JSON response
    mock_response = Mock()
    mock_response.text = 'This image is great! Score: 0.85'

    mock_model_instance = Mock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_gen_model.return_value = mock_model_instance

    # Validate
    validator = QualityValidator(mock_config)
    result = validator.validate(image_path, 'Test prompt')

    # Should extract score from text
    assert result.score == 0.85
    assert result.passed is True


def test_validate_missing_image(mock_config):
    """Test validation with missing image file."""
    validator = QualityValidator(mock_config)

    with pytest.raises(FileNotFoundError):
        validator.validate(Path('nonexistent.png'), 'Test prompt')
```

### Step 2: Run test to verify it fails

```bash
pytest tests/ai/test_quality_validator.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'hero_image_generator.ai.quality_validator'`

### Step 3: Implement quality validator

Create `hero_image_generator/ai/quality_validator.py`:
```python
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
```

### Step 4: Update AI module exports

Modify `hero_image_generator/ai/__init__.py`:
```python
"""AI-powered hero image generation module.

This module provides AI-generated hero images using:
- Flux models (via Replicate API)
- Gemini/Imagen models (via Google Vertex AI)
- Quality validation with Gemini Vision
- Cost tracking and reporting
"""

from .config import AIConfig, ConfigurationError
from .base import BaseAIModel, GenerationError
from .flux import FluxModel
from .gemini import GeminiModel
from .cost_tracker import CostTracker
from .quality_validator import QualityValidator, ValidationResult

__all__ = [
    'AIConfig',
    'ConfigurationError',
    'BaseAIModel',
    'GenerationError',
    'FluxModel',
    'GeminiModel',
    'CostTracker',
    'QualityValidator',
    'ValidationResult'
]
```

### Step 5: Run tests to verify they pass

```bash
pytest tests/ai/test_quality_validator.py -v
```

Expected: PASS (all 6 tests)

### Step 6: Commit

```bash
git add hero_image_generator/ai/quality_validator.py tests/ai/test_quality_validator.py hero_image_generator/ai/__init__.py
git commit -m "feat: implement quality validator with Gemini Vision (#2)"
```

---

## Task 6: Create AI Wizard Flow Module

**Files:**
- Create: `hero_image_generator/wizard/ai_wizard.py`
- Create: `tests/wizard/test_ai_wizard.py`

### Step 1: Write failing test for AI wizard

Create `tests/wizard/test_ai_wizard.py`:
```python
"""Tests for AI wizard flow."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from hero_image_generator.wizard.ai_wizard import AIWizardRunner


@pytest.fixture
def mock_config(monkeypatch, tmp_path):
    """Mock environment for AI wizard."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token')
    monkeypatch.setenv('GCP_PROJECT_ID', 'test_project')
    monkeypatch.setenv('OUTPUT_DIRECTORY', str(tmp_path))
    return tmp_path


def test_ai_wizard_initialization(mock_config):
    """Test AI wizard initializes correctly."""
    wizard = AIWizardRunner()
    assert wizard.config is not None
    assert wizard.cost_tracker is not None


@patch('hero_image_generator.wizard.ai_wizard.input')
def test_collect_prompt(mock_input, mock_config):
    """Test prompt collection."""
    mock_input.return_value = 'Professional hero image for AI consultancy'

    wizard = AIWizardRunner()
    prompt = wizard._collect_prompt()

    assert prompt == 'Professional hero image for AI consultancy'


@patch('hero_image_generator.wizard.ai_wizard.input')
def test_select_model_flux_pro(mock_input, mock_config):
    """Test model selection for Flux Pro."""
    mock_input.return_value = '1'  # Flux Pro

    wizard = AIWizardRunner()
    model = wizard._select_model()

    assert model.name == 'Flux Pro'


@patch('hero_image_generator.wizard.ai_wizard.input')
def test_select_size_medium(mock_input, mock_config):
    """Test size selection."""
    mock_input.return_value = '2'  # Medium

    wizard = AIWizardRunner()
    size = wizard._select_size()

    assert size == (1920, 1080)


@patch('hero_image_generator.wizard.ai_wizard.input')
def test_refinement_regenerate(mock_input, mock_config):
    """Test refinement choice - regenerate."""
    mock_input.return_value = '1'

    wizard = AIWizardRunner()
    choice = wizard._show_refinement_menu()

    assert choice == 'regenerate'


@patch('hero_image_generator.wizard.ai_wizard.input')
def test_refinement_modify_prompt(mock_input, mock_config):
    """Test refinement choice - modify prompt."""
    mock_input.return_value = '2'

    wizard = AIWizardRunner()
    choice = wizard._show_refinement_menu()

    assert choice == 'modify_prompt'
```

### Step 2: Run test to verify it fails

```bash
pytest tests/wizard/test_ai_wizard.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'hero_image_generator.wizard.ai_wizard'`

### Step 3: Implement AI wizard

Create `hero_image_generator/wizard/ai_wizard.py`:
```python
"""AI-powered hero image wizard flow."""
import sys
from pathlib import Path
from typing import Optional, Tuple
import tempfile

from ..ai import (
    AIConfig,
    FluxModel,
    GeminiModel,
    CostTracker,
    QualityValidator,
    BaseAIModel,
    GenerationError
)


class AIWizardRunner:
    """Interactive wizard for AI-generated hero images."""

    def __init__(self):
        """Initialize AI wizard."""
        try:
            self.config = AIConfig.load()
        except Exception as e:
            print(f'\nError loading AI configuration: {e}')
            print('\nPlease ensure you have:')
            print('1. Created a .env file (see .env.example)')
            print('2. Added your REPLICATE_API_TOKEN')
            print('3. Added your GCP_PROJECT_ID')
            sys.exit(1)

        # Initialize components
        log_file = Path(self.config.cost_log_file) if self.config.log_costs else None
        self.cost_tracker = CostTracker(log_file)
        self.quality_validator = QualityValidator(self.config) if self.config.enable_quality_check else None

        # State
        self.prompt: Optional[str] = None
        self.model: Optional[BaseAIModel] = None
        self.size: Optional[Tuple[int, int]] = None
        self.output_path: Optional[Path] = None

    def run(self) -> None:
        """Run the AI wizard flow."""
        print('\n' + '=' * 60)
        print('AI Hero Image Generator')
        print('=' * 60)

        try:
            # Collect inputs
            self.prompt = self._collect_prompt()
            self.model = self._select_model()
            self.size = self._select_size()

            # Show cost estimate
            self._show_cost_estimate()

            # Generation and refinement loop
            satisfied = False
            while not satisfied:
                # Generate image
                self._generate_and_preview()

                # Ask if satisfied
                satisfied = self._ask_satisfied()

                if not satisfied:
                    # Show refinement menu
                    choice = self._show_refinement_menu()

                    if choice == 'regenerate':
                        continue
                    elif choice == 'modify_prompt':
                        self.prompt = self._collect_prompt()
                    elif choice == 'change_model':
                        self.model = self._select_model()
                    elif choice == 'change_size':
                        self.size = self._select_size()
                    elif choice == 'cancel':
                        print('\nGeneration cancelled.')
                        return

            # Save final image
            self._save_final_image()

            # Show cost summary
            print('\n' + self.cost_tracker.display_summary())

        except KeyboardInterrupt:
            print('\n\nWizard cancelled by user.')
            sys.exit(0)

    def _collect_prompt(self) -> str:
        """Collect image generation prompt from user."""
        print('\n📝 Describe your hero image')
        print('Example: "Professional hero image for AI consultancy, modern and clean, ')
        print('         featuring abstract neural network patterns in blue and purple"')
        print()

        while True:
            prompt = input('Prompt: ').strip()
            if prompt:
                return prompt
            print('Prompt cannot be empty. Please try again.')

    def _select_model(self) -> BaseAIModel:
        """Let user select AI model."""
        print('\n🤖 Select AI Model')
        print('1. Flux Pro ($0.055/image) - Highest quality')
        print('2. Flux Dev ($0.020/image) - Good quality, faster')
        print('3. Flux Schnell ($0.010/image) - Fast iterations')
        print('4. Imagen ($0.020/image) - Google Vertex AI')
        print()

        while True:
            choice = input('Select model [1-4]: ').strip()

            if choice == '1':
                return FluxModel(self.config, variant='pro')
            elif choice == '2':
                return FluxModel(self.config, variant='dev')
            elif choice == '3':
                return FluxModel(self.config, variant='schnell')
            elif choice == '4':
                return GeminiModel(self.config, use_imagen=True)
            else:
                print('Invalid choice. Please enter 1, 2, 3, or 4.')

    def _select_size(self) -> Tuple[int, int]:
        """Let user select image size."""
        print('\n📐 Select Image Size')
        print(f'1. Small - {self.config.size_small[0]}x{self.config.size_small[1]}')
        print(f'2. Medium - {self.config.size_medium[0]}x{self.config.size_medium[1]}')
        print(f'3. Large - {self.config.size_large[0]}x{self.config.size_large[1]}')
        print()

        while True:
            choice = input('Select size [1-3]: ').strip()

            if choice == '1':
                return self.config.size_small
            elif choice == '2':
                return self.config.size_medium
            elif choice == '3':
                return self.config.size_large
            else:
                print('Invalid choice. Please enter 1, 2, or 3.')

    def _show_cost_estimate(self) -> None:
        """Show estimated cost for generation."""
        gen_cost = self.model.get_cost_per_image()
        val_cost = 0.001 if self.quality_validator else 0.0
        total = gen_cost + val_cost

        print(f'\n💰 Estimated cost: ${total:.3f}')
        if self.quality_validator:
            print(f'   (Generation: ${gen_cost:.3f}, Validation: ${val_cost:.3f})')

    def _generate_and_preview(self) -> None:
        """Generate image and show preview."""
        print(f'\n⏳ Generating image with {self.model.name}...')

        try:
            # Create temp file for preview
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                temp_path = Path(tmp.name)

            # Generate image
            self.output_path = self.model.generate(
                prompt=self.prompt,
                size=self.size,
                output_path=temp_path
            )

            # Track cost
            gen_cost = self.model.get_cost_per_image()

            # Validate if enabled
            val_cost = 0.0
            if self.quality_validator:
                print('🔍 Validating image quality...')
                result = self.quality_validator.validate(self.output_path, self.prompt)
                val_cost = result.cost

                if result.passed:
                    print(f'✓ Quality check passed (score: {result.score:.2f})')
                else:
                    print(f'⚠ Quality check failed (score: {result.score:.2f})')
                    print(f'  Issues: {result.feedback}')

            # Track total cost
            self.cost_tracker.track(
                model=self.model.name,
                cost=gen_cost,
                status='success',
                image_path=str(self.output_path),
                size=self.size,
                validation_cost=val_cost
            )

            print(f'✓ Image generated: {self.output_path}')
            print(f'💰 Cost: ${gen_cost + val_cost:.3f}')

            # Try to open preview
            self._open_preview()

        except GenerationError as e:
            print(f'❌ Generation failed: {e}')
            print('Try selecting a different model or modifying your prompt.')

    def _open_preview(self) -> None:
        """Open image preview in system viewer."""
        try:
            import subprocess
            import platform

            system = platform.system()
            if system == 'Darwin':  # macOS
                subprocess.run(['open', str(self.output_path)], check=False)
            elif system == 'Linux':
                subprocess.run(['xdg-open', str(self.output_path)], check=False)
            elif system == 'Windows':
                import os
                os.startfile(str(self.output_path))
            else:
                print(f'Preview not available on {system}. View file at: {self.output_path}')
        except Exception:
            print(f'Could not open preview. View file at: {self.output_path}')

    def _ask_satisfied(self) -> bool:
        """Ask if user is satisfied with generated image."""
        print()
        while True:
            response = input('Are you satisfied with this image? [y/n]: ').strip().lower()
            if response in ('y', 'yes'):
                return True
            elif response in ('n', 'no'):
                return False
            print('Please enter y or n.')

    def _show_refinement_menu(self) -> str:
        """Show refinement options and get user choice."""
        print('\n🔧 Refinement Options')
        print('1. Regenerate with same settings')
        print('2. Modify prompt')
        print('3. Change model')
        print('4. Change size')
        print('0. Cancel (discard image)')
        print()

        choices = {
            '1': 'regenerate',
            '2': 'modify_prompt',
            '3': 'change_model',
            '4': 'change_size',
            '0': 'cancel'
        }

        while True:
            choice = input('Select option [0-4]: ').strip()
            if choice in choices:
                return choices[choice]
            print('Invalid choice. Please enter 0, 1, 2, 3, or 4.')

    def _save_final_image(self) -> None:
        """Save final image to output directory."""
        # Get filename from user
        print('\n💾 Save Image')
        default_name = 'hero_image.png'
        filename = input(f'Filename [{default_name}]: ').strip() or default_name

        if not filename.endswith('.png'):
            filename += '.png'

        # Determine output path
        output_dir = Path(self.config.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        final_path = output_dir / filename

        # Copy temp file to final location
        import shutil
        shutil.copy(self.output_path, final_path)

        print(f'✓ Image saved to: {final_path}')
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/wizard/test_ai_wizard.py -v
```

Expected: PASS (all 6 tests)

### Step 5: Commit

```bash
git add hero_image_generator/wizard/ai_wizard.py tests/wizard/test_ai_wizard.py
git commit -m "feat: create AI wizard flow module (#2)"
```

---

## Task 7: Modify Main Wizard with Mode Selection

**Files:**
- Modify: `hero_image_generator/wizard/__init__.py`
- Modify: `tests/wizard/test_wizard_runner.py`

### Step 1: Write test for mode selection

Append to `tests/wizard/test_wizard_runner.py`:
```python
@patch('hero_image_generator.wizard.input')
def test_wizard_mode_selection_programmatic(mock_input):
    """Test selecting programmatic mode."""
    mock_input.return_value = '1'

    wizard = WizardRunner()
    mode = wizard._select_mode()

    assert mode == 'programmatic'


@patch('hero_image_generator.wizard.input')
def test_wizard_mode_selection_ai(mock_input):
    """Test selecting AI mode."""
    mock_input.return_value = '2'

    wizard = WizardRunner()
    mode = wizard._select_mode()

    assert mode == 'ai'
```

### Step 2: Run test to verify it fails

```bash
pytest tests/wizard/test_wizard_runner.py::test_wizard_mode_selection_programmatic -v
```

Expected: FAIL with `AttributeError: 'WizardRunner' object has no attribute '_select_mode'`

### Step 3: Modify WizardRunner to add mode selection

Modify `hero_image_generator/wizard/__init__.py`:

Find the `run()` method and add mode selection at the beginning:

```python
def run(self) -> None:
    """Run the interactive wizard."""
    print('\n' + '=' * 60)
    print('Hero Image Generator')
    print('=' * 60)

    try:
        # NEW: Mode selection
        mode = self._select_mode()

        if mode == 'ai':
            # Delegate to AI wizard
            from .ai_wizard import AIWizardRunner
            ai_wizard = AIWizardRunner()
            ai_wizard.run()
            return

        # EXISTING: Programmatic mode continues below
        self._load_config()

        # ... rest of existing wizard code
```

Add the mode selection method before `_load_config()`:

```python
def _select_mode(self) -> str:
    """Let user select generation mode.

    Returns:
        'programmatic' or 'ai'
    """
    print('\n🎨 How would you like to generate your hero image?')
    print('1. Programmatic themes (AI/ML, SEO, Automation, Strategy)')
    print('2. AI-generated (Flux/Gemini photorealistic images)')
    print()

    while True:
        choice = input('Select mode [1-2]: ').strip()

        if choice == '1':
            return 'programmatic'
        elif choice == '2':
            return 'ai'
        else:
            print('Invalid choice. Please enter 1 or 2.')
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/wizard/test_wizard_runner.py -v
```

Expected: PASS (including new tests)

### Step 5: Commit

```bash
git add hero_image_generator/wizard/__init__.py tests/wizard/test_wizard_runner.py
git commit -m "feat: add mode selection to main wizard (#2)"
```

---

## Task 8: Update CLI for AI Mode Flags

**Files:**
- Modify: `hero_image_generator/cli.py`
- Modify: `tests/test_cli.py`

### Step 1: Write tests for AI CLI flags

Append to `tests/test_cli.py`:
```python
@patch('hero_image_generator.cli.FluxModel')
@patch('hero_image_generator.cli.AIConfig')
def test_cli_ai_mode_flag(mock_config, mock_flux, monkeypatch):
    """Test --ai flag generates with AI model."""
    monkeypatch.setattr('sys.argv', [
        'hero-image-generator',
        '--ai',
        '--prompt', 'Test prompt',
        '--model', 'flux-pro',
        '--size', 'medium',
        '--output', 'test.png'
    ])

    # Mock config
    mock_config_instance = Mock()
    mock_config_instance.size_medium = (1920, 1080)
    mock_config.load.return_value = mock_config_instance

    # Mock model
    mock_model_instance = Mock()
    mock_model_instance.generate.return_value = Path('test.png')
    mock_flux.return_value = mock_model_instance

    # Run CLI
    main()

    # Verify
    mock_flux.assert_called_once()
    mock_model_instance.generate.assert_called_once()


def test_cli_backward_compatibility_no_args_launches_wizard(monkeypatch):
    """Test that no args still launches wizard (backward compatible)."""
    monkeypatch.setattr('sys.argv', ['hero-image-generator'])

    with patch('hero_image_generator.cli.WizardRunner') as mock_wizard:
        mock_wizard_instance = Mock()
        mock_wizard.return_value = mock_wizard_instance

        main()

        mock_wizard_instance.run.assert_called_once()
```

### Step 2: Run test to verify it fails

```bash
pytest tests/test_cli.py::test_cli_ai_mode_flag -v
```

Expected: FAIL (CLI doesn't recognize --ai flag yet)

### Step 3: Modify CLI to add AI mode support

Modify `hero_image_generator/cli.py`:

Add imports at the top:
```python
from pathlib import Path
from .ai import AIConfig, FluxModel, GeminiModel, CostTracker, GenerationError
```

Modify the argument parser section:
```python
parser = argparse.ArgumentParser(
    description='Generate professional hero images'
)

# NEW: AI mode flags
parser.add_argument(
    '--ai',
    action='store_true',
    help='Use AI generation (Flux/Gemini) instead of programmatic themes'
)
parser.add_argument(
    '--prompt',
    type=str,
    help='AI generation prompt (required with --ai)'
)
parser.add_argument(
    '--model',
    type=str,
    choices=['flux-pro', 'flux-dev', 'flux-schnell', 'imagen'],
    help='AI model to use (default: flux-pro)'
)
parser.add_argument(
    '--size',
    type=str,
    choices=['small', 'medium', 'large'],
    default='medium',
    help='Image size (default: medium)'
)
parser.add_argument(
    '--validate',
    action='store_true',
    default=True,
    help='Enable quality validation (default: enabled)'
)

# EXISTING: Programmatic mode flags
parser.add_argument(
    '--preview',
    action='store_true',
    help='Generate preview samples of all themes'
)
# ... rest of existing args
```

Add AI mode handler in `main()`:
```python
def main():
    """Main CLI entry point."""
    args = parser.parse_args()

    # No arguments: launch wizard
    if len(sys.argv) == 1:
        from .wizard import WizardRunner
        wizard = WizardRunner()
        wizard.run()
        return

    # NEW: AI mode
    if args.ai:
        handle_ai_mode(args)
        return

    # EXISTING: Programmatic mode
    if args.preview:
        generate_preview_samples(args.output_dir)
        return

    # ... rest of existing code


def handle_ai_mode(args):
    """Handle AI generation mode from CLI."""
    if not args.prompt:
        print('Error: --prompt is required when using --ai mode')
        sys.exit(1)

    try:
        # Load config
        config = AIConfig.load()

        # Parse size
        size_map = {
            'small': config.size_small,
            'medium': config.size_medium,
            'large': config.size_large
        }
        size = size_map[args.size]

        # Select model
        model_name = args.model or 'flux-pro'
        if model_name.startswith('flux'):
            variant = model_name.split('-')[1]  # Extract 'pro', 'dev', 'schnell'
            model = FluxModel(config, variant=variant)
        else:  # imagen
            model = GeminiModel(config, use_imagen=True)

        # Initialize cost tracker
        log_file = Path(config.cost_log_file) if config.log_costs else None
        cost_tracker = CostTracker(log_file)

        # Determine output path
        output_path = Path(args.output) if args.output else Path(config.output_directory) / 'hero_image.png'
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate
        print(f'Generating image with {model.name}...')
        result_path = model.generate(
            prompt=args.prompt,
            size=size,
            output_path=output_path
        )

        # Track cost
        gen_cost = model.get_cost_per_image()
        cost_tracker.track(
            model=model.name,
            cost=gen_cost,
            status='success',
            image_path=str(result_path),
            size=size
        )

        print(f'✓ Image saved to: {result_path}')
        print(f'💰 Cost: ${gen_cost:.3f}')

        # Optional quality validation
        if args.validate and config.enable_quality_check:
            from .ai import QualityValidator
            validator = QualityValidator(config)

            print('Validating image quality...')
            result = validator.validate(result_path, args.prompt)

            cost_tracker.track(
                model='validation',
                cost=result.cost,
                status='validated',
                image_path=str(result_path),
                size=size
            )

            if result.passed:
                print(f'✓ Quality check passed (score: {result.score:.2f})')
            else:
                print(f'⚠ Quality check failed (score: {result.score:.2f})')
                print(f'  Issues: {result.feedback}')

        # Show cost summary
        print('\n' + cost_tracker.display_summary())

    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/test_cli.py -v
```

Expected: PASS (all tests including new ones)

### Step 5: Test CLI manually

```bash
# Test AI mode (will fail if APIs not configured, that's expected)
python -m hero_image_generator --ai --prompt "Test image" --model flux-pro --size medium --output test.png

# Test backward compatibility
python -m hero_image_generator --preview
```

### Step 6: Commit

```bash
git add hero_image_generator/cli.py tests/test_cli.py
git commit -m "feat: add AI mode CLI flags (#2)"
```

---

## Task 9: Write Integration Tests (Real API)

**Files:**
- Create: `tests/integration/__init__.py`
- Create: `tests/integration/test_flux_integration.py`
- Create: `tests/integration/test_gemini_integration.py`
- Create: `pytest.ini`

### Step 1: Create pytest configuration

Create `pytest.ini`:
```ini
[pytest]
markers =
    slow: marks tests as slow (requires --run-slow flag)
    requires_api_keys: marks tests that need real API keys
    integration: marks integration tests
```

### Step 2: Create integration test structure

Create `tests/integration/__init__.py`:
```python
"""Integration tests requiring real API credentials.

Run with: pytest tests/integration/ --run-slow
"""
```

### Step 3: Write Flux integration test

Create `tests/integration/test_flux_integration.py`:
```python
"""Integration tests for Flux API.

These tests make real API calls and are skipped by default.
Run with: pytest tests/integration/test_flux_integration.py --run-slow
"""
import pytest
from pathlib import Path
from hero_image_generator.ai import AIConfig, FluxModel, GenerationError


@pytest.fixture
def real_config():
    """Load real AIConfig from environment."""
    try:
        return AIConfig.load()
    except Exception as e:
        pytest.skip(f'Could not load AI config: {e}')


@pytest.mark.slow
@pytest.mark.requires_api_keys
@pytest.mark.integration
def test_flux_schnell_real_generation(real_config, tmp_path):
    """Test real Flux Schnell generation (cheapest/fastest for testing)."""
    model = FluxModel(real_config, variant='schnell')
    output_path = tmp_path / 'flux_test.png'

    result = model.generate(
        prompt='Simple geometric hero image with blue and purple gradients',
        size=(800, 450),  # Small size for speed
        output_path=output_path
    )

    assert result.exists()
    assert result.stat().st_size > 0
    print(f'Generated image: {result}')
    print(f'Cost: ${model.get_cost_per_image()}')


@pytest.mark.slow
@pytest.mark.requires_api_keys
@pytest.mark.integration
def test_flux_pro_real_generation(real_config, tmp_path):
    """Test real Flux Pro generation (expensive - only run when needed)."""
    pytest.skip('Expensive test - only run manually')

    model = FluxModel(real_config, variant='pro')
    output_path = tmp_path / 'flux_pro_test.png'

    result = model.generate(
        prompt='Professional hero image for AI consultancy, modern design',
        size=(1920, 1080),
        output_path=output_path
    )

    assert result.exists()
    print(f'Generated image: {result}')
    print(f'Cost: ${model.get_cost_per_image()}')
```

### Step 4: Write Gemini integration test

Create `tests/integration/test_gemini_integration.py`:
```python
"""Integration tests for Gemini/Imagen API.

These tests make real API calls and are skipped by default.
Run with: pytest tests/integration/test_gemini_integration.py --run-slow
"""
import pytest
from pathlib import Path
from hero_image_generator.ai import AIConfig, GeminiModel, QualityValidator


@pytest.fixture
def real_config():
    """Load real AIConfig from environment."""
    try:
        return AIConfig.load()
    except Exception as e:
        pytest.skip(f'Could not load AI config: {e}')


@pytest.mark.slow
@pytest.mark.requires_api_keys
@pytest.mark.integration
def test_imagen_real_generation(real_config, tmp_path):
    """Test real Imagen generation."""
    model = GeminiModel(real_config, use_imagen=True)
    output_path = tmp_path / 'imagen_test.png'

    result = model.generate(
        prompt='Professional hero image with abstract technology patterns',
        size=(1920, 1080),
        output_path=output_path
    )

    assert result.exists()
    assert result.stat().st_size > 0
    print(f'Generated image: {result}')
    print(f'Cost: ${model.get_cost_per_image()}')


@pytest.mark.slow
@pytest.mark.requires_api_keys
@pytest.mark.integration
def test_quality_validation_real(real_config, tmp_path):
    """Test real quality validation with Gemini Vision."""
    # First generate an image
    model = GeminiModel(real_config, use_imagen=True)
    image_path = tmp_path / 'test.png'

    prompt = 'Professional hero image with blue gradients'
    model.generate(prompt, (800, 450), image_path)

    # Validate it
    validator = QualityValidator(real_config)
    result = validator.validate(image_path, prompt)

    assert result.score >= 0.0
    assert result.score <= 1.0
    assert result.cost > 0
    print(f'Validation score: {result.score}')
    print(f'Feedback: {result.feedback}')
    print(f'Passed: {result.passed}')
```

### Step 5: Document how to run integration tests

Create `tests/integration/README.md`:
```markdown
# Integration Tests

These tests make real API calls to Replicate and Google Vertex AI.

## Prerequisites

1. Set up `.env` file with real credentials:
   - `REPLICATE_API_TOKEN`
   - `GCP_PROJECT_ID`
   - `GOOGLE_APPLICATION_CREDENTIALS`

2. Ensure you have API credits available

## Running Tests

```bash
# Run all integration tests (will incur API costs)
pytest tests/integration/ --run-slow -v

# Run only Flux tests
pytest tests/integration/test_flux_integration.py --run-slow -v

# Run only Gemini tests
pytest tests/integration/test_gemini_integration.py --run-slow -v
```

## Costs

Approximate costs per test run:
- Flux Schnell test: $0.01
- Flux Pro test: $0.055 (skipped by default)
- Imagen test: $0.02
- Quality validation test: $0.021 (generation + validation)

Total (with Flux Pro skipped): ~$0.04 per full test run
```

### Step 6: Run unit tests (skip integration)

```bash
pytest tests/ -v -m "not slow"
```

Expected: All unit tests pass, integration tests skipped

### Step 7: Commit

```bash
git add tests/integration/ pytest.ini
git commit -m "test: add integration tests for real API calls (#2)"
```

---

## Task 10: Create Setup Documentation

**Files:**
- Create: `docs/setup/replicate_setup.md`
- Create: `docs/setup/gcp_setup.md`
- Create: `docs/setup/testing_setup.md`

### Step 1: Create Replicate setup guide

Create `docs/setup/replicate_setup.md`:
```markdown
# Replicate API Setup Guide

This guide walks you through setting up Replicate API access for Flux image generation.

## 1. Create Replicate Account

1. Go to [replicate.com](https://replicate.com)
2. Click "Sign Up" in the top right
3. Sign up with GitHub, Google, or email
4. Verify your email if required

## 2. Get API Token

1. Log in to Replicate
2. Click your profile icon (top right)
3. Select "API tokens" from the dropdown
4. Click "Create token"
5. Give it a name (e.g., "hero-image-generator")
6. Copy the token (starts with `r8_...`)

**Important:** Save this token securely. You won't be able to see it again.

## 3. Add Token to .env

Open your `.env` file and add:

```bash
REPLICATE_API_TOKEN=r8_YourTokenHere
```

## 4. Test Connection

Run this Python script to verify your setup:

```python
import os
from dotenv import load_dotenv
import replicate

load_dotenv()

# Verify token is loaded
token = os.getenv('REPLICATE_API_TOKEN')
print(f'Token loaded: {token[:10]}...' if token else 'Token not found!')

# Test API call (very cheap - $0.01)
output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={"prompt": "test image", "width": 512, "height": 512}
)

print(f'Success! Generated image URL: {output[0]}')
```

## 5. Pricing Information

| Model | Cost per Image | Quality | Speed |
|-------|---------------|---------|-------|
| Flux Pro | $0.055 | Highest | ~6s |
| Flux Dev | $0.020 | Good | ~4s |
| Flux Schnell | $0.010 | Fast drafts | ~2s |

## 6. Troubleshooting

### Error: "Invalid API token"
- Check that you copied the full token (starts with `r8_`)
- Ensure there are no spaces in the `.env` file
- Try regenerating the token

### Error: "Insufficient credits"
- Go to replicate.com/account/billing
- Add payment method
- Purchase credits ($10 minimum)

### Rate Limits
- Standard tier: 50 concurrent requests, 600/minute
- If you hit limits, wait 60 seconds or upgrade tier

## Next Steps

- See [GCP Setup](gcp_setup.md) for Gemini/Imagen configuration
- See [Testing Setup](testing_setup.md) for running tests
```

### Step 2: Create GCP setup guide

Create `docs/setup/gcp_setup.md`:
```markdown
# Google Cloud Platform Setup Guide

This guide walks you through setting up Google Vertex AI for Gemini/Imagen image generation.

## 1. Create GCP Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "hero-image-generator")
4. Click "Create"
5. Wait for project creation (takes ~30 seconds)
6. Note your **Project ID** (not the project name - they may differ)

## 2. Enable Required APIs

1. In the GCP Console, go to "APIs & Services" → "Library"
2. Search for and enable:
   - **Vertex AI API**
   - **Cloud AI Platform API**

Click "Enable" for each.

## 3. Create Service Account

1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Enter details:
   - Name: `hero-image-generator`
   - ID: (auto-filled)
   - Description: "Service account for AI image generation"
4. Click "Create and Continue"
5. Grant role: **Vertex AI User**
6. Click "Continue" → "Done"

## 4. Create and Download Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Select "JSON" format
5. Click "Create"
6. A JSON file downloads automatically

**Important:** Store this file securely. Anyone with this file can access your GCP resources.

## 5. Configure .env File

Move the downloaded JSON file to a secure location (e.g., `~/.gcp/hero-image-generator-key.json`)

Add to your `.env`:

```bash
GCP_PROJECT_ID=your-project-id-here
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/key.json
```

**Security tip:** Add `*.json` to your `.gitignore` to prevent accidentally committing keys.

## 6. Test Connection

Run this Python script to verify your setup:

```python
import os
from dotenv import load_dotenv
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

load_dotenv()

# Initialize Vertex AI
project_id = os.getenv('GCP_PROJECT_ID')
location = os.getenv('GCP_LOCATION', 'us-central1')

aiplatform.init(project=project_id, location=location)

print(f'✓ Connected to GCP project: {project_id}')

# Test image generation (costs ~$0.02)
model = ImageGenerationModel.from_pretrained('imagegeneration@006')
response = model.generate_images(
    prompt='simple test image',
    number_of_images=1
)

print(f'✓ Successfully generated test image')
print(f'  Model: Imagen')
print(f'  Cost: ~$0.02')
```

## 7. Pricing Information

| Service | Cost | Notes |
|---------|------|-------|
| Imagen (imagegeneration@006) | $0.020/image | Stable, production-ready |
| Gemini Vision (validation) | $0.001-0.002/call | For quality checks |

## 8. Set Up Billing

1. Go to "Billing" in GCP Console
2. Link a billing account (or create new one)
3. Add payment method
4. Enable billing for your project

**Free tier:** GCP offers $300 free credits for new accounts.

## 9. Set Budget Alerts (Recommended)

1. Go to "Billing" → "Budgets & alerts"
2. Click "Create budget"
3. Set budget amount (e.g., $50/month)
4. Set alert thresholds (50%, 90%, 100%)
5. Add your email for notifications

## 10. Troubleshooting

### Error: "Project not found"
- Double-check your `GCP_PROJECT_ID` in `.env`
- Use the Project ID, not the Project Name
- Verify project exists in console.cloud.google.com

### Error: "Permission denied"
- Ensure service account has "Vertex AI User" role
- Check that `GOOGLE_APPLICATION_CREDENTIALS` points to valid JSON file
- Verify APIs are enabled (step 2)

### Error: "Billing not enabled"
- Go to console.cloud.google.com/billing
- Link a billing account to your project

### Rate Limits
- Imagen: 60 requests/minute
- If you hit limits, implement delays or request quota increase

## Next Steps

- See [Replicate Setup](replicate_setup.md) for Flux configuration
- See [Testing Setup](testing_setup.md) for running tests
```

### Step 3: Create testing setup guide

Create `docs/setup/testing_setup.md`:
```markdown
# Testing Setup Guide

Guide for running tests in the hero-image-generator project.

## Test Structure

```
tests/
├── ai/                        # Unit tests for AI module (mocked)
│   ├── test_config.py
│   ├── test_flux.py
│   ├── test_gemini.py
│   ├── test_cost_tracker.py
│   └── test_quality_validator.py
├── integration/               # Integration tests (real APIs)
│   ├── test_flux_integration.py
│   └── test_gemini_integration.py
├── wizard/                    # Wizard tests
│   ├── test_ai_wizard.py
│   └── ...
└── test_cli.py               # CLI tests
```

## Running Unit Tests

Unit tests use mocked APIs and run quickly without incurring costs.

```bash
# Run all unit tests
pytest tests/ -v

# Run specific module
pytest tests/ai/ -v

# Run with coverage report
pytest tests/ --cov=hero_image_generator --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Running Integration Tests

Integration tests make real API calls and incur costs.

### Prerequisites

1. Complete [Replicate Setup](replicate_setup.md)
2. Complete [GCP Setup](gcp_setup.md)
3. Ensure `.env` has valid credentials

### Run Integration Tests

```bash
# Run all integration tests (~$0.04 cost)
pytest tests/integration/ --run-slow -v

# Run only Flux tests (~$0.01)
pytest tests/integration/test_flux_integration.py --run-slow -v

# Run only Gemini tests (~$0.02)
pytest tests/integration/test_gemini_integration.py --run-slow -v
```

### Cost Breakdown

| Test | API Calls | Cost |
|------|-----------|------|
| Flux Schnell | 1 generation | $0.01 |
| Flux Pro | 1 generation | $0.055 (skipped by default) |
| Imagen | 1 generation | $0.02 |
| Quality validation | 1 generation + 1 validation | $0.021 |

**Total per full run:** ~$0.04 (with expensive tests skipped)

## Test Markers

Tests use pytest markers for categorization:

```python
@pytest.mark.slow              # Slow tests (integration)
@pytest.mark.requires_api_keys # Needs real API keys
@pytest.mark.integration       # Integration test
```

### Run Only Unit Tests

```bash
pytest tests/ -v -m "not slow"
```

### Run Only Integration Tests

```bash
pytest tests/ -v -m "integration"
```

## Test Configuration

See `pytest.ini`:

```ini
[pytest]
markers =
    slow: marks tests as slow (requires --run-slow flag)
    requires_api_keys: marks tests that need real API keys
    integration: marks integration tests
```

## Continuous Integration

For CI/CD pipelines:

```yaml
# .github/workflows/test.yml example
- name: Run unit tests
  run: pytest tests/ -v -m "not slow"

# Only run integration tests manually or on release
- name: Run integration tests
  if: github.event_name == 'release'
  run: pytest tests/integration/ --run-slow -v
  env:
    REPLICATE_API_TOKEN: ${{ secrets.REPLICATE_API_TOKEN }}
    GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
```

## Troubleshooting

### Tests fail with "Configuration error"
- Check that `.env` exists in project root
- Verify all required env vars are set
- Run: `python -c "from hero_image_generator.ai import AIConfig; print(AIConfig.load())"`

### Integration tests skipped
- Add `--run-slow` flag
- Check that API credentials are valid

### Import errors
- Ensure package is installed: `pip install -e .`
- Or install with dev dependencies: `pip install -e ".[dev]"`

### Mocking errors in unit tests
- Unit tests should NEVER make real API calls
- Check that mocks are set up correctly
- Look for `@patch` decorators

## Writing New Tests

### Unit Test Template

```python
from unittest.mock import Mock, patch
import pytest

@patch('module.external_api')
def test_feature(mock_api):
    # Setup mock
    mock_api.return_value = 'expected'

    # Run code
    result = function_under_test()

    # Assert
    assert result == 'expected'
    mock_api.assert_called_once()
```

### Integration Test Template

```python
import pytest

@pytest.mark.slow
@pytest.mark.requires_api_keys
@pytest.mark.integration
def test_real_api_call(real_config, tmp_path):
    # Real API call here
    result = make_real_call()

    # Verify
    assert result.exists()
```

## Next Steps

- See [Replicate Setup](replicate_setup.md) for API configuration
- See [GCP Setup](gcp_setup.md) for Vertex AI configuration
```

### Step 4: Commit

```bash
git add docs/setup/
git commit -m "docs: add setup guides for Replicate, GCP, and testing (#2)"
```

---

## Task 11: Update README and CLAUDE.md

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`

### Step 1: Update README with AI features

Modify `README.md` - add AI section after Quick Start:

```markdown
## AI-Generated Images (v1.2.0+)

Generate photorealistic hero images using state-of-the-art AI models:

### Quick Start

1. **Set up API credentials:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials (see Setup Guides below)
   ```

2. **Install with AI dependencies:**
   ```bash
   pip install -e ".[ai]"
   ```

3. **Run interactive wizard:**
   ```bash
   python -m hero_image_generator
   # Select option 2: "AI-generated"
   ```

4. **Or use CLI directly:**
   ```bash
   python -m hero_image_generator \
     --ai \
     --prompt "Professional hero image for AI consultancy, modern and clean" \
     --model flux-pro \
     --size medium \
     --output my_hero.png
   ```

### Supported AI Models

| Model | Cost/Image | Quality | Speed | Provider |
|-------|-----------|---------|-------|----------|
| Flux Pro | $0.055 | Highest | ~6s | Replicate |
| Flux Dev | $0.020 | Good | ~4s | Replicate |
| Flux Schnell | $0.010 | Fast | ~2s | Replicate |
| Imagen | $0.020 | High | ~5s | Google Vertex AI |

### Features

- ✅ **Multiple AI models** - Flux Pro/Dev/Schnell, Gemini/Imagen
- ✅ **Quality validation** - Automatic image-prompt matching with Gemini Vision
- ✅ **Cost tracking** - Real-time cost display and session summaries
- ✅ **Model fallback** - Automatic retry with alternative model on failure
- ✅ **Interactive wizard** - Guided experience with live preview
- ✅ **Flexible sizing** - Small (800x450), Medium (1920x1080), Large (2560x1440)

### Setup Guides

- [Replicate API Setup](docs/setup/replicate_setup.md)
- [Google Cloud Platform Setup](docs/setup/gcp_setup.md)
- [Testing Guide](docs/setup/testing_setup.md)

### Example Usage

**Interactive Wizard:**
```bash
$ python -m hero_image_generator

How would you like to generate your hero image?
1. Programmatic themes (AI/ML, SEO, Automation, Strategy)
2. AI-generated (Flux/Gemini photorealistic images)

Select mode [1-2]: 2

📝 Describe your hero image
Prompt: Professional hero image for fintech startup, modern minimalist design

🤖 Select AI Model
1. Flux Pro ($0.055/image) - Highest quality
...

✓ Image generated: /tmp/preview.png
💰 Cost: $0.055
```

**CLI Mode:**
```bash
# Generate with Flux Pro
python -m hero_image_generator \
  --ai \
  --prompt "Vibrant hero image for e-commerce platform" \
  --model flux-pro \
  --size large

# Generate with Imagen (Google)
python -m hero_image_generator \
  --ai \
  --prompt "Elegant hero image for luxury brand" \
  --model imagen \
  --size medium
```

### Cost Management

```bash
# View generation costs
cat generation_costs.log

# Sample output:
# [2024-12-30 10:30:45] hero_001.png | Model: flux-pro | Size: 1920x1080 | Cost: $0.056 | Status: success
# [2024-12-30 10:31:10] hero_002.png | Model: imagen | Size: 1920x1080 | Cost: $0.021 | Status: success
```

---

## Original Programmatic Features (v1.0+)

(Keep existing README content here)
```

### Step 2: Update CLAUDE.md with AI architecture

Modify `CLAUDE.md` - add AI section after Development Commands:

```markdown
## AI Integration Architecture (v1.2.0+)

### Overview

The AI module (`hero_image_generator/ai/`) provides photorealistic hero image generation using:
- **Flux models** (Replicate): flux-pro, flux-dev, flux-schnell
- **Gemini/Imagen** (Google Vertex AI): imagegeneration@006
- **Quality validation** (Gemini Vision): gemini-1.5-flash
- **Cost tracking** and session management

### Module Structure

```
hero_image_generator/
├── ai/
│   ├── __init__.py           # Module exports
│   ├── base.py               # BaseAIModel abstract class
│   ├── config.py             # AIConfig (.env loader)
│   ├── flux.py               # FluxModel implementation
│   ├── gemini.py             # GeminiModel implementation
│   ├── cost_tracker.py       # CostTracker utility
│   └── quality_validator.py  # QualityValidator (Gemini Vision)
├── wizard/
│   ├── __init__.py           # WizardRunner (mode selection added)
│   └── ai_wizard.py          # AIWizardRunner (AI-specific flow)
└── cli.py                    # CLI with --ai flags
```

### Wizard Flow (Option A: Separate Modes)

```
User runs: python -m hero_image_generator

1. Mode selection:
   [1] Programmatic themes → Existing wizard (unchanged)
   [2] AI-generated → AIWizardRunner

If AI mode selected:
  2. Prompt collection
  3. Model selection (Flux Pro/Dev/Schnell/Imagen)
  4. Size selection (Small/Medium/Large)
  5. Cost estimate display
  6. Generation + preview
  7. Quality validation (optional)
  8. Refinement loop:
     - Regenerate with same settings
     - Modify prompt
     - Change model
     - Change size
     - Accept and save
  9. Final save + cost summary
```

### Base Abstraction (base.py:10-45)

All AI models inherit from `BaseAIModel`:

```python
class BaseAIModel(ABC):
    @abstractmethod
    def generate(prompt: str, size: Tuple[int, int], output_path: Path) -> Path

    @abstractmethod
    def get_cost_per_image() -> float

    @property
    @abstractmethod
    def name() -> str
```

### Flux Integration (flux.py)

**API:** Replicate SDK (`replicate>=0.25.0`)

**Models:**
- `black-forest-labs/flux-pro` ($0.055/image, highest quality)
- `black-forest-labs/flux-dev` ($0.020/image, good quality)
- `black-forest-labs/flux-schnell` ($0.010/image, fast iterations)

**Generation flow:**
1. Call `replicate.run()` with prompt, width, height
2. Download image from returned URL
3. Save to output_path

**Error handling:** All failures raise `GenerationError`

### Gemini/Imagen Integration (gemini.py)

**API:** Google Vertex AI (`google-cloud-aiplatform>=1.38.0`)

**Model:** `imagegeneration@006` (Imagen, stable production model)

**Note:** Gemini 2.0 Flash image generation is experimental and not used by default.

**Generation flow:**
1. Initialize Vertex AI with project_id and location
2. Load `ImageGenerationModel.from_pretrained('imagegeneration@006')`
3. Call `generate_images()` with prompt and aspect_ratio
4. Save PIL image to output_path

**Aspect ratio mapping:**
- Auto-calculates closest supported ratio (1:1, 3:4, 4:3, 9:16, 16:9)
- Example: 1920x1080 → 16:9

### Cost Tracking (cost_tracker.py)

**Purpose:** Track and log generation costs per model.

**Log format:**
```
[2024-12-30 10:30:45] hero_001.png | Model: flux-pro | Size: 1920x1080 | Cost: $0.056 (gen: $0.055, validation: $0.001) | Status: success
```

**Session tracking:**
- `track(model, cost, status, image_path, size, validation_cost=0)`
- `get_session_total()` → cumulative cost
- `get_breakdown()` → cost per model
- `display_summary()` → human-readable summary

### Quality Validation (quality_validator.py)

**Purpose:** Validate generated images match prompts using Gemini Vision.

**Model:** `gemini-1.5-flash` (multimodal)

**Validation criteria:**
1. Subject matter match (0-0.4)
2. Style/mood alignment (0-0.3)
3. Professional quality (0-0.3)

**Prompt template:**
```
Analyze this hero image against the following prompt: "{prompt}"
Score from 0.0 to 1.0 on these criteria...
Return JSON: {"score": 0.0-1.0, "breakdown": {...}, "issues": [...]}
```

**Threshold:** Configurable via `MIN_QUALITY_SCORE` (default: 0.6)

**Cost:** ~$0.001 per validation

**Failure mode:** On validation error, defaults to passing (0.6 score) to avoid blocking workflow.

### Configuration Management (config.py)

**Source:** `.env` file (loaded via `python-dotenv`)

**Required variables:**
```bash
REPLICATE_API_TOKEN=r8_...
GCP_PROJECT_ID=your-project-id
```

**Optional with defaults:**
```bash
GCP_LOCATION=us-central1
DEFAULT_MODEL=flux-pro
FALLBACK_MODEL=imagen
ENABLE_QUALITY_CHECK=true
MIN_QUALITY_SCORE=0.6
SIZE_SMALL=800x450
SIZE_MEDIUM=1920x1080
SIZE_LARGE=2560x1440
OUTPUT_DIRECTORY=public/images
MAX_RETRIES=2
```

**Loading:**
```python
from hero_image_generator.ai import AIConfig
config = AIConfig.load()  # Raises ConfigurationError if required vars missing
```

### CLI Integration (cli.py)

**New flags:**
```bash
--ai                    # Enable AI mode
--prompt TEXT           # Generation prompt (required with --ai)
--model CHOICE          # flux-pro, flux-dev, flux-schnell, imagen
--size CHOICE           # small, medium, large
--validate              # Enable quality validation (default: true)
```

**Example:**
```bash
python -m hero_image_generator \
  --ai \
  --prompt "Professional hero image for SaaS product" \
  --model flux-pro \
  --size medium \
  --output hero.png
```

**Backward compatibility:** All existing flags (`--preview`, `--title`, `--tags`, `--metadata`) work unchanged.

### Testing Strategy

**Unit tests** (mocked APIs):
- `tests/ai/test_config.py` - Config loading and validation
- `tests/ai/test_flux.py` - Flux model with mocked `replicate.run()`
- `tests/ai/test_gemini.py` - Gemini model with mocked Vertex AI
- `tests/ai/test_cost_tracker.py` - Cost tracking logic
- `tests/ai/test_quality_validator.py` - Validation with mocked Gemini

**Integration tests** (real APIs):
- `tests/integration/test_flux_integration.py` - Real Flux generation
- `tests/integration/test_gemini_integration.py` - Real Imagen generation

**Run tests:**
```bash
# Unit tests only (fast, no API costs)
pytest tests/ -v -m "not slow"

# Integration tests (slow, ~$0.04 cost)
pytest tests/integration/ --run-slow -v
```

### Extending AI Models

To add a new AI model (e.g., DALL-E, Midjourney):

1. Create `hero_image_generator/ai/dalle.py`:
   ```python
   from .base import BaseAIModel

   class DalleModel(BaseAIModel):
       def generate(self, prompt, size, output_path):
           # API call here
           pass

       def get_cost_per_image(self):
           return 0.040  # Example cost

       @property
       def name(self):
           return 'DALL-E 3'
   ```

2. Update `ai/__init__.py` exports

3. Add to `ai_wizard.py` model selection menu

4. Add to CLI `--model` choices

5. Add unit tests with mocked API

6. Add integration test (mark as `@pytest.mark.slow`)

### Security Considerations

- **Never commit `.env`** or service account JSON keys
- `.gitignore` includes: `.env`, `*.json`, `generation_costs.log`
- API keys loaded via environment variables only
- Service account should have minimal permissions (Vertex AI User role only)
- Cost tracking helps prevent runaway API spending

### Dependencies

**Production:**
```
Pillow>=10.0.0                    # Already in v1.0
replicate>=0.25.0                 # Flux API
google-cloud-aiplatform>=1.38.0   # Vertex AI
python-dotenv>=1.0.0              # .env loading
```

**Optional:** Install with `pip install hero-image-generator[ai]`

---

(Keep rest of existing CLAUDE.md content)
```

### Step 3: Commit

```bash
git add README.md CLAUDE.md
git commit -m "docs: update README and CLAUDE.md with AI integration (#2)"
```

---

## Task 12: Final Testing and Validation

**Goal:** Run full test suite and verify backward compatibility

### Step 1: Run all unit tests

```bash
pytest tests/ -v -m "not slow" --cov=hero_image_generator --cov-report=term
```

Expected: All tests pass, coverage >60%

### Step 2: Test backward compatibility

```bash
# Test programmatic mode still works
python -m hero_image_generator --preview

# Test wizard mode 1 (programmatic)
# Select option 1 when prompted
python -m hero_image_generator

# Test existing CLI flags
python -m hero_image_generator \
  --title "Test Title" \
  --tags ai,ml \
  --year 2024 \
  --output test_programmatic.png
```

Expected: All existing functionality works unchanged

### Step 3: Test AI mode (if credentials configured)

```bash
# Test AI wizard (will prompt for API setup if not configured)
python -m hero_image_generator
# Select option 2

# Test AI CLI mode
python -m hero_image_generator \
  --ai \
  --prompt "Test AI generation" \
  --model flux-schnell \
  --size small \
  --output test_ai.png
```

Expected: Either generates successfully or shows clear error about missing credentials

### Step 4: Verify package structure

```bash
python -c "
from hero_image_generator.ai import (
    AIConfig,
    FluxModel,
    GeminiModel,
    CostTracker,
    QualityValidator
)
print('✓ All AI imports successful')
"
```

Expected: No import errors

### Step 5: Check documentation completeness

```bash
ls -la docs/setup/
ls -la docs/plans/
```

Expected files:
- `docs/setup/replicate_setup.md`
- `docs/setup/gcp_setup.md`
- `docs/setup/testing_setup.md`
- `docs/plans/2025-12-30-ai-integration.md`

### Step 6: Commit final validation

```bash
git add .
git commit -m "test: validate AI integration and backward compatibility (#2)"
```

---

## Completion Checklist

Before marking this implementation complete, verify:

- [ ] All 72 existing tests still pass (backward compatibility)
- [ ] All new AI unit tests pass (mocked APIs)
- [ ] Package structure follows existing conventions
- [ ] No breaking changes to programmatic mode
- [ ] Wizard mode selection works (option 1 and 2)
- [ ] CLI `--ai` flag works
- [ ] Documentation is complete and accurate
- [ ] `.env.example` is comprehensive
- [ ] `.gitignore` prevents credential commits
- [ ] Integration tests exist (even if not run by default)
- [ ] Cost tracking works and logs correctly
- [ ] Quality validation works (when enabled)

---

## Next Steps (Phase 2 - Future)

Features deferred to Phase 2:
- Prompt enhancement with AI
- Multiple image variations/A/B testing
- EXIF metadata embedding
- JSON manifest tracking
- Automation hooks/webhooks
- Web UI interface
- Real-time generation API

---

## Rollback Plan

If issues arise during implementation:

1. **Restore previous version:**
   ```bash
   git log --oneline  # Find last good commit
   git revert <commit-hash>
   ```

2. **Disable AI mode:**
   - Remove mode selection from `wizard/__init__.py`
   - Keep AI module for future use

3. **Make AI dependencies optional:**
   - Already implemented via `pip install hero-image-generator[ai]`
   - Core package works without AI dependencies
