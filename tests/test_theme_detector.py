import sys
sys.path.insert(0, 'scripts')
from theme_detector import ThemeDetector, Theme

def test_detect_ai_ml_theme():
    detector = ThemeDetector()
    theme = detector.get_theme(['ai', 'ml', 'platform'])
    assert theme.name == 'ai_ml'
    assert theme.accent_color == (139, 92, 246)

def test_detect_seo_theme():
    detector = ThemeDetector()
    theme = detector.get_theme(['seo', 'optimization'])
    assert theme.name == 'seo_analytics'
    assert theme.accent_color == (34, 197, 94)

def test_detect_automation_theme():
    detector = ThemeDetector()
    theme = detector.get_theme(['automation', 'api'])
    assert theme.name == 'automation'
    assert theme.accent_color == (249, 115, 22)

def test_fallback_to_default_theme():
    detector = ThemeDetector()
    theme = detector.get_theme(['unknown-tag'])
    assert theme.name == 'default'
    assert theme.accent_color == (139, 92, 246)
