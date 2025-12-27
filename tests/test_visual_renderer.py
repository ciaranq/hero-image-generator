import sys
sys.path.insert(0, 'scripts')
from PIL import Image
from visual_renderer import VisualRenderer
from theme_detector import Theme

def test_render_returns_image():
    renderer = VisualRenderer()
    img = Image.new('RGB', (1200, 630))
    theme = Theme(name='default', accent_color=(139, 92, 246))

    result = renderer.render(img, theme)
    assert result.size == (1200, 630)
    assert result.mode == 'RGB'
