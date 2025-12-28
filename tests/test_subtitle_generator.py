from hero_image_generator.subtitle_generator import SubtitleGenerator

def test_generate_ai_subtitle():
    gen = SubtitleGenerator()
    subtitle = gen.generate(['ai', 'platform'], 2025)
    assert subtitle == 'AI Intelligence Guide 2025'

def test_generate_seo_subtitle():
    gen = SubtitleGenerator()
    subtitle = gen.generate(['seo', 'optimization'], 2024)
    assert subtitle == 'SEO Best Practices 2024'

def test_generate_subtitle_without_year():
    gen = SubtitleGenerator()
    subtitle = gen.generate(['automation'], 2022)
    assert subtitle == 'Automation Handbook'

def test_fallback_subtitle():
    gen = SubtitleGenerator()
    subtitle = gen.generate(['unknown-tag'], 2025)
    assert subtitle == 'Technical Guide 2025'
