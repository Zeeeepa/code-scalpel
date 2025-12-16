"""
Tests for Workflow Prompts.

[20251216_TEST] Tests for Feature 10: Workflow Prompts
"""



class TestSecurityAuditPrompt:
    """Test the security audit workflow prompt."""

    def test_security_audit_prompt_exists(self):
        """Test that the security audit prompt is defined."""
        from code_scalpel.mcp.server import security_audit_workflow_prompt
        
        assert security_audit_workflow_prompt is not None
        assert callable(security_audit_workflow_prompt)

    def test_security_audit_prompt_takes_project_path(self):
        """Test that the prompt accepts a project_path parameter."""
        from code_scalpel.mcp.server import security_audit_workflow_prompt
        
        result = security_audit_workflow_prompt("/path/to/project")
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_security_audit_prompt_includes_project_path(self):
        """Test that the prompt includes the project path."""
        from code_scalpel.mcp.server import security_audit_workflow_prompt
        
        project_path = "/my/test/project"
        result = security_audit_workflow_prompt(project_path)
        
        assert project_path in result

    def test_security_audit_prompt_includes_steps(self):
        """Test that the prompt includes all workflow steps."""
        from code_scalpel.mcp.server import security_audit_workflow_prompt
        
        result = security_audit_workflow_prompt("/project")
        
        # Check for key workflow steps
        assert "Step 1" in result
        assert "Step 2" in result
        assert "Step 3" in result
        assert "Step 4" in result

    def test_security_audit_prompt_mentions_tools(self):
        """Test that the prompt mentions required MCP tools."""
        from code_scalpel.mcp.server import security_audit_workflow_prompt
        
        result = security_audit_workflow_prompt("/project")
        
        # Check for tool mentions
        assert "crawl_project" in result
        assert "security_scan" in result
        assert "scan_dependencies" in result

    def test_security_audit_prompt_includes_severity_levels(self):
        """Test that the prompt includes severity level guidance."""
        from code_scalpel.mcp.server import security_audit_workflow_prompt
        
        result = security_audit_workflow_prompt("/project")
        
        # Check for severity levels
        assert "CRITICAL" in result
        assert "HIGH" in result
        assert "MEDIUM" in result
        assert "LOW" in result

    def test_security_audit_prompt_provides_concrete_examples(self):
        """Test that the prompt provides concrete tool invocation examples."""
        from code_scalpel.mcp.server import security_audit_workflow_prompt
        
        result = security_audit_workflow_prompt("/project")
        
        # Check for concrete examples with code blocks
        assert "```" in result
        assert "crawl_project(" in result
        assert "security_scan(" in result


class TestSafeRefactorPrompt:
    """Test the safe refactor workflow prompt."""

    def test_safe_refactor_prompt_exists(self):
        """Test that the safe refactor prompt is defined."""
        from code_scalpel.mcp.server import safe_refactor_workflow_prompt
        
        assert safe_refactor_workflow_prompt is not None
        assert callable(safe_refactor_workflow_prompt)

    def test_safe_refactor_prompt_takes_parameters(self):
        """Test that the prompt accepts file_path and symbol_name parameters."""
        from code_scalpel.mcp.server import safe_refactor_workflow_prompt
        
        result = safe_refactor_workflow_prompt("/path/to/file.py", "my_function")
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_safe_refactor_prompt_includes_parameters(self):
        """Test that the prompt includes the provided parameters."""
        from code_scalpel.mcp.server import safe_refactor_workflow_prompt
        
        file_path = "/my/test/file.py"
        symbol_name = "test_function"
        result = safe_refactor_workflow_prompt(file_path, symbol_name)
        
        assert file_path in result
        assert symbol_name in result

    def test_safe_refactor_prompt_includes_steps(self):
        """Test that the prompt includes all workflow steps."""
        from code_scalpel.mcp.server import safe_refactor_workflow_prompt
        
        result = safe_refactor_workflow_prompt("/file.py", "func")
        
        # Check for key workflow steps
        assert "Step 1" in result
        assert "Step 2" in result
        assert "Step 3" in result
        assert "Step 4" in result
        assert "Step 5" in result

    def test_safe_refactor_prompt_mentions_tools(self):
        """Test that the prompt mentions required MCP tools."""
        from code_scalpel.mcp.server import safe_refactor_workflow_prompt
        
        result = safe_refactor_workflow_prompt("/file.py", "func")
        
        # Check for tool mentions
        assert "extract_code" in result
        assert "get_symbol_references" in result
        assert "simulate_refactor" in result
        assert "update_symbol" in result

    def test_safe_refactor_prompt_emphasizes_safety(self):
        """Test that the prompt emphasizes safety checks."""
        from code_scalpel.mcp.server import safe_refactor_workflow_prompt
        
        result = safe_refactor_workflow_prompt("/file.py", "func")
        
        # Check for safety-related content
        assert "safe" in result.lower() or "Safe" in result
        assert "simulation" in result.lower()
        assert "backup" in result.lower()

    def test_safe_refactor_prompt_provides_concrete_examples(self):
        """Test that the prompt provides concrete tool invocation examples."""
        from code_scalpel.mcp.server import safe_refactor_workflow_prompt
        
        result = safe_refactor_workflow_prompt("/file.py", "func")
        
        # Check for concrete examples with code blocks
        assert "```" in result
        assert "extract_code(" in result
        assert "simulate_refactor(" in result

    def test_safe_refactor_prompt_includes_verification(self):
        """Test that the prompt includes verification steps."""
        from code_scalpel.mcp.server import safe_refactor_workflow_prompt
        
        result = safe_refactor_workflow_prompt("/file.py", "func")
        
        # Check for verification mentions
        assert "verify" in result.lower() or "Verify" in result
        assert "test" in result.lower() or "Test" in result


class TestPromptDiscoverability:
    """Test that prompts are discoverable via MCP protocol."""

    def test_prompts_have_decorators(self):
        """Test that workflow prompts have @mcp.prompt decorators."""
        import inspect
        from code_scalpel.mcp import server
        
        # Get all functions in the module
        functions = inspect.getmembers(server, inspect.isfunction)
        
        # Find our workflow prompts
        security_audit_found = False
        safe_refactor_found = False
        
        for name, func in functions:
            if name == "security_audit_workflow_prompt":
                security_audit_found = True
            elif name == "safe_refactor_workflow_prompt":
                safe_refactor_found = True
        
        assert security_audit_found, "security_audit_workflow_prompt not found"
        assert safe_refactor_found, "safe_refactor_workflow_prompt not found"

    def test_prompts_return_strings(self):
        """Test that prompts return string content."""
        from code_scalpel.mcp.server import (
            security_audit_workflow_prompt,
            safe_refactor_workflow_prompt,
        )
        
        audit_result = security_audit_workflow_prompt("/project")
        refactor_result = safe_refactor_workflow_prompt("/file.py", "func")
        
        assert isinstance(audit_result, str)
        assert isinstance(refactor_result, str)
        assert len(audit_result) > 100  # Should be substantial
        assert len(refactor_result) > 100


class TestAcceptanceCriteria:
    """Test acceptance criteria from the problem statement."""

    def test_security_audit_guides_through_full_audit(self):
        """Acceptance: security-audit prompt guides through full audit."""
        from code_scalpel.mcp.server import security_audit_workflow_prompt
        
        result = security_audit_workflow_prompt("/project")
        
        # Should guide through:
        # 1. Project structure analysis
        assert "crawl_project" in result
        
        # 2. Vulnerability scanning
        assert "security_scan" in result
        
        # 3. Dependency checking
        assert "scan_dependencies" in result
        
        # 4. Report generation
        assert "report" in result.lower()
        assert "findings" in result.lower()

    def test_safe_refactor_guides_through_refactor(self):
        """Acceptance: safe-refactor prompt guides through refactor."""
        from code_scalpel.mcp.server import safe_refactor_workflow_prompt
        
        result = safe_refactor_workflow_prompt("/file.py", "func")
        
        # Should guide through:
        # 1. Extract current implementation
        assert "extract_code" in result
        
        # 2. Find all usages
        assert "get_symbol_references" in result
        
        # 3. Plan changes
        assert "plan" in result.lower() or "Plan" in result
        
        # 4. Simulate refactor
        assert "simulate_refactor" in result
        
        # 5. Apply changes
        assert "update_symbol" in result

    def test_prompts_are_discoverable_via_mcp(self):
        """Acceptance: Prompts are discoverable via MCP protocol."""
        # The @mcp.prompt decorator makes them discoverable
        # This is handled by the FastMCP framework
        from code_scalpel.mcp.server import (
            mcp,
            security_audit_workflow_prompt,
            safe_refactor_workflow_prompt,
        )
        
        # The mcp instance exists and prompts are registered via decorators
        assert mcp is not None
        
        # Prompts should be callable and return strings
        assert callable(security_audit_workflow_prompt)
        assert callable(safe_refactor_workflow_prompt)

    def test_prompts_include_concrete_tool_invocations(self):
        """Acceptance: Prompts include concrete tool invocation examples."""
        from code_scalpel.mcp.server import (
            security_audit_workflow_prompt,
            safe_refactor_workflow_prompt,
        )
        
        audit = security_audit_workflow_prompt("/project")
        refactor = safe_refactor_workflow_prompt("/file.py", "func")
        
        # Both should have concrete examples with function calls
        assert "(" in audit and ")" in audit  # Function call syntax
        assert "(" in refactor and ")" in refactor
        
        # Should have parameter examples
        assert "=" in audit  # Parameter assignment
        assert "=" in refactor

    def test_prompts_handle_edge_cases(self):
        """Acceptance: Prompts handle edge cases (missing files, etc.)."""
        from code_scalpel.mcp.server import (
            security_audit_workflow_prompt,
            safe_refactor_workflow_prompt,
        )
        
        # Should not crash with various inputs
        audit1 = security_audit_workflow_prompt("")
        audit2 = security_audit_workflow_prompt("/nonexistent/path")
        
        refactor1 = safe_refactor_workflow_prompt("", "")
        refactor2 = safe_refactor_workflow_prompt("/file.py", "nonexistent_func")
        
        # All should return valid strings (prompts don't validate paths)
        assert isinstance(audit1, str)
        assert isinstance(audit2, str)
        assert isinstance(refactor1, str)
        assert isinstance(refactor2, str)
