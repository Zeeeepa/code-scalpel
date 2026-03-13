"""
Codegen Configuration Adapter

Direct imports from Codegen SDK configuration - no reimplementation.
Provides codebase configuration and factory patterns.

Features:
- Codebase configuration
- Config file parsing
- Factory patterns for codebase creation
- Session management
"""

from codegen.sdk.codebase.config import Config as _Config
from codegen.sdk.codebase.config_parser import (
    parse_config as _parse_config,
    ConfigParser as _ConfigParser
)
from codegen.sdk.codebase.factory.codebase_factory import (
    CodebaseFactory as _CodebaseFactory
)
from codegen.sdk.codebase.factory.get_session import (
    get_session as _get_session
)

# Re-export with tier unification
# All configuration functionality is now Community tier accessible

Config = _Config
"""
Configuration class - Community tier

Codebase configuration with:
- Language settings
- Parser options
- Index configuration
- Performance tuning

Example:
    config = Config(
        languages=["python", "typescript"],
        max_file_size=10_000_000,
        enable_caching=True
    )
"""

def parse_config(*args, **kwargs):
    """
    Parse configuration file - Community tier
    
    Parses configuration from:
    - YAML files
    - JSON files
    - TOML files
    - Python dicts
    
    Returns:
        Config object
    """
    return _parse_config(*args, **kwargs)


ConfigParser = _ConfigParser
"""
Configuration parser class - Community tier

Handles configuration parsing with:
- Multiple format support
- Validation
- Default values
- Environment variable expansion
"""

CodebaseFactory = _CodebaseFactory
"""
Codebase factory class - Community tier

Factory for creating Codebase instances with:
- Configuration-based creation
- Language detection
- Parser selection
- Index initialization

Example:
    factory = CodebaseFactory(config)
    codebase = factory.create_from_path("/path/to/repo")
"""

def get_session(*args, **kwargs):
    """
    Get or create session - Community tier
    
    Session management with:
    - Session caching
    - Resource pooling
    - Cleanup on exit
    
    Returns:
        Session object
    """
    return _get_session(*args, **kwargs)


__all__ = [
    'Config',
    'parse_config',
    'ConfigParser',
    'CodebaseFactory',
    'get_session',
]

