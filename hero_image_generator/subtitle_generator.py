from typing import List

class SubtitleGenerator:
    """Generates contextual subtitles from blog post tags"""

    def __init__(self):
        # Tag -> subtitle template mapping
        self.subtitle_map = {
            'ai': 'AI Intelligence Guide',
            'ml': 'AI Intelligence Guide',
            'llm': 'AI Intelligence Guide',
            'agent': 'Agent Systems Explained',
            'orchestration': 'Agent Systems Explained',
            'seo': 'SEO Best Practices',
            'optimization': 'SEO Best Practices',
            'content': 'Content Strategy Guide',
            'writing': 'Content Strategy Guide',
            'analytics': 'Data-Driven Insights',
            'metrics': 'Data-Driven Insights',
            'automation': 'Automation Handbook',
            'integration': 'Automation Handbook',
            'strategy': 'Strategic Framework',
            'consulting': 'Strategic Framework',
            'enterprise': 'Enterprise Solutions',
            'platform': 'Enterprise Solutions',
            'technical': 'Technical Deep Dive',
            'development': 'Technical Deep Dive',
            'customer-service': 'Customer Experience Guide',
        }

        self.default_subtitle = 'Technical Guide'

    def generate(self, tags: List[str], year: int) -> str:
        """
        Generate subtitle from primary tag and year.

        Args:
            tags: List of blog post tags (uses first matching)
            year: Publication year (appends if 2024+)

        Returns:
            Generated subtitle string
        """
        tags_lower = [tag.lower() for tag in tags]

        # Find first matching tag
        subtitle = self.default_subtitle
        for tag in tags_lower:
            if tag in self.subtitle_map:
                subtitle = self.subtitle_map[tag]
                break

        # Append year if recent
        if year >= 2024:
            subtitle = f"{subtitle} {year}"

        return subtitle
