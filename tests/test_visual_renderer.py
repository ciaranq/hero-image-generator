from PIL import Image
from hero_image_generator.visual_renderer import VisualRenderer
from hero_image_generator.theme_detector import Theme

def test_render_returns_image():
    renderer = VisualRenderer()
    img = Image.new('RGB', (1200, 630))
    theme = Theme(name='default', accent_color=(139, 92, 246))

    result = renderer.render(img, theme)
    assert result.size == (1200, 630)
    assert result.mode == 'RGB'
