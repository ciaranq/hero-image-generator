#!/usr/bin/env python3
"""
Hero Image Generator CLI

Generate professional hero images with theme-based visual systems.
"""

import json
import argparse
import sys
from pathlib import Path

from .image_generator import HeroImageGenerator


def generate_single_image(title, tags, year, output, output_dir=None):
    """
    Generate a single hero image

    Args:
        title: Image title text
        tags: List of tags for theme detection
        year: Year for badge (optional)
        output: Output filename
        output_dir: Output directory (optional)
    """
    generator = HeroImageGenerator()

    if output_dir:
        generator.output_dir = output_dir

    try:
        output_path = generator.generate(title, tags, year, output)
        print(f"✅ Generated: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Failed to generate {output}: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_from_metadata(metadata_path, filter_year=None, dry_run=False, output_dir=None):
    """
    Generate hero images from metadata JSON file

    Args:
        metadata_path: Path to JSON file with image metadata
        filter_year: Only generate for specific year (optional)
        dry_run: If True, only print what would be generated
        output_dir: Output directory (optional)
    """
    # Load metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    generator = HeroImageGenerator()
    if output_dir:
        generator.output_dir = output_dir

    # Filter by year if specified
    items_to_process = metadata
    if filter_year:
        items_to_process = [item for item in metadata if item.get('year') == filter_year]

    print(f"Processing {len(items_to_process)} items from {metadata_path}...")

    generated = 0
    skipped = 0

    for item in items_to_process:
        title = item['title']
        tags = item['tags']
        year = item.get('year', 2025)
        filename = item.get('filename', f"{item.get('slug', 'image')}-hero.png")

        if dry_run:
            print(f"  Would generate: {filename}")
            print(f"    Title: {title}")
            print(f"    Tags: {', '.join(tags)}")
            print(f"    Year: {year}")
        else:
            try:
                output_path = generator.generate(title, tags, year, filename)
                print(f"✅ Generated: {filename}")
                generated += 1
            except Exception as e:
                print(f"❌ Failed to generate {filename}: {e}")
                import traceback
                traceback.print_exc()
                skipped += 1

    print(f"\n{'Dry run' if dry_run else 'Generation'} complete:")
    print(f"  {'Would generate' if dry_run else 'Generated'}: {generated if not dry_run else len(items_to_process)}")
    if not dry_run and skipped > 0:
        print(f"  Skipped: {skipped}")


def generate_preview_samples(output_dir=None):
    """Generate one sample image for each theme to preview styles"""
    generator = HeroImageGenerator()

    if output_dir:
        generator.output_dir = output_dir

    # Sample images for each theme
    samples = [
        {
            'title': 'AI Agent Orchestration Platform',
            'tags': ['ai', 'agent', 'platform'],
            'year': 2025,
            'filename': 'preview-ai-ml.png'
        },
        {
            'title': 'SEO Optimization Best Practices',
            'tags': ['seo', 'optimization'],
            'year': 2025,
            'filename': 'preview-seo.png'
        },
        {
            'title': 'API Automation Framework',
            'tags': ['automation', 'api'],
            'year': 2025,
            'filename': 'preview-automation.png'
        },
        {
            'title': 'Enterprise Strategy Guide',
            'tags': ['strategy', 'enterprise'],
            'year': 2025,
            'filename': 'preview-strategy.png'
        },
        {
            'title': 'Technical Deep Dive',
            'tags': ['unknown-tag'],
            'year': 2025,
            'filename': 'preview-default.png'
        },
    ]

    print("Generating preview samples for each theme...\n")

    for sample in samples:
        try:
            output_path = generator.generate(
                sample['title'],
                sample['tags'],
                sample['year'],
                sample['filename']
            )
            print(f"✅ Generated: {sample['filename']} (tags: {', '.join(sample['tags'])})")
        except Exception as e:
            print(f"❌ Failed: {sample['filename']}: {e}")

    print(f"\nPreview images saved to: {generator.output_dir}/")


def main():
    parser = argparse.ArgumentParser(
        description='Generate professional hero images with theme-based visual systems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single image
  %(prog)s --title "My Blog Post" --tags ai,ml --year 2025 --output my-hero.png

  # Generate preview samples
  %(prog)s --preview

  # Generate from metadata file
  %(prog)s --metadata posts.json

  # Generate with custom output directory
  %(prog)s --preview --output-dir ./images
        """
    )

    # Single image generation
    parser.add_argument('--title', help='Image title text')
    parser.add_argument('--tags', help='Comma-separated tags for theme detection (e.g., ai,ml,platform)')
    parser.add_argument('--year', type=int, default=2025, help='Year for badge (default: 2025)')
    parser.add_argument('--output', help='Output filename (e.g., my-hero.png)')

    # Batch generation
    parser.add_argument('--metadata', help='Generate from JSON metadata file')
    parser.add_argument('--filter-year', type=int, help='Only generate images for specific year')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without creating files')

    # Preview mode
    parser.add_argument('--preview', action='store_true', help='Generate preview samples for each theme')

    # Output options
    parser.add_argument('--output-dir', help='Output directory (default: public/images)')

    args = parser.parse_args()

    # Interactive wizard mode (no arguments)
    if len(sys.argv) == 1:
        from .wizard import WizardRunner
        wizard = WizardRunner()
        wizard.run()
        return

    # Preview mode
    if args.preview:
        generate_preview_samples(output_dir=args.output_dir)

    # Single image generation
    elif args.title and args.tags and args.output:
        tags = [tag.strip() for tag in args.tags.split(',')]
        generate_single_image(
            args.title,
            tags,
            args.year,
            args.output,
            output_dir=args.output_dir
        )

    # Batch generation from metadata
    elif args.metadata:
        generate_from_metadata(
            args.metadata,
            filter_year=args.filter_year,
            dry_run=args.dry_run,
            output_dir=args.output_dir
        )

    # Show help if no valid mode specified
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
