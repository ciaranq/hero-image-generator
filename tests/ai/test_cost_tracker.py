"""Tests for CostTracker utility."""

from pathlib import Path
from datetime import datetime
import pytest
from hero_image_generator.ai.cost_tracker import CostTracker


def test_track_single_generation(tmp_path):
    """Track one generation and verify total and log file."""
    log_file = tmp_path / "costs.log"
    tracker = CostTracker(log_file)

    tracker.track(
        model="dall-e-3",
        cost=0.040,
        status="success",
        image_path=Path("test.png"),
        size=(1024, 1024)
    )

    assert tracker.get_session_total() == 0.040
    assert log_file.exists()

    content = log_file.read_text()
    assert "dall-e-3" in content
    assert "1024x1024" in content
    assert "$0.040" in content
    assert "success" in content


def test_track_multiple_generations(tmp_path):
    """Track 3 generations and verify cumulative total."""
    log_file = tmp_path / "costs.log"
    tracker = CostTracker(log_file)

    tracker.track("dall-e-3", 0.040, "success", Path("img1.png"), (1024, 1024))
    tracker.track("dall-e-3", 0.080, "success", Path("img2.png"), (1024, 1792))
    tracker.track("dall-e-2", 0.020, "success", Path("img3.png"), (1024, 1024))

    assert tracker.get_session_total() == pytest.approx(0.140)


def test_track_with_validation_cost(tmp_path):
    """Include validation cost in total."""
    log_file = tmp_path / "costs.log"
    tracker = CostTracker(log_file)

    tracker.track(
        model="dall-e-3",
        cost=0.040,
        status="success",
        image_path=Path("test.png"),
        size=(1024, 1024),
        validation_cost=0.002
    )

    assert tracker.get_session_total() == 0.042

    content = log_file.read_text()
    assert "$0.042" in content
    assert "generation: $0.040" in content
    assert "validation: $0.002" in content


def test_log_file_format(tmp_path):
    """Verify log entry format."""
    log_file = tmp_path / "costs.log"
    tracker = CostTracker(log_file)

    tracker.track(
        model="dall-e-3",
        cost=0.040,
        status="success",
        image_path=Path("hero.png"),
        size=(1024, 1024)
    )

    lines = log_file.read_text().strip().split('\n')
    assert len(lines) == 2  # Header + entry
    assert lines[0] == "# Cost Tracking Log"

    entry = lines[1]
    assert entry.startswith("[")
    assert "] hero.png" in entry
    assert "Model: dall-e-3" in entry
    assert "Size: 1024x1024" in entry
    assert "Cost: $0.040" in entry
    assert "Status: success" in entry


def test_session_cost_breakdown(tmp_path):
    """Get breakdown by model."""
    log_file = tmp_path / "costs.log"
    tracker = CostTracker(log_file)

    tracker.track("dall-e-3", 0.040, "success", Path("img1.png"), (1024, 1024))
    tracker.track("dall-e-3", 0.080, "success", Path("img2.png"), (1024, 1792))
    tracker.track("dall-e-2", 0.020, "success", Path("img3.png"), (1024, 1024))

    breakdown = tracker.get_breakdown()
    assert breakdown["dall-e-3"] == pytest.approx(0.120)
    assert breakdown["dall-e-2"] == pytest.approx(0.020)
    assert breakdown["total"] == pytest.approx(0.140)


def test_cost_tracker_no_logging(tmp_path):
    """Work without log file (None)."""
    tracker = CostTracker(None)

    tracker.track("dall-e-3", 0.040, "success", Path("test.png"), (1024, 1024))
    tracker.track("dall-e-2", 0.020, "success", Path("test2.png"), (512, 512))

    assert tracker.get_session_total() == 0.060
    breakdown = tracker.get_breakdown()
    assert breakdown["total"] == 0.060


def test_display_summary(tmp_path):
    """Display formatted summary."""
    log_file = tmp_path / "costs.log"
    tracker = CostTracker(log_file)

    tracker.track("dall-e-3", 0.040, "success", Path("img1.png"), (1024, 1024))
    tracker.track("dall-e-3", 0.080, "success", Path("img2.png"), (1024, 1792))
    tracker.track("dall-e-2", 0.020, "success", Path("img3.png"), (1024, 1024))

    summary = tracker.display_summary()
    assert "dall-e-3: $0.120" in summary
    assert "dall-e-2: $0.020" in summary
    assert "Total: $0.140" in summary
