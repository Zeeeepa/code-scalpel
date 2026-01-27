"""Build time profiling and optimization analysis."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class BuildStage:
    """Represents a build stage with timing information."""

    name: str
    duration: float
    timestamp: datetime
    status: str = "completed"


class BuildProfiler:
    """Profile build stages and identify bottlenecks."""

    def __init__(self):
        """Initialize build profiler."""
        self.stages: list[BuildStage] = []
        self.build_history: list[dict] = []

    def record_stage(self, name: str, duration: float) -> BuildStage:
        """Record a build stage."""
        stage = BuildStage(name=name, duration=duration, timestamp=datetime.now())
        self.stages.append(stage)
        return stage

    def profile_build(self) -> dict:
        """Get profile of current build."""
        total_time = sum(s.duration for s in self.stages)
        return {
            "total_time": total_time,
            "stage_count": len(self.stages),
            "stages": [{"name": s.name, "duration": s.duration} for s in self.stages],
        }

    def get_bottlenecks(self, threshold: float = 0.1) -> list[BuildStage]:
        """Get stages taking more than threshold percentage of time."""
        if not self.stages:
            return []
        total_time = sum(s.duration for s in self.stages)
        if total_time == 0:
            return []
        return [s for s in self.stages if s.duration / total_time > threshold]

    def compare_builds(self, other_profiler: BuildProfiler) -> dict:
        """Compare two builds."""
        current_time = sum(s.duration for s in self.stages)
        other_time = sum(s.duration for s in other_profiler.stages)
        difference = current_time - other_time
        percentage = (difference / other_time * 100) if other_time > 0 else 0
        return {
            "current_time": current_time,
            "other_time": other_time,
            "difference": difference,
            "percentage_change": percentage,
        }

    def generate_report(self) -> str:
        """Generate a profiling report."""
        if not self.stages:
            return "No build stages recorded"
        profile = self.profile_build()
        bottlenecks = self.get_bottlenecks()
        lines = [
            "Build Profile Report",
            f"Total Time: {profile['total_time']:.2f}s",
            f"Stages: {profile['stage_count']}",
            "",
            "Stage Breakdown:",
        ]
        for stage in self.stages:
            percentage = stage.duration / profile["total_time"] * 100
            lines.append(f"  {stage.name}: {stage.duration:.2f}s ({percentage:.1f}%)")
        if bottlenecks:
            lines.append("")
            lines.append("Bottlenecks (>10%):")
            for stage in bottlenecks:
                percentage = stage.duration / profile["total_time"] * 100
                lines.append(f"  {stage.name}: {percentage:.1f}%")
        return "\n".join(lines)

    def clear_stages(self) -> None:
        """Clear recorded stages."""
        self.stages.clear()
