# Release Automation API Reference

## Overview

This document provides comprehensive API documentation for all release automation modules in Code Scalpel.

## Table of Contents

1. [Secrets Manager](#secrets-manager)
2. [Changelog Generator](#changelog-generator)
3. [Release Notes Templates](#release-notes-templates)
4. [Rollback Manager](#rollback-manager)
5. [Metrics Tracker](#metrics-tracker)
6. [Build Profiler](#build-profiler)
7. [Status Dashboard](#status-dashboard)
8. [Failure Alerter](#failure-alerter)

---

## Secrets Manager

Module: `code_scalpel.release.secrets_manager`

### Secret Class

Data class representing a single secret with metadata.

**Attributes:**
- `name` (str): Name of the secret
- `value` (str): Secret value (masked in logs)
- `type` (str): Type of secret (pypi, vscode, docker, github)
- `created_at` (datetime): When the secret was created
- `expires_at` (Optional[datetime]): When the secret expires
- `environment` (str): GitHub environment (prod, staging)

**Methods:**
- `is_expired() -> bool`: Check if secret has expired
- `days_until_expiry() -> Optional[int]`: Get days until expiry
- `__str__() -> str`: Return masked representation

**Example:**
```python
from code_scalpel.release.secrets_manager import Secret
from datetime import datetime, timedelta

secret = Secret(
    name="PYPI_TOKEN",
    value="pypi_token_value",
    type="pypi",
    created_at=datetime.now(),
    expires_at=datetime.now() + timedelta(days=365)
)

if secret.is_expired():
    print("Secret has expired!")
else:
    days_left = secret.days_until_expiry()
    print(f"Secret expires in {days_left} days")
```

### SecretsManager Class

Manages GitHub Actions secrets for release automation.

**Methods:**
- `__init__(project_dir: str = ".")`: Initialize manager
- `validate_secrets() -> dict`: Validate all required secrets
- `get_secret(name: str) -> Secret`: Get a secret by name
- `set_secret(name: str, value: str, type: str, expires_at: Optional[datetime] = None)`: Add/update secret
- `add_to_env(name: str) -> None`: Add secret to environment
- `export_secrets(exclude_expired: bool = False) -> dict`: Export all secrets
- `get_expiry_report() -> dict`: Get expiration status report
- `get_status() -> dict`: Get overall status report

**Example:**
```python
from code_scalpel.release.secrets_manager import SecretsManager

manager = SecretsManager()
manager.set_secret("PYPI_TOKEN", "your_token_here", "pypi")

# Validate all required secrets
status = manager.validate_secrets()
print(status['all_valid'])  # True or False

# Get expiration report
report = manager.get_expiry_report()
for secret_name, days_until_expiry in report.items():
    print(f"{secret_name}: expires in {days_until_expiry} days")
```

---

## Changelog Generator

Module: `code_scalpel.release.changelog_generator`

### ChangeEntry Class

Represents a single change in the changelog.

**Attributes:**
- `message` (str): The change message
- `type` (ChangeType): Type of change (Feature, Fix, Breaking, etc.)
- `commit_hash` (str): Associated git commit hash
- `author` (str): Author of the change
- `date` (datetime): Date of the change
- `issue_number` (Optional[str]): Associated issue number
- `breaking_details` (Optional[str]): Details about breaking changes

**Example:**
```python
from code_scalpel.release.changelog_generator import ChangeEntry, ChangeType
from datetime import datetime

entry = ChangeEntry(
    message="Add new API endpoint",
    type=ChangeType.FEATURE,
    commit_hash="abc123def",
    author="John Doe",
    date=datetime.now(),
    issue_number="42"
)
```

### ChangelogGenerator Class

Generates changelogs from commit history with template support.

**Methods:**
- `__init__(project_dir: str = ".")`: Initialize generator
- `add_entry(message, version, commit_hash, author, date=None) -> ChangeEntry`: Add entry
- `create_section(version, title=None, date=None) -> ChangelogSection`: Create version section
- `generate() -> str`: Generate Markdown changelog
- `format_changelog(format_type) -> str`: Format in specified format (Markdown/HTML/JSON)
- `get_changelog(version=None) -> str`: Get changelog for specific version
- `add_breaking_change(title, description, version, commit_hash, author)`: Add breaking change
- `export_to_file(file_path, format_type=ChangelogFormat.MARKDOWN)`: Export to file

**Supported Formats:**
- `ChangelogFormat.MARKDOWN`: Markdown format
- `ChangelogFormat.HTML`: HTML format
- `ChangelogFormat.JSON`: JSON format

**Example:**
```python
from code_scalpel.release.changelog_generator import ChangelogGenerator, ChangelogFormat

generator = ChangelogGenerator()

# Add entries
generator.add_entry(
    message="feat: add new feature",
    version="1.0.0",
    commit_hash="abc123",
    author="John Doe"
)

generator.add_entry(
    message="fix: resolve bug",
    version="1.0.0",
    commit_hash="def456",
    author="Jane Smith"
)

# Generate Markdown
markdown = generator.generate()
print(markdown)

# Export to HTML
generator.export_to_file("CHANGELOG.html", ChangelogFormat.HTML)

# Export to JSON
generator.export_to_file("CHANGELOG.json", ChangelogFormat.JSON)
```

---

## Release Notes Templates

Module: `code_scalpel.release.release_notes_templates`

### Template Class

Represents a release notes template with variables.

**Attributes:**
- `name` (str): Template name
- `content` (str): Template content with variables
- `variables` (list[str]): List of required variables
- `custom_formatters` (dict): Custom formatting functions
- `parent` (Optional[str]): Parent template

**Methods:**
- `render(context: dict) -> str`: Render template with context
- `add_formatter(variable: str, formatter: Callable)`: Add custom formatter

**Example:**
```python
from code_scalpel.release.release_notes_templates import Template

template = Template(
    name="custom",
    content="Version {{version}} released on {{date}}\n\n{{features}}",
    variables=["version", "date", "features"]
)

# Add custom formatter
template.add_formatter("date", lambda x: f"📅 {x}")

# Render template
result = template.render({
    "version": "1.0.0",
    "date": "2024-01-15",
    "features": "- Feature 1\n- Feature 2"
})
print(result)
```

### ReleaseNotesTemplate Class

Main interface for release notes template operations.

**Built-in Templates:**
- `default`: Standard template with all sections
- `minimal`: Concise template
- `detailed`: Comprehensive template with migration guide
- `highlight-breaking-changes`: Emphasizes breaking changes

**Methods:**
- `__init__()`: Initialize template manager
- `load_template(name) -> Template`: Load template by name
- `render(template_name, context) -> str`: Render template
- `list_available() -> list[str]`: List all available templates
- `create_custom(name, content, variables=None) -> Template`: Create custom template
- `get_default_context(version) -> dict`: Get default context for rendering

**Example:**
```python
from code_scalpel.release.release_notes_templates import ReleaseNotesTemplate

template_manager = ReleaseNotesTemplate()

# List available templates
templates = template_manager.list_available()
print(templates)  # ['default', 'minimal', 'detailed', 'highlight-breaking-changes']

# Get default context
context = template_manager.get_default_context("1.0.0")

# Fill in details
context["summary"] = "Major release with new features"
context["features"] = "- Feature A\n- Feature B"
context["fixes"] = "- Bug fix 1"

# Render using default template
release_notes = template_manager.render("default", context)
print(release_notes)

# Create custom template
custom = template_manager.create_custom(
    "my_template",
    "## {{version}}\n\n{{summary}}"
)
```

---

## Rollback Manager

Module: `code_scalpel.release.rollback_manager`

### RollbackPoint Class

Represents a point in history that can be rolled back to.

**Attributes:**
- `version` (str): Version number
- `commit_hash` (str): Git commit hash
- `timestamp` (datetime): When released
- `description` (str): Release description
- `is_stable` (bool): Whether this is a stable release

### Hotfix Class

Represents a hotfix for a released version.

**Attributes:**
- `hotfix_version` (str): Hotfix version (e.g., 1.0.1)
- `target_version` (str): Version being fixed
- `created_at` (datetime): When created
- `branch_name` (str): Git branch name
- `status` (str): Current status
- `description` (str): Hotfix description

### RollbackManager Class

Manages release rollbacks and hotfix workflows.

**Methods:**
- `__init__(project_dir: str = ".")`: Initialize manager
- `add_rollback_point(version, commit_hash, description="", is_stable=True)`: Add rollback point
- `list_rollback_points(stable_only=False) -> list[RollbackPoint]`: List available points
- `get_rollback_point(version) -> Optional[RollbackPoint]`: Get specific point
- `rollback_to_version(version, reason="") -> dict`: Execute rollback
- `create_hotfix(target_version, hotfix_description="") -> Hotfix`: Create hotfix
- `apply_hotfix(hotfix_version) -> dict`: Apply hotfix
- `list_hotfixes(target_version=None) -> list[Hotfix]`: List hotfixes
- `get_rollback_history() -> list[dict]`: Get rollback operations
- `can_rollback_to(version) -> bool`: Check if rollback possible

**Example:**
```python
from code_scalpel.release.rollback_manager import RollbackManager

manager = RollbackManager()

# Add rollback points
manager.add_rollback_point("1.0.0", "abc123", "Initial release", is_stable=True)
manager.add_rollback_point("1.1.0", "def456", "Minor update", is_stable=True)

# List available rollback points
points = manager.list_rollback_points(stable_only=True)
for point in points:
    print(f"Can rollback to {point.version}")

# Create and apply hotfix
hotfix = manager.create_hotfix("1.0.0", "Security patch")
print(f"Created hotfix: {hotfix.hotfix_version}")

manager.apply_hotfix(hotfix.hotfix_version)

# Rollback if needed
if manager.can_rollback_to("1.0.0"):
    result = manager.rollback_to_version("1.0.0", reason="Critical bug found")
    print(result)
```

---

## Metrics Tracker

Module: `code_scalpel.release.metrics_tracker`

### Metric Class

Represents a recorded metric.

**Attributes:**
- `name` (str): Metric name
- `value` (float): Metric value
- `type` (MetricType): Type of metric
- `timestamp` (datetime): When recorded
- `tags` (dict): Tags for grouping

### MetricsTracker Class

Tracks and analyzes release metrics.

**Methods:**
- `__init__()`: Initialize tracker
- `record_metric(name, value, metric_type=MetricType.CUSTOM, tags=None) -> Metric`: Record metric
- `get_metrics(metric_type=None, tag_filter=None) -> list[Metric]`: Get metrics
- `calculate_statistics(metric_type=None) -> dict`: Calculate stats
- `export_metrics() -> list[dict]`: Export all metrics
- `get_metric_summary() -> dict`: Get summary by type

**Example:**
```python
from code_scalpel.release.metrics_tracker import MetricsTracker, MetricType

tracker = MetricsTracker()

# Record metrics
tracker.record_metric("build_time", 45.5, MetricType.BUILD_TIME, {"branch": "main"})
tracker.record_metric("test_duration", 120, MetricType.TEST_DURATION)
tracker.record_metric("publish_time", 15.3, MetricType.PUBLISH_TIME)

# Get statistics
stats = tracker.calculate_statistics(MetricType.BUILD_TIME)
print(f"Build times - Count: {stats['count']}, Mean: {stats['mean']}, Max: {stats['max']}")

# Get summary
summary = tracker.get_metric_summary()
for metric_type, stats in summary.items():
    print(f"{metric_type}: avg {stats['mean']:.2f}s")
```

---

## Build Profiler

Module: `code_scalpel.release.build_profiler`

### BuildStage Class

Represents a build stage with timing.

**Attributes:**
- `name` (str): Stage name
- `duration` (float): Duration in seconds
- `timestamp` (datetime): When recorded

### BuildProfiler Class

Profile build stages and identify bottlenecks.

**Methods:**
- `__init__()`: Initialize profiler
- `record_stage(name, duration) -> BuildStage`: Record stage
- `profile_build() -> dict`: Get build profile
- `get_bottlenecks(threshold=0.1) -> list[BuildStage]`: Get bottlenecks
- `compare_builds(other_profiler) -> dict`: Compare two builds
- `generate_report() -> str`: Generate profiling report

**Example:**
```python
from code_scalpel.release.build_profiler import BuildProfiler

profiler = BuildProfiler()

# Record build stages
profiler.record_stage("compile", 30)
profiler.record_stage("test", 120)
profiler.record_stage("package", 10)

# Get profile
profile = profiler.profile_build()
print(f"Total time: {profile['total_time']}s")

# Identify bottlenecks
bottlenecks = profiler.get_bottlenecks(threshold=0.1)
for stage in bottlenecks:
    print(f"Bottleneck: {stage.name}")

# Generate report
report = profiler.generate_report()
print(report)
```

---

## Status Dashboard

Module: `code_scalpel.release.status_dashboard`

### PublishEvent Class

Represents a publishing event.

**Attributes:**
- `stage` (str): Stage name
- `status` (PublishStatus): Event status
- `timestamp` (datetime): When occurred
- `message` (str): Event message

### StatusDashboard Class

Real-time publishing status tracking.

**Methods:**
- `__init__()`: Initialize dashboard
- `update_status(stage, status, message="") -> PublishEvent`: Update status
- `get_current_status() -> dict`: Get current status
- `render_dashboard() -> str`: Render as text
- `export_status() -> dict`: Export status data

**Example:**
```python
from code_scalpel.release.status_dashboard import StatusDashboard, PublishStatus

dashboard = StatusDashboard()
dashboard.current_version = "1.0.0"

# Update status
dashboard.update_status("build", PublishStatus.IN_PROGRESS)
dashboard.update_status("build", PublishStatus.COMPLETED)
dashboard.update_status("test", PublishStatus.IN_PROGRESS)

# Get current status
status = dashboard.get_current_status()
print(f"Overall: {status['overall_status']}")

# Render dashboard
print(dashboard.render_dashboard())

# Export for reporting
exported = dashboard.export_status()
```

---

## Failure Alerter

Module: `code_scalpel.release.failure_alerter`

### Alert Class

Represents an alert notification.

**Attributes:**
- `title` (str): Alert title
- `message` (str): Alert message
- `severity` (str): Severity level
- `timestamp` (datetime): When created
- `channel` (AlertChannel): Notification channel

### FailureAlerter Class

Send alerts on release failures.

**Methods:**
- `__init__()`: Initialize alerter
- `configure_channel(channel, config)`: Configure channel
- `list_channels() -> list[AlertChannel]`: List configured channels
- `register_handler(channel, handler)`: Register custom handler
- `create_alert(title, message, severity="error", channel=AlertChannel.CONSOLE)`: Create alert
- `send_alert(title, message, channel=AlertChannel.CONSOLE, severity="error") -> bool`: Send alert
- `get_alerts(channel=None) -> list[Alert]`: Get alerts

**Example:**
```python
from code_scalpel.release.failure_alerter import FailureAlerter, AlertChannel

alerter = FailureAlerter()

# Configure channels
alerter.configure_channel(AlertChannel.EMAIL, {"smtp": "smtp.example.com"})
alerter.configure_channel(AlertChannel.SLACK, {"webhook": "https://hooks.slack.com/..."})

# Register custom handlers
def email_handler(alert):
    # Send email logic
    print(f"Sending email: {alert.title}")
    return True

alerter.register_handler(AlertChannel.EMAIL, email_handler)

# Send alerts
alerter.send_alert(
    "Build Failed",
    "Compilation error in main branch",
    channel=AlertChannel.SLACK,
    severity="critical"
)

# Get alerts
all_alerts = alerter.get_alerts()
slack_alerts = alerter.get_alerts(AlertChannel.SLACK)
```

---

## Common Patterns

### Error Handling

All modules implement proper error handling:

```python
try:
    manager.rollback_to_version("nonexistent")
except ValueError as e:
    print(f"Error: {e}")

try:
    template_manager.render("unknown_template", {})
except ValueError as e:
    print(f"Template error: {e}")
```

### Type Hints

All modules use full type hints for IDE support:

```python
from typing import Optional, list, dict

def get_secrets(filter_by_type: Optional[str] = None) -> list[dict]:
    ...
```

### Context Managers

Some modules support context manager patterns:

```python
with StatusDashboard() as dashboard:
    dashboard.update_status("build", PublishStatus.IN_PROGRESS)
    # Automatic cleanup on exit
```

---

## Related Documentation

- [Secrets Management Guide](guides/secrets_management_guide.md)
- [Changelog Generation Guide](guides/changelog_generation_guide.md)
- [Rollback Procedures](guides/rollback_procedures.md)
- [Metrics and Monitoring](guides/metrics_and_monitoring.md)
- [Architecture Guide](architecture.md)
