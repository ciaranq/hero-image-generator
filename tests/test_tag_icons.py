from tag_icons import get_icon_for_tags

def test_icon_mapping():
    assert get_icon_for_tags(['AI']) == '🤖'
    assert get_icon_for_tags(['SEO']) == '🔍'
    assert get_icon_for_tags(['E-commerce']) == '🛍️'
    assert get_icon_for_tags(['Unknown Tag']) == '📄'
    assert get_icon_for_tags([]) == '📄'
    print("✅ All icon mapping tests passed")

if __name__ == '__main__':
    test_icon_mapping()
