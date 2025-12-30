"""Cost tracking utility for AI image generation."""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple


class CostTracker:
    """Tracks and logs costs for AI image generation."""

    def __init__(self, log_file: Optional[Path]):
        """
        Initialize cost tracker.

        Args:
            log_file: Path to log file, or None to disable logging
        """
        self.log_file = log_file
        self.session_costs: Dict[str, float] = defaultdict(float)
        self._log_initialized = False

    def track(
        self,
        model: str,
        cost: float,
        status: str,
        image_path: Path,
        size: Tuple[int, int],
        validation_cost: float = 0
    ) -> None:
        """
        Track a single generation cost.

        Args:
            model: Model name (e.g., "dall-e-3")
            cost: Generation cost in dollars
            status: Generation status (e.g., "success", "failed")
            image_path: Path to generated image
            size: Image dimensions (width, height)
            validation_cost: Optional validation cost in dollars
        """
        total_cost = cost + validation_cost
        self.session_costs[model] += total_cost

        if self.log_file is not None:
            self._write_log_entry(model, cost, status, image_path, size, validation_cost)

    def _write_log_entry(
        self,
        model: str,
        cost: float,
        status: str,
        image_path: Path,
        size: Tuple[int, int],
        validation_cost: float
    ) -> None:
        """Write entry to log file."""
        if not self._log_initialized:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'w') as f:
                f.write("# Cost Tracking Log\n")
            self._log_initialized = True

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_cost = cost + validation_cost
        size_str = f"{size[0]}x{size[1]}"

        # Build cost string with breakdown if validation cost exists
        if validation_cost > 0:
            cost_str = f"${total_cost:.3f} (generation: ${cost:.3f}, validation: ${validation_cost:.3f})"
        else:
            cost_str = f"${total_cost:.3f}"

        entry = (
            f"[{timestamp}] {image_path.name} | "
            f"Model: {model} | "
            f"Size: {size_str} | "
            f"Cost: {cost_str} | "
            f"Status: {status}\n"
        )

        with open(self.log_file, 'a') as f:
            f.write(entry)

    def get_session_total(self) -> float:
        """
        Get total cost for current session.

        Returns:
            Total cost in dollars
        """
        return sum(self.session_costs.values())

    def get_breakdown(self) -> Dict[str, float]:
        """
        Get cost breakdown by model.

        Returns:
            Dictionary with per-model costs and total
        """
        breakdown = dict(self.session_costs)
        breakdown['total'] = self.get_session_total()
        return breakdown

    def display_summary(self) -> str:
        """
        Generate formatted cost summary.

        Returns:
            Multi-line summary string
        """
        lines = []
        for model, cost in sorted(self.session_costs.items()):
            lines.append(f"{model}: ${cost:.3f}")
        lines.append(f"Total: ${self.get_session_total():.3f}")
        return "\n".join(lines)
