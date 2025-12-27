from PIL import Image, ImageDraw, ImageFont
import os
from theme_detector import ThemeDetector, Theme
from subtitle_generator import SubtitleGenerator
from visual_renderer import VisualRenderer

class HeroImageGenerator:
    """Generate hero images for blog posts"""

    def __init__(self, width=1200, height=630):
        self.width = width
        self.height = height
        self.output_dir = 'public/images'

        # Color scheme: Modern blue/purple gradient
        self.bg_color_start = (59, 130, 246)  # Blue
        self.bg_color_end = (139, 92, 246)    # Purple
        self.text_color = (255, 255, 255)     # White
        self.badge_color = (34, 197, 94)      # Green

        # New components
        self.theme_detector = ThemeDetector()
        self.subtitle_generator = SubtitleGenerator()
        self.visual_renderer = VisualRenderer()

    def create_gradient_background(self, theme=None):
        """Create a gradient background with optional theme colors"""
        # Use theme colors or defaults
        if theme:
            start_color = theme.base_gradient_start
            end_color = theme.accent_color  # Blend to accent color
        else:
            start_color = self.bg_color_start
            end_color = self.bg_color_end

        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        # Create gradient from top to bottom
        for y in range(self.height):
            ratio = y / self.height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        return img

    def add_grid_pattern(self, img):
        """Add subtle grid pattern overlay to image"""
        draw = ImageDraw.Draw(img, 'RGBA')

        # Grid settings
        grid_color = (255, 255, 255, 26)  # White with 10% opacity
        grid_spacing = 100

        # Vertical lines
        for x in range(0, self.width, grid_spacing):
            draw.line([(x, 0), (x, self.height)], fill=grid_color, width=1)

        # Horizontal lines
        for y in range(0, self.height, grid_spacing):
            draw.line([(0, y), (self.width, y)], fill=grid_color, width=1)

        return img

    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def generate(self, title, tags, year, output_filename):
        """
        Generate a hero image with theme-specific visuals

        Args:
            title: Blog post title
            tags: List of blog post tags (for theme detection)
            year: Publication year (for badge and subtitle)
            output_filename: Output file path
        """
        # 1. Detect theme from tags
        theme = self.theme_detector.get_theme(tags)

        # 2. Create gradient background with theme colors
        img = self.create_gradient_background(theme)

        # 3. Add grid pattern overlay
        img = self.add_grid_pattern(img)

        # 4. Render theme-specific visual elements
        img = self.visual_renderer.render(img, theme)

        # 5. Generate subtitle from tags
        subtitle = self.subtitle_generator.generate(tags, year)

        # 6. Add text layers
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)

        # Load fonts
        try:
            # macOS fonts
            title_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 60)
            subtitle_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 32)
            year_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 36)
        except:
            try:
                # Linux fonts
                title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
                subtitle_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 32)
                year_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 36)
            except:
                # Fallback
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                year_font = ImageFont.load_default()

        # Draw year badge (top-right)
        year_text = str(year)
        year_bbox = year_font.getbbox(year_text)
        year_width = year_bbox[2] - year_bbox[0]
        year_height = year_bbox[3] - year_bbox[1]

        badge_padding = 20
        badge_x = self.width - year_width - badge_padding * 3
        badge_y = 60

        badge_rect = [
            badge_x - badge_padding,
            badge_y - badge_padding,
            badge_x + year_width + badge_padding,
            badge_y + year_height + badge_padding
        ]
        draw.rounded_rectangle(badge_rect, radius=10, fill=theme.accent_color)
        draw.text((badge_x, badge_y), year_text, font=year_font, fill=self.text_color)

        # Draw title (centered, left side to avoid visuals on right)
        max_title_width = 700  # Narrower to keep left side
        title_lines = self.wrap_text(title, title_font, max_title_width)

        # Calculate title block height
        line_spacing = 20
        title_height = len(title_lines) * (60 + line_spacing)

        # Position title in upper-left quadrant
        title_start_y = 200

        for i, line in enumerate(title_lines):
            bbox = title_font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            line_x = 100  # Left-aligned with margin
            line_y = title_start_y + i * (60 + line_spacing)

            # Text shadow
            shadow_offset = 3
            draw.text((line_x + shadow_offset, line_y + shadow_offset), line,
                     font=title_font, fill=(0, 0, 0))

            # Main text
            draw.text((line_x, line_y), line, font=title_font, fill=self.text_color)

        # Draw subtitle below title
        subtitle_y = title_start_y + title_height + 10
        subtitle_color = (255, 255, 255, 179)  # 70% opacity

        draw.text((100, subtitle_y), subtitle, font=subtitle_font,
                 fill=self.text_color)

        # 7. Save image
        import os
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, output_filename)
        img.save(output_path, 'PNG', optimize=True)

        return output_path
