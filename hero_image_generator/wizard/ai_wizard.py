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
