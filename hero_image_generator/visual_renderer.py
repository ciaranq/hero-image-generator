from PIL import Image, ImageDraw
from .theme_detector import Theme

class VisualRenderer:
    """Renders theme-specific visual elements on hero images"""

    def __init__(self):
        pass

    def render(self, img: Image.Image, theme: Theme) -> Image.Image:
        """
        Render visual elements based on theme.

        Args:
            img: Base image to draw on
            theme: Theme object with visual style info

        Returns:
            Image with visual elements drawn
        """
        # Route to theme-specific renderer
        if theme.name == 'ai_ml':
            return self._render_ai_ml(img, theme)
        elif theme.name == 'seo_analytics':
            return self._render_seo_analytics(img, theme)
        elif theme.name == 'automation':
            return self._render_automation(img, theme)
        elif theme.name == 'strategy':
            return self._render_strategy(img, theme)
        else:
            return self._render_default(img, theme)

    def _render_default(self, img: Image.Image, theme: Theme) -> Image.Image:
        """Render default/fallback visual elements"""
        # Simple geometric pattern for unknown themes
        draw = ImageDraw.Draw(img, 'RGBA')

        # Draw a few accent circles
        accent_color = theme.accent_color + (77,)  # 30% opacity

        draw.ellipse([900, 100, 1100, 300], fill=accent_color)
        draw.ellipse([100, 400, 300, 600], fill=accent_color)

        return img

    def _render_ai_ml(self, img: Image.Image, theme: Theme) -> Image.Image:
        """Render AI/ML theme: connected nodes network"""
        draw = ImageDraw.Draw(img, 'RGBA')

        # Colors with transparency
        accent_color = theme.accent_color + (128,)  # 50% opacity
        accent_light = theme.accent_color + (51,)   # 20% opacity
        white_alpha = (255, 255, 255, 179)          # 70% opacity
        line_color = (255, 255, 255, 77)            # 30% opacity

        # Central hub (right side, lower)
        center_x, center_y = 900, 400

        # Large glow circle
        draw.ellipse([center_x - 80, center_y - 80, center_x + 80, center_y + 80],
                     fill=accent_light)

        # Central node
        draw.ellipse([center_x - 50, center_y - 50, center_x + 50, center_y + 50],
                     fill=white_alpha)

        # Satellite nodes (6 nodes around center)
        import math
        satellites = [
            (center_x - 200, center_y - 150),  # Top-left
            (center_x, center_y - 200),        # Top
            (center_x + 200, center_y - 150),  # Top-right
            (center_x + 200, center_y + 100),  # Bottom-right
            (center_x, center_y + 200),        # Bottom
            (center_x - 200, center_y + 100),  # Bottom-left
        ]

        # Draw connection lines first (behind circles)
        for sat_x, sat_y in satellites:
            draw.line([(center_x, center_y), (sat_x, sat_y)],
                     fill=line_color, width=2)

        # Draw satellite nodes
        node_radius = 35
        for sat_x, sat_y in satellites:
            draw.ellipse([sat_x - node_radius, sat_y - node_radius,
                         sat_x + node_radius, sat_y + node_radius],
                        fill=white_alpha)

        return img

    def _render_seo_analytics(self, img: Image.Image, theme: Theme) -> Image.Image:
        """Render SEO/Analytics theme: charts and graphs"""
        draw = ImageDraw.Draw(img, 'RGBA')

        # Colors
        accent_color = theme.accent_color + (179,)  # 70% opacity
        white_alpha = (255, 255, 255, 128)          # 50% opacity
        line_color = theme.accent_color + (204,)    # 80% opacity

        # Bar chart on right side
        bar_base_x = 850
        bar_base_y = 500
        bar_width = 40
        bar_spacing = 20

        # 5 bars with varying heights
        bar_heights = [120, 180, 140, 220, 260]

        for i, height in enumerate(bar_heights):
            x = bar_base_x + i * (bar_width + bar_spacing)
            y = bar_base_y - height

            # Draw bar
            draw.rectangle([x, y, x + bar_width, bar_base_y],
                          fill=accent_color)

            # Draw top highlight
            draw.rectangle([x, y, x + bar_width, y + 5],
                          fill=white_alpha)

        # Trend line (rising from bottom-left to top-right)
        trend_points = [
            (bar_base_x - 50, bar_base_y - 80),
            (bar_base_x + 80, bar_base_y - 140),
            (bar_base_x + 180, bar_base_y - 180),
            (bar_base_x + 280, bar_base_y - 240),
        ]

        # Draw line segments
        for i in range(len(trend_points) - 1):
            draw.line([trend_points[i], trend_points[i + 1]],
                     fill=line_color, width=4)

        # Draw data point circles
        for point in trend_points:
            draw.ellipse([point[0] - 8, point[1] - 8,
                         point[0] + 8, point[1] + 8],
                        fill=white_alpha)

        return img

    def _render_automation(self, img: Image.Image, theme: Theme) -> Image.Image:
        """Render Automation theme: gears and circuits"""
        draw = ImageDraw.Draw(img, 'RGBA')

        # Colors
        accent_color = theme.accent_color + (128,)  # 50% opacity
        white_alpha = (255, 255, 255, 179)          # 70% opacity
        line_color = theme.accent_color + (179,)    # 70% opacity

        # Draw 3 interlocking circular nodes (simplified gears)
        nodes = [
            (850, 250, 80),   # Top-right: (x, y, radius)
            (950, 400, 70),   # Bottom-right
            (750, 400, 70),   # Bottom-left
        ]

        # Draw connection lines between nodes
        draw.line([(nodes[0][0], nodes[0][1]), (nodes[1][0], nodes[1][1])],
                 fill=line_color, width=3)
        draw.line([(nodes[0][0], nodes[0][1]), (nodes[2][0], nodes[2][1])],
                 fill=line_color, width=3)
        draw.line([(nodes[1][0], nodes[1][1]), (nodes[2][0], nodes[2][1])],
                 fill=line_color, width=3)

        # Draw gear circles
        for x, y, radius in nodes:
            # Outer glow
            draw.ellipse([x - radius - 10, y - radius - 10,
                         x + radius + 10, y + radius + 10],
                        fill=accent_color)

            # Main circle
            draw.ellipse([x - radius, y - radius,
                         x + radius, y + radius],
                        fill=white_alpha, outline=line_color, width=3)

            # Center dot
            draw.ellipse([x - 15, y - 15, x + 15, y + 15],
                        fill=line_color)

        # Add circuit-style connection arrows
        # Arrow from top to bottom-right
        arrow_tip = (950, 350)
        draw.polygon([
            (arrow_tip[0], arrow_tip[1]),
            (arrow_tip[0] - 10, arrow_tip[1] - 15),
            (arrow_tip[0] + 10, arrow_tip[1] - 15),
        ], fill=line_color)

        return img

    def _render_strategy(self, img: Image.Image, theme: Theme) -> Image.Image:
        """Render Strategy theme: hierarchical diagrams"""
        draw = ImageDraw.Draw(img, 'RGBA')

        # Colors
        accent_color = theme.accent_color + (128,)  # 50% opacity
        white_alpha = (255, 255, 255, 179)          # 70% opacity
        line_color = theme.accent_color + (204,)    # 80% opacity

        # Pyramid structure (3 levels)
        # Level 1: Top node (strategy)
        top_x, top_y = 900, 180
        top_w, top_h = 140, 60

        draw.rectangle([top_x - top_w//2, top_y - top_h//2,
                       top_x + top_w//2, top_y + top_h//2],
                      fill=white_alpha, outline=line_color, width=2)

        # Level 2: Two nodes (tactics)
        level2_y = 320
        level2_nodes = [(800, level2_y), (1000, level2_y)]
        node2_w, node2_h = 120, 50

        for node_x, node_y in level2_nodes:
            draw.rectangle([node_x - node2_w//2, node_y - node2_h//2,
                           node_x + node2_w//2, node_y + node2_h//2],
                          fill=white_alpha, outline=line_color, width=2)

            # Connection line from top
            draw.line([(top_x, top_y + top_h//2), (node_x, node_y - node2_h//2)],
                     fill=line_color, width=3)

        # Level 3: Three nodes (execution)
        level3_y = 480
        level3_nodes = [(750, level3_y), (900, level3_y), (1050, level3_y)]
        node3_w, node3_h = 100, 45

        for i, (node_x, node_y) in enumerate(level3_nodes):
            draw.rectangle([node_x - node3_w//2, node_y - node3_h//2,
                           node_x + node3_w//2, node_y + node3_h//2],
                          fill=accent_color, outline=line_color, width=2)

            # Connection lines from level 2
            parent_idx = 0 if i == 0 else 1
            parent_x, parent_y = level2_nodes[parent_idx]
            draw.line([(parent_x, parent_y + node2_h//2),
                      (node_x, node_y - node3_h//2)],
                     fill=line_color, width=2)

        return img
