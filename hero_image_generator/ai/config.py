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
        try:
            min_quality = float(os.getenv('MIN_QUALITY_SCORE', '0.6'))
        except ValueError:
            raise ConfigurationError(
                f"MIN_QUALITY_SCORE must be a number, got: {os.getenv('MIN_QUALITY_SCORE')}"
            )

        # Parse sizes
        size_small = cls._parse_size(os.getenv('SIZE_SMALL', '800x450'))
        size_medium = cls._parse_size(os.getenv('SIZE_MEDIUM', '1920x1080'))
        size_large = cls._parse_size(os.getenv('SIZE_LARGE', '2560x1440'))

        output_dir = os.getenv('OUTPUT_DIRECTORY', 'public/images')
        failed_dir = os.getenv('FAILED_OUTPUT_DIRECTORY', 'public/images/failed')
        save_failed = os.getenv('SAVE_FAILED_GENERATIONS', 'true').lower() == 'true'

        log_costs = os.getenv('LOG_COSTS', 'true').lower() == 'true'
        cost_log = os.getenv('COST_LOG_FILE', 'generation_costs.log')

        try:
            max_retries = int(os.getenv('MAX_RETRIES', '2'))
        except ValueError:
            raise ConfigurationError(
                f"MAX_RETRIES must be an integer, got: {os.getenv('MAX_RETRIES')}"
            )

        try:
            retry_delay = int(os.getenv('RETRY_DELAY_SECONDS', '5'))
        except ValueError:
            raise ConfigurationError(
                f"RETRY_DELAY_SECONDS must be an integer, got: {os.getenv('RETRY_DELAY_SECONDS')}"
            )

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
