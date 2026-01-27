# Rollback and Hotfix Procedures

## Overview

Handle releases failures and create hotfixes efficiently.

## Adding Rollback Points

```python
from code_scalpel.release.rollback_manager import RollbackManager

manager = RollbackManager()

# Record released versions
manager.add_rollback_point(
    version="1.0.0",
    commit_hash="abc123def",
    description="Initial production release",
    is_stable=True
)

manager.add_rollback_point(
    version="1.1.0",
    commit_hash="def456abc",
    description="Bug fix release",
    is_stable=True
)
```

## Rolling Back

```python
# Check available rollback points
points = manager.list_rollback_points(stable_only=True)
for point in points:
    print(f"Can rollback to {point.version}")

# Perform rollback
if manager.can_rollback_to("1.0.0"):
    result = manager.rollback_to_version(
        "1.0.0",
        reason="Critical bug in 1.1.0"
    )
    print(f"Rolled back to {result['to_version']}")
```

## Creating Hotfixes

```python
# Create hotfix for a released version
hotfix = manager.create_hotfix(
    target_version="1.0.0",
    hotfix_description="Security patch for XSS vulnerability"
)

print(f"Created: {hotfix.hotfix_version}")
print(f"Branch: {hotfix.branch_name}")

# Apply hotfix
manager.apply_hotfix(hotfix.hotfix_version)
```

## Hotfix Workflow

1. **Create hotfix branch** from stable release tag
2. **Implement fix** with commits
3. **Test thoroughly** 
4. **Create hotfix version** (e.g., 1.0.1 from 1.0.0)
5. **Apply hotfix** through manager
6. **Merge back** to main branch

## Tracking Changes

```python
# View rollback history
history = manager.get_rollback_history()
for operation in history:
    print(f"Rolled back from {operation['from_version']} to {operation['to_version']}")
    print(f"Reason: {operation['reason']}")

# View hotfixes
hotfixes = manager.list_hotfixes()
for hotfix in hotfixes:
    print(f"{hotfix.hotfix_version}: {hotfix.description}")
```

## Best Practices

1. Keep release tags stable
2. Always test hotfixes
3. Document rollback reasons
4. Monitor performance after rollback
5. Plan backport to main branch
