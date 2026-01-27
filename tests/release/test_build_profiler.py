"""Tests for build profiling system."""

from datetime import datetime


from code_scalpel.release.build_profiler import BuildProfiler, BuildStage


class TestBuildStage:
    """Test BuildStage class."""

    def test_create_stage(self):
        """Test creating a build stage."""
        stage = BuildStage(name="compile", duration=30.5, timestamp=datetime.now())
        assert stage.name == "compile"
        assert stage.duration == 30.5


class TestBuildProfiler:
    """Test BuildProfiler class."""

    def test_record_stage(self):
        """Test recording a stage."""
        profiler = BuildProfiler()
        stage = profiler.record_stage("compile", 30)
        assert len(profiler.stages) == 1
        assert stage.name == "compile"

    def test_record_multiple_stages(self):
        """Test recording multiple stages."""
        profiler = BuildProfiler()
        profiler.record_stage("compile", 30)
        profiler.record_stage("test", 60)
        profiler.record_stage("package", 10)
        assert len(profiler.stages) == 3

    def test_profile_build(self):
        """Test getting build profile."""
        profiler = BuildProfiler()
        profiler.record_stage("stage1", 30)
        profiler.record_stage("stage2", 20)
        profile = profiler.profile_build()
        assert profile["total_time"] == 50
        assert profile["stage_count"] == 2

    def test_get_bottlenecks(self):
        """Test identifying bottlenecks."""
        profiler = BuildProfiler()
        profiler.record_stage("compile", 80)
        profiler.record_stage("test", 15)
        profiler.record_stage("package", 5)
        bottlenecks = profiler.get_bottlenecks(threshold=0.1)
        assert len(bottlenecks) >= 1
        assert bottlenecks[0].name == "compile"

    def test_get_bottlenecks_empty(self):
        """Test bottlenecks with no stages."""
        profiler = BuildProfiler()
        bottlenecks = profiler.get_bottlenecks()
        assert len(bottlenecks) == 0

    def test_compare_builds(self):
        """Test comparing two builds."""
        profiler1 = BuildProfiler()
        profiler1.record_stage("compile", 30)
        profiler1.record_stage("test", 20)

        profiler2 = BuildProfiler()
        profiler2.record_stage("compile", 25)
        profiler2.record_stage("test", 25)

        comparison = profiler1.compare_builds(profiler2)
        assert comparison["current_time"] == 50
        assert comparison["other_time"] == 50

    def test_generate_report(self):
        """Test generating profiling report."""
        profiler = BuildProfiler()
        profiler.record_stage("compile", 30)
        profiler.record_stage("test", 20)
        report = profiler.generate_report()
        assert "Build Profile Report" in report
        assert "compile" in report
        assert "test" in report

    def test_clear_stages(self):
        """Test clearing stages."""
        profiler = BuildProfiler()
        profiler.record_stage("stage1", 10)
        assert len(profiler.stages) == 1
        profiler.clear_stages()
        assert len(profiler.stages) == 0
