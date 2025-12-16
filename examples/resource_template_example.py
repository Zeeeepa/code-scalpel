"""
Resource Template Example

[20251216_FEATURE] v2.0.2 - Demonstrates accessing code via URIs.

This example shows how to use Code Scalpel's resource templates
to access code elements via parameterized URIs without knowing
exact file paths.
"""

import asyncio
import tempfile
import json
from pathlib import Path
from code_scalpel.mcp.server import get_code_resource
from code_scalpel.mcp import server


async def setup_example_project():
    """Set up example project structure."""
    tmpdir = tempfile.mkdtemp()
    project_root = Path(tmpdir)

    # Create Python module
    (project_root / "utils.py").write_text('''
def calculate_tax(amount):
    """Calculate tax on an amount."""
    return amount * 0.1

def format_currency(value):
    """Format value as currency."""
    return f"${value:.2f}"
''')

    # Create TypeScript component
    components_dir = project_root / "components"
    components_dir.mkdir()
    (components_dir / "Button.tsx").write_text('''
interface ButtonProps {
  label: string;
  onClick: () => void;
}

export function Button({ label, onClick }: ButtonProps) {
  return <button onClick={onClick}>{label}</button>;
}
''')

    # Create JavaScript module
    services_dir = project_root / "services"
    services_dir.mkdir()
    (services_dir / "auth.js").write_text('''
export function authenticate(username, password) {
  // Authentication logic here
  return { token: "example-token", user: { username } };
}
''')

    return project_root


async def example_python_resource():
    """Access Python code via URI."""
    print("=" * 60)
    print("Example 1: Python Function via code:/// URI")
    print("=" * 60)

    result_json = await get_code_resource("python", "utils", "calculate_tax")
    result = json.loads(result_json)

    if "error" not in result:
        print(f"✓ URI: {result['uri']}")
        print(f"✓ MIME Type: {result['mimeType']}")
        print(f"✓ File Path: {result['metadata']['file_path']}")
        print(f"✓ Lines: {result['metadata']['line_start']} - {result['metadata']['line_end']}")
        print(f"✓ Code:\n{result['code']}")
    else:
        print(f"✗ Error: {result['error']}")
    print()


async def example_typescript_resource():
    """Access TypeScript component via URI."""
    print("=" * 60)
    print("Example 2: TypeScript Component via code:/// URI")
    print("=" * 60)

    result_json = await get_code_resource("typescript", "components/Button", "Button")
    result = json.loads(result_json)

    if "error" not in result:
        print(f"✓ URI: {result['uri']}")
        print(f"✓ MIME Type: {result['mimeType']}")
        print(f"✓ Component Type: {result['metadata']['component_type']}")
        print(f"✓ JSX Normalized: {result['metadata']['jsx_normalized']}")
        print(f"✓ Code:\n{result['code'][:200]}...")  # First 200 chars
    else:
        print(f"✗ Error: {result['error']}")
    print()


async def example_javascript_resource():
    """Access JavaScript function via URI."""
    print("=" * 60)
    print("Example 3: JavaScript Function via code:/// URI")
    print("=" * 60)

    result_json = await get_code_resource("javascript", "services/auth", "authenticate")
    result = json.loads(result_json)

    if "error" not in result:
        print(f"✓ URI: {result['uri']}")
        print(f"✓ MIME Type: {result['mimeType']}")
        print(f"✓ Token Estimate: {result['metadata']['token_estimate']}")
        print(f"✓ Code:\n{result['code']}")
    else:
        print(f"✗ Error: {result['error']}")
    print()


async def example_error_handling():
    """Demonstrate error handling for invalid URIs."""
    print("=" * 60)
    print("Example 4: Error Handling")
    print("=" * 60)

    # Try to access non-existent module
    result_json = await get_code_resource("python", "nonexistent", "func")
    result = json.loads(result_json)

    print(f"✓ Error message: {result['error']}")
    print(f"✓ Language: {result['language']}")
    print(f"✓ Module: {result['module']}")
    print(f"✓ Symbol: {result['symbol']}")
    print()


async def main():
    """Run all examples."""
    print("\nCode Scalpel v2.0.2 - Resource Template Examples\n")

    # Setup example project
    project_root = await setup_example_project()
    original_root = server.PROJECT_ROOT
    server.PROJECT_ROOT = project_root

    try:
        await example_python_resource()
        await example_typescript_resource()
        await example_javascript_resource()
        await example_error_handling()

        print("=" * 60)
        print("All examples completed successfully!")
        print(f"Example project created at: {project_root}")
        print("=" * 60)
    finally:
        # Restore original PROJECT_ROOT
        server.PROJECT_ROOT = original_root


if __name__ == "__main__":
    asyncio.run(main())
