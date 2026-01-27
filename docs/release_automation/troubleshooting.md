# Troubleshooting Guide

## Common Issues and Solutions

### Secrets Management

#### Issue: "Secret not found"

**Cause**: Secret name mismatch or not loaded from environment

**Solution**:
```python
# Check loaded secrets
manager = SecretsManager()
if not manager.get_secret("PYPI_TOKEN"):
    # Load from environment
    import os
    os.environ["PYPI_TOKEN"] = "your_token"
    manager = SecretsManager()  # Reinitialize
```

#### Issue: Secret expired but still being used

**Cause**: No expiration checking before use

**Solution**:
```python
secret = manager.get_secret("PYPI_TOKEN")
if secret.is_expired():
    raise RuntimeError(f"Secret {secret.name} has expired!")
```

### Changelog Generation

#### Issue: Commits not appearing in changelog

**Cause**: Commit message doesn't match patterns

**Solution**:
```python
# Use proper commit message format
# feat: description
# fix: description
# BREAKING CHANGE: description

# Or check categorization
message = "your commit message"
change_type = generator._categorize_message(message)
print(f"Categorized as: {change_type}")
```

#### Issue: Issue numbers not extracted

**Cause**: Issue numbers not in message

**Solution**:
```python
# Include issue number in message
message = "Fix security issue #123"
issue_num = generator._extract_issue_number(message)
print(f"Issue: {issue_num}")
```

### Release Notes

#### Issue: Variables not rendering

**Cause**: Missing required variables in context

**Solution**:
```python
try:
    result = template_mgr.render("default", context)
except KeyError as e:
    print(f"Missing variable: {e}")
    # Add missing variable to context
    context[str(e).strip("'")] = "value"
```

### Rollback Management

#### Issue: Cannot rollback to version

**Cause**: Version not marked as stable

**Solution**:
```python
# Check if rollback possible
if manager.can_rollback_to("1.0.0"):
    manager.rollback_to_version("1.0.0")
else:
    # Add rollback point if missing
    manager.add_rollback_point("1.0.0", "abc123", is_stable=True)
```

### Metrics and Monitoring

#### Issue: No metrics being recorded

**Cause**: Tracker not initialized or recording not called

**Solution**:
```python
tracker = MetricsTracker()

# Record metrics
tracker.record_metric("build_time", 45.5, MetricType.BUILD_TIME)

# Verify recording
metrics = tracker.get_metrics()
print(f"Recorded {len(metrics)} metrics")
```

#### Issue: Statistics show zeros

**Cause**: No metrics recorded for metric type

**Solution**:
```python
# Record some metrics first
tracker.record_metric("m1", 10, MetricType.BUILD_TIME)
tracker.record_metric("m2", 20, MetricType.BUILD_TIME)

# Now calculate statistics
stats = tracker.calculate_statistics(MetricType.BUILD_TIME)
```

### Build Profiling

#### Issue: Bottleneck identification not working

**Cause**: Threshold too high or insufficient data

**Solution**:
```python
# Try lower threshold
bottlenecks = profiler.get_bottlenecks(threshold=0.05)  # 5% instead of 10%

# Verify total time
profile = profiler.profile_build()
print(f"Total time: {profile['total_time']}")
```

### Status Dashboard

#### Issue: Events not updating

**Cause**: Dashboard not properly tracking state

**Solution**:
```python
dashboard = StatusDashboard()
dashboard.current_version = "1.0.0"  # Must set version first

# Now update status
dashboard.update_status("build", PublishStatus.IN_PROGRESS)

# Verify update
status = dashboard.get_current_status()
print(status)
```

### Failure Alerting

#### Issue: Alerts not being sent

**Cause**: Channel not configured or handler not registered

**Solution**:
```python
alerter = FailureAlerter()

# Must configure channel first
alerter.configure_channel(AlertChannel.SLACK, {"webhook": "https://..."})

# Then send alert
success = alerter.send_alert("Title", "Message", AlertChannel.SLACK)
if not success:
    print("Alert failed to send")
```

## Debugging Tips

### Enable Detailed Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("release_automation")
logger.setLevel(logging.DEBUG)
```

### Inspect Object State

```python
# Secrets
print(f"Loaded secrets: {list(manager.secrets.keys())}")

# Changelog
print(f"Sections: {len(generator.sections)}")
for section in generator.sections:
    print(f"  {section.version}: {len(section.entries)} entries")

# Metrics
print(f"Recorded metrics: {len(tracker.metrics)}")
```

### Export and Review Data

```python
# Export metrics
import json
metrics = tracker.export_metrics()
print(json.dumps(metrics, indent=2))

# Export status
status = dashboard.export_status()
print(json.dumps(status, indent=2))
```

## Performance Issues

### Slow Changelog Generation

**Possible causes**:
- Processing large number of commits
- Complex regex patterns

**Solutions**:
```python
# Generate for specific version only
changelog = generator.get_changelog(version="1.0.0")

# Use simpler patterns for large repos
```

### Memory Issues with Metrics

**Solutions**:
```python
# Clear old metrics periodically
if len(tracker.metrics) > 10000:
    tracker.clear_metrics()

# Use streaming export for large datasets
for metric in tracker.export_metrics():
    process_metric(metric)
```

## Contact and Support

For additional support:
- Check GitHub issues: https://github.com/code-scalpel/issues
- Review test files for usage examples
- Check API reference documentation
