from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Theme:
    """Represents a visual theme with colors and style"""
    name: str
    accent_color: Tuple[int, int, int]
    base_gradient_start: Tuple[int, int, int] = (30, 58, 138)
    base_gradient_end: Tuple[int, int, int] = (59, 130, 246)

class ThemeDetector:
    """Detects visual theme based on blog post tags"""

    def __init__(self):
        # Theme mappings: tag -> theme
        self.theme_map = {
            'ai_ml': {
                'tags': ['ai', 'ml', 'llm', 'platform', 'agent', 'orchestration'],
                'accent': (139, 92, 246),  # Purple
            },
            'seo_analytics': {
                'tags': ['seo', 'analytics', 'metrics', 'content', 'optimization'],
                'accent': (34, 197, 94),  # Green
            },
            'automation': {
                'tags': ['automation', 'api', 'integration', 'technical', 'development'],
                'accent': (249, 115, 22),  # Orange
            },
            'strategy': {
                'tags': ['strategy', 'business', 'enterprise', 'consulting'],
                'accent': (6, 182, 212),  # Cyan
            },
        }

        self.default_theme = Theme(
            name='default',
            accent_color=(139, 92, 246)  # Purple default
        )

    def get_theme(self, tags: List[str]) -> Theme:
        """
        Detect theme from tags. Returns first matching theme or default.

        Note: If tags match multiple themes, returns the first theme found
        in the internal theme_map iteration order.

        Args:
            tags: List of blog post tags

        Returns:
            Theme object with name and colors
        """
        tags_lower = [tag.lower() for tag in tags]

        for theme_name, theme_data in self.theme_map.items():
            for tag in tags_lower:
                if tag in theme_data['tags']:
                    return Theme(
                        name=theme_name,
                        accent_color=theme_data['accent']
                    )

        return self.default_theme
