# Release Notes - v[VERSION] ([DATE])

## Overview

[1-2 sentence overview of the release's focus and primary goals]

---

## Features & Enhancements

### 🎯 Feature Category 1

[Description of major features added in this release]

- Subfeature 1
- Subfeature 2
- Subfeature 3

### 📊 Feature Category 2

[Description of another major feature]

- Implementation detail 1
- Implementation detail 2

---

## Bug Fixes

### 🔧 Bug Category 1

[Description of bugs fixed]

- Bug 1 fixed: [Details]
- Bug 2 fixed: [Details]

---

## Performance Improvements

### ⚡ Performance Enhancement 1

[Description of performance improvement and impact]

- Metric: X% faster
- Impact: Better responsiveness for Y use case

---

## Documentation Improvements

### 📖 New Documentation Files

- **docs/FILE.md**: [Brief description]
- **docs/ANOTHER_FILE.md**: [Brief description]

### 📚 Updated Documentation

- Enhanced X documentation with Y details
- Added examples for Z feature
- Updated roadmap with v[NEXT_VERSION] plans

---

## Technical Details

### Architecture Changes

[Description of any significant architectural changes]

### API Changes

[Document any API additions, removals, or modifications]

```python
# Example of new/changed API
new_function_v[VERSION](param1: str, param2: int) -> Result:
    """Description of the function."""
    pass
```

### Dependencies

**New Dependencies**:
- `package-name>=version.x.x` - Reason for addition

**Updated Dependencies**:
- `existing-package>=version.x.x` - Reason for update (security/features/compatibility)

**Removed Dependencies**:
- `old-package` - Reason for removal (replaced by X, deprecated, etc.)

---

## Breaking Changes

### ⚠️ Breaking Change 1

[Description of breaking change]

**Migration Path**:
```python
# Before v[VERSION]
old_code()

# After v[VERSION]
new_code()
```

### ⚠️ Breaking Change 2

[Description of another breaking change]

---

## Deprecations

### 🔔 Deprecated Feature 1

[Description of deprecated feature]

**Timeline**:
- v[CURRENT]: Warning emitted
- v[NEXT]: Intense warnings
- v[FUTURE]: Removal

**Migration Path**: [Link to migration guide or description]

---

## Known Issues

- **Issue 1**: Description of issue, workaround if available
- **Issue 2**: Description of issue, workaround if available

[Note: For critical issues, consider hotfix release]

---

## Security Updates

### 🔒 Security Fix 1

[Description of security vulnerability and fix]

**CVE**: CVE-XXXX-XXXXX
**Affected Versions**: v[X].x.x - v[Y].x.x
**Fix Introduced**: v[VERSION]

---

## Installation

### From PyPI
```bash
pip install codescalpel==[VERSION]
```

### From GitHub
```bash
pip install git+https://github.com/anthropics/code-scalpel.git@v[VERSION]
```

### Via UVX
```bash
uvx codescalpel mcp
```

---

## Contributors

[List main contributors, if applicable]
- Name 1
- Name 2
- Code Scalpel Team

---

## Testing

This release has been tested on:
- Python 3.10, 3.11, 3.12, 3.13
- macOS, Linux, Windows
- [Any specific platforms or configurations]

---

## Support

For issues, questions, or feature requests, please visit:
- GitHub Issues: https://github.com/anthropics/code-scalpel/issues
- Documentation: https://github.com/anthropics/code-scalpel#documentation
- Discord: [Link if available]

---

## Changelog

See [CHANGELOG.md](../../CHANGELOG.md) for detailed commit history.

---

## What's Next?

[Brief description of planned features for next release]

---

## Acknowledgments

[Any special acknowledgments or thanks]

---

**Release Date**: [DATE]
**Released by**: [PERSON/TEAM]
**Signature**: [COMMIT HASH or TAG]
