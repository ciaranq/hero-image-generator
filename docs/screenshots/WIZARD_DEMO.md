# Interactive Wizard Demo

## Launching the Wizard

```bash
$ python -m hero_image_generator
```

## Wizard Flow

```
🎨 Hero Image Generator - Interactive Wizard

Enter image title: AI Agent Orchestration Platform
Enter tags (comma-separated): ai,ml,agents,platform
✓ Detected theme: AI/ML
Year [2025]: 2025

Customize colors/fonts? (y/n) [n]: y

Accent color:
[1] purple  [2] green  [3] orange  [4] cyan
[5] red     [6] blue   [7] custom
Choice [1]: 1

Customize gradient? (y/n) [n]: n

Customize font sizes? (y/n) [n]: n

⏳ Generating image...
✅ Generated: public/images/temp-preview.png
🖼️  Opening preview...

Satisfied with this image? (y/n): n

What would you like to change?
[1] Title
[2] Tags (will re-detect theme)
[3] Year badge
[4] Override theme
[5] Accent color
[6] Gradient colors
[7] Font sizes
[8] Start over
[0] Cancel (keep current image)

Choice: 1

Enter image title: AI Agent Platform

⏳ Generating image...
✅ Generated: public/images/temp-preview.png
🖼️  Opening preview...

Satisfied with this image? (y/n): y

Save as [ai-agent-platform-hero.png]:
Output directory [public/images]:

✅ Saved: public/images/ai-agent-platform-hero.png
💾 Preferences saved for next session

✅ Done!
```

## Features Demonstrated

- **Interactive prompts** for title, tags, and year
- **Automatic theme detection** from tags
- **Live preview** opens in system default viewer
- **Refinement loop** allows iterative changes
- **Preference persistence** saves settings for next session
- **Color customization** with presets and custom hex/RGB
- **Smart defaults** from last session

## Color Customization

The wizard supports multiple color input formats:

```
Enter custom color:
  Format: #8b5cf6 (hex) or 139,92,246 (RGB)
Color: #FF6B35        ✓ Hex with hash
Color: 22C55E          ✓ Hex without hash
Color: 59,130,246      ✓ RGB tuple
```

## Saved Preferences

Preferences are saved to `~/.config/hero-image-generator/last-used.json`:

```json
{
  "accent_color": [139, 92, 246],
  "gradient_start": [59, 130, 246],
  "gradient_end": [139, 92, 246],
  "title_font_size": 60,
  "subtitle_font_size": 32,
  "year_font_size": 36,
  "theme_override": null,
  "last_year": 2025
}
```

These settings are automatically loaded in the next wizard session!
