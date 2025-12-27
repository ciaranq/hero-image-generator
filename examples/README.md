# Examples

This directory contains example scripts demonstrating how to customize the hero image generator for different brands.

## IntelliAgent Brand Configuration

The `intelliagent_brand.py` file shows how to:
- Customize brand colors
- Add custom themes
- Override default settings
- Generate branded images

Run it:

```bash
python examples/intelliagent_brand.py
```

## Creating Your Own Brand Configuration

1. Copy `intelliagent_brand.py` to a new file (e.g., `my_brand.py`)
2. Update the colors in the `__init__` method:
   ```python
   self.bg_color_start = (R, G, B)  # Your start color
   self.bg_color_end = (R, G, B)    # Your end color
   self.text_color = (R, G, B)      # Your text color
   self.badge_color = (R, G, B)     # Your badge color
   ```
3. Add custom themes in `ThemeDetector` if needed
4. Run your custom generator

## Batch Generation Example

Create a metadata file for your content:

```json
[
  {
    "title": "Your Blog Post Title",
    "tags": ["ai", "ml"],
    "year": 2025,
    "filename": "blog-post-hero.png"
  }
]
```

Then use the CLI:

```bash
python -m hero_image_generator --metadata your-content.json --output-dir ./output
```
