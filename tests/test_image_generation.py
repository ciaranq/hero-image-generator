import sys
sys.path.insert(0, 'scripts')

from image_generator import HeroImageGenerator

def test_single_image():
    """Test generating a single hero image"""
    generator = HeroImageGenerator()

    output = generator.generate(
        title="AI Agent Orchestration: Multi-Agent Workflows",
        icon="🤖",
        year=2025,
        output_filename="test-hero.png"
    )

    print(f"✅ Generated test image: {output}")
    print("⚠️  Check public/images/test-hero.png to verify it looks good")

if __name__ == '__main__':
    test_single_image()
