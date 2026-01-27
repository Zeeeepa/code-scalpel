# Secrets Management Guide

## Overview

This guide covers best practices for managing secrets in Code Scalpel's release automation system.

## Table of Contents

1. [Setting Up Secrets](#setting-up-secrets)
2. [Validating Secrets](#validating-secrets)
3. [Secret Rotation](#secret-rotation)
4. [Environment Configuration](#environment-configuration)
5. [Troubleshooting](#troubleshooting)

## Setting Up Secrets

### Creating Secrets

```python
from code_scalpel.release.secrets_manager import SecretsManager
from datetime import datetime, timedelta

manager = SecretsManager()

# Add PyPI token
manager.set_secret(
    name="PYPI_TOKEN",
    value="your_pypi_token_here",
    type="pypi",
    expires_at=datetime.now() + timedelta(days=365)
)

# Add Docker credentials
manager.set_secret(
    name="DOCKER_USERNAME",
    value="your_username",
    type="docker"
)
manager.set_secret(
    name="DOCKER_PASSWORD",
    value="your_password",
    type="docker"
)
```

## Validating Secrets

Always validate secrets before starting a release:

```python
# Validate all required secrets
status = manager.validate_secrets()

if not status['all_valid']:
    print("Missing secrets:")
    for secret_name in status['missing']:
        print(f"  - {secret_name}")
        
if status['expired']:
    print("Expired secrets:")
    for secret_name in status['expired']:
        print(f"  - {secret_name}")
```

## Secret Rotation

### Checking Expiration Status

```python
# Get expiration report
report = manager.get_expiry_report()

print("Expiration Status:")
for secret_name, expiry_info in report.items():
    if expiry_info['days_until_expiry'] is None:
        print(f"  {secret_name}: No expiration")
    elif expiry_info['days_until_expiry'] < 30:
        print(f"  {secret_name}: EXPIRING SOON ({expiry_info['days_until_expiry']} days)")
    else:
        print(f"  {secret_name}: OK ({expiry_info['days_until_expiry']} days)")
```

### Rotating Secrets

```python
# Rotate an expiring secret
old_secret = manager.get_secret("PYPI_TOKEN")
print(f"Current token: {old_secret}")

# Generate new token and update
manager.set_secret(
    name="PYPI_TOKEN",
    value="new_token_value",
    type="pypi",
    expires_at=datetime.now() + timedelta(days=365)
)

print("Secret rotated successfully")
```

## Environment Configuration

### Loading Secrets into Environment

```python
# Add single secret to environment
manager.add_to_env("PYPI_TOKEN")

# Export all secrets
all_secrets = manager.export_secrets(exclude_expired=True)

# Use in subprocess
import os
import subprocess

env = os.environ.copy()
env.update(all_secrets)

subprocess.run(["python", "setup.py", "upload"], env=env)
```

## Best Practices

1. **Never commit secrets**: Always use environment variables
2. **Rotate regularly**: Rotate secrets every 90-365 days
3. **Monitor expiration**: Check expiration status regularly
4. **Use strong tokens**: Generate new tokens instead of reusing old ones
5. **Restrict permissions**: Grant only necessary permissions to tokens
6. **Audit access**: Log which secrets are accessed and when

## Troubleshooting

### Secret not found

```python
try:
    secret = manager.get_secret("UNKNOWN_SECRET")
except KeyError as e:
    print(f"Secret not found: {e}")
```

### Expired secret

```python
secret = manager.get_secret("PYPI_TOKEN")
if secret.is_expired():
    raise RuntimeError(f"Secret '{secret.name}' has expired!")
```

### Missing required secrets

```python
status = manager.validate_secrets()
if not status['all_valid']:
    raise RuntimeError(f"Missing required secrets: {status['missing']}")
```
