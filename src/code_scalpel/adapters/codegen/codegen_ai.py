"""
Codegen AI Adapter

Direct imports from Codegen SDK AI features - no reimplementation.
Provides AI-powered code generation, analysis, and refactoring.

Features:
- AI-powered code generation
- Context-aware transformations
- Intelligent docstring generation
- Semantic code analysis
"""

from codegen.sdk.codebase.codebase_ai import (
    generate_system_prompt as _generate_system_prompt,
    generate_flag_system_prompt as _generate_flag_system_prompt,
    generate_context as _generate_context,
    generate_tools as _generate_tools,
    generate_flag_tools as _generate_flag_tools,
)

# Re-export with tier unification
# All AI functionality is now Community tier accessible

def generate_system_prompt(*args, **kwargs):
    """
    Generate AI system prompt - Community tier (unified from Enterprise)
    
    Creates context-aware system prompts for AI operations with:
    - Target code context
    - Surrounding code context
    - Dependency information
    - Usage patterns
    
    Args:
        target: The code element to focus on (optional)
        context: Additional context (str, Editable, list, or dict)
        
    Returns:
        Formatted system prompt string
        
    Example:
        prompt = generate_system_prompt(
            target=function,
            context={"dependencies": deps, "usages": usages}
        )
    """
    return _generate_system_prompt(*args, **kwargs)


def generate_flag_system_prompt(*args, **kwargs):
    """
    Generate flagging system prompt - Community tier (unified from Enterprise)
    
    Creates prompts for identifying code issues with:
    - Code smell detection
    - Security vulnerability identification
    - Performance issue flagging
    - Best practice violations
    
    Args:
        target: The code element to analyze
        context: Additional context for analysis
        
    Returns:
        Formatted flagging prompt string
    """
    return _generate_flag_system_prompt(*args, **kwargs)


def generate_context(*args, **kwargs):
    """
    Generate AI context - Community tier (unified from Enterprise)
    
    Formats code context for AI consumption with:
    - Code snippets
    - Symbol information
    - Dependency graphs
    - Usage examples
    
    Args:
        context: Context to format (str, Editable, File, list, or dict)
        
    Returns:
        Formatted context string
        
    Example:
        context_str = generate_context({
            "current_file": file,
            "dependencies": [dep1, dep2],
            "usages": usage_list
        })
    """
    return _generate_context(*args, **kwargs)


def generate_tools(*args, **kwargs):
    """
    Generate AI tools - Community tier (unified from Enterprise)
    
    Creates tool definitions for AI function calling with:
    - Tool schemas
    - Parameter definitions
    - Return type specifications
    - Usage examples
    
    Returns:
        List of tool definitions
    """
    return _generate_tools(*args, **kwargs)


def generate_flag_tools(*args, **kwargs):
    """
    Generate flagging tools - Community tier (unified from Enterprise)
    
    Creates tool definitions for code analysis with:
    - Issue detection tools
    - Severity classification
    - Fix suggestions
    - Impact analysis
    
    Returns:
        List of flagging tool definitions
    """
    return _generate_flag_tools(*args, **kwargs)


__all__ = [
    'generate_system_prompt',
    'generate_flag_system_prompt',
    'generate_context',
    'generate_tools',
    'generate_flag_tools',
]

