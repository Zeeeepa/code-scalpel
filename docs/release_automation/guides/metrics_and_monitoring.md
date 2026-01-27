# Metrics and Monitoring Guide

## Recording Metrics

```python
from code_scalpel.release.metrics_tracker import MetricsTracker, MetricType
from code_scalpel.release.build_profiler import BuildProfiler

# Track release metrics
tracker = MetricsTracker()

tracker.record_metric(
    "build_time",
    45.5,
    MetricType.BUILD_TIME,
    tags={"branch": "main", "version": "1.0.0"}
)

tracker.record_metric(
    "test_duration",
    120.3,
    MetricType.TEST_DURATION,
    tags={"suite": "unit"}
)
```

## Analyzing Performance

```python
# Get statistics
stats = tracker.calculate_statistics(MetricType.BUILD_TIME)
print(f"Build Time Stats:")
print(f"  Count: {stats['count']}")
print(f"  Average: {stats['mean']:.2f}s")
print(f"  Min: {stats['min']:.2f}s")
print(f"  Max: {stats['max']:.2f}s")

# Profile build stages
profiler = BuildProfiler()
profiler.record_stage("compile", 30)
profiler.record_stage("test", 120)
profiler.record_stage("package", 10)

# Identify bottlenecks
bottlenecks = profiler.get_bottlenecks(threshold=0.1)
for stage in bottlenecks:
    print(f"Bottleneck: {stage.name}")

# Generate report
report = profiler.generate_report()
print(report)
```

## Status Monitoring

```python
from code_scalpel.release.status_dashboard import StatusDashboard, PublishStatus

dashboard = StatusDashboard()
dashboard.current_version = "1.0.0"

# Track progress
dashboard.update_status("build", PublishStatus.IN_PROGRESS)
dashboard.update_status("build", PublishStatus.COMPLETED, "Build succeeded")
dashboard.update_status("test", PublishStatus.IN_PROGRESS)
dashboard.update_status("test", PublishStatus.COMPLETED, "All tests passed")

# Display status
print(dashboard.render_dashboard())

# Export for monitoring systems
status = dashboard.export_status()
```

## Alerting on Failures

```python
from code_scalpel.release.failure_alerter import FailureAlerter, AlertChannel

alerter = FailureAlerter()
alerter.configure_channel(AlertChannel.SLACK, {"webhook": "https://..."})

# Send alert on failure
try:
    # Publish code
    pass
except Exception as e:
    alerter.send_alert(
        "Release Failed",
        str(e),
        channel=AlertChannel.SLACK,
        severity="critical"
    )
```
