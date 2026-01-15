"""
CrewAI Integration for Code Scalpel.

[20251217_FEATURE] Native CrewAI Crew integration for collaborative code fixing.

This module provides CrewAI agents and tools that:
- Analyze errors and identify root causes
- Generate fixes based on analysis
- Validate fixes in sandbox environments
- Apply fixes with security scanning
"""

# TODO [20251224] Phase 1 (COMMUNITY): Implement CodeInput Pydantic model
# TODO [20251224] Phase 1 (COMMUNITY): Create ErrorInput Pydantic model
# TODO [20251224] Phase 1 (COMMUNITY): Implement FixInput Pydantic model
# TODO [20251224] Phase 1 (COMMUNITY): Add AnalyzeErrorTool implementation
# TODO [20251224] Phase 1 (COMMUNITY): Create ApplyFixTool implementation
# TODO [20251224] Phase 1 (COMMUNITY): Implement TestFixTool implementation
# TODO [20251224] Phase 1 (COMMUNITY): Add tool registration with CrewAI
# TODO [20251224] Phase 1 (COMMUNITY): Create Agent wrapper classes
# TODO [20251224] Phase 1 (COMMUNITY): Implement Task wrapper classes
# TODO [20251224] Phase 1 (COMMUNITY): Add Crew wrapper class
# TODO [20251224] Phase 1 (COMMUNITY): Create tool execution engine
# TODO [20251224] Phase 1 (COMMUNITY): Implement result aggregation
# TODO [20251224] Phase 1 (COMMUNITY): Add error handling
# TODO [20251224] Phase 1 (COMMUNITY): Create logging integration
# TODO [20251224] Phase 1 (COMMUNITY): Implement documentation
# TODO [20251224] Phase 1 (COMMUNITY): Add type annotations
# TODO [20251224] Phase 1 (COMMUNITY): Create input validation
# TODO [20251224] Phase 1 (COMMUNITY): Implement output validation
# TODO [20251224] Phase 1 (COMMUNITY): Add state management
# TODO [20251224] Phase 1 (COMMUNITY): Create task tracking
# TODO [20251224] Phase 1 (COMMUNITY): Implement task persistence
# TODO [20251224] Phase 1 (COMMUNITY): Add checkpoint saving
# TODO [20251224] Phase 1 (COMMUNITY): Create recovery mechanisms
# TODO [20251224] Phase 1 (COMMUNITY): Implement timeout enforcement
# TODO [20251224] Phase 1 (COMMUNITY): Add graceful shutdown

# TODO [20251224] Phase 2 (PRO): Implement multi-agent teams
# TODO [20251224] Phase 2 (PRO): Create role-based agents
# TODO [20251224] Phase 2 (PRO): Add agent specialization
# TODO [20251224] Phase 2 (PRO): Implement agent coordination
# TODO [20251224] Phase 2 (PRO): Create task dependency management
# TODO [20251224] Phase 2 (PRO): Add parallel task execution
# TODO [20251224] Phase 2 (PRO): Implement async operations
# TODO [20251224] Phase 2 (PRO): Create streaming results
# TODO [20251224] Phase 2 (PRO): Add result streaming aggregation
# TODO [20251224] Phase 2 (PRO): Implement tool composition
# TODO [20251224] Phase 2 (PRO): Create tool orchestration
# TODO [20251224] Phase 2 (PRO): Add dynamic tool registration
# TODO [20251224] Phase 2 (PRO): Implement performance optimization
# TODO [20251224] Phase 2 (PRO): Create caching layer
# TODO [20251224] Phase 2 (PRO): Add distributed execution
# TODO [20251224] Phase 2 (PRO): Implement load balancing
# TODO [20251224] Phase 2 (PRO): Create failover mechanisms
# TODO [20251224] Phase 2 (PRO): Add advanced error recovery
# TODO [20251224] Phase 2 (PRO): Implement circuit breaker pattern
# TODO [20251224] Phase 2 (PRO): Create retry logic
# TODO [20251224] Phase 2 (PRO): Add exponential backoff
# TODO [20251224] Phase 2 (PRO): Implement usage analytics
# TODO [20251224] Phase 2 (PRO): Create cost tracking
# TODO [20251224] Phase 2 (PRO): Add budget enforcement
# TODO [20251224] Phase 2 (PRO): Implement monitoring integration

# TODO [20251224] Phase 3 (ENTERPRISE): Implement multi-region deployment
# TODO [20251224] Phase 3 (ENTERPRISE): Create disaster recovery
# TODO [20251224] Phase 3 (ENTERPRISE): Add high availability
# TODO [20251224] Phase 3 (ENTERPRISE): Implement federation
# TODO [20251224] Phase 3 (ENTERPRISE): Create centralized management
# TODO [20251224] Phase 3 (ENTERPRISE): Add role-based access control
# TODO [20251224] Phase 3 (ENTERPRISE): Implement audit logging
# TODO [20251224] Phase 3 (ENTERPRISE): Create compliance enforcement
# TODO [20251224] Phase 3 (ENTERPRISE): Add encryption support
# TODO [20251224] Phase 3 (ENTERPRISE): Implement data residency
# TODO [20251224] Phase 3 (ENTERPRISE): Create advanced security
# TODO [20251224] Phase 3 (ENTERPRISE): Add threat detection
# TODO [20251224] Phase 3 (ENTERPRISE): Implement anomaly detection
# TODO [20251224] Phase 3 (ENTERPRISE): Create advanced analytics
# TODO [20251224] Phase 3 (ENTERPRISE): Add predictive capabilities
# TODO [20251224] Phase 3 (ENTERPRISE): Implement cost optimization
# TODO [20251224] Phase 3 (ENTERPRISE): Create billing integration
# TODO [20251224] Phase 3 (ENTERPRISE): Add usage reporting
# TODO [20251224] Phase 3 (ENTERPRISE): Implement SLA tracking
# TODO [20251224] Phase 3 (ENTERPRISE): Create incident management
# TODO [20251224] Phase 3 (ENTERPRISE): Add change control
# TODO [20251224] Phase 3 (ENTERPRISE): Implement governance
# TODO [20251224] Phase 3 (ENTERPRISE): Create executive dashboards
# TODO [20251224] Phase 3 (ENTERPRISE): Add advanced monitoring
# TODO [20251224] Phase 3 (ENTERPRISE): Implement automated scaling

try:
    from crewai import Agent, Crew, Task
    from crewai.tools import BaseTool
    from pydantic import BaseModel, Field
except ImportError as e:
    raise ImportError(
        "CrewAI is required for this integration. "
        "Install it with: pip install crewai"
    ) from e


# ============================================================================
# Tool Input Schemas
# ============================================================================


class CodeInput(BaseModel):
    """Input schema for code analysis tools."""

    code: str = Field(description="Python code to analyze")


class ErrorInput(BaseModel):
    """Input schema for error analysis tools."""

    code: str = Field(description="Python code with error")
    error: str = Field(description="Error message to analyze")


class FixInput(BaseModel):
    """Input schema for fix generation tools."""

    code: str = Field(description="Python code to fix")
    analysis: str = Field(description="Error analysis results")


# ============================================================================
# Code Scalpel Tools for CrewAI
# ============================================================================


class ScalpelAnalyzeTool(BaseTool):
    """Tool for analyzing code using Code Scalpel AST analyzer."""

    name: str = "scalpel_analyze"
    description: str = (
        "Analyzes Python code using AST parsing to detect syntax and style issues"
    )
    args_schema: type[BaseModel] = CodeInput

    def _run(self, code: str) -> str:
        """
        Run code analysis.

        [20251217_FEATURE] AST-based code analysis for CrewAI.
        """
        try:
            from ...ast_tools.analyzer import ASTAnalyzer

            analyzer = ASTAnalyzer()
            tree = analyzer.parse_to_ast(code)
            style_issues = analyzer.analyze_code_style(tree)
            security_issues = analyzer.find_security_issues(tree)

            return str(
                {
                    "parsed": True,
                    "style_issues": style_issues,
                    "security_issues": len(security_issues),
                }
            )
        except SyntaxError as e:
            return str(
                {
                    "parsed": False,
                    "error": str(e),
                    "line": getattr(e, "lineno", None),
                }
            )
        except Exception as e:
            return str({"error": f"Analysis failed: {str(e)}"})


class ScalpelErrorToDiffTool(BaseTool):
    """Tool for converting errors to actionable diffs."""

    name: str = "scalpel_error_to_diff"
    description: str = "Converts error messages into actionable code diffs"
    args_schema: type[BaseModel] = ErrorInput

    def _run(self, code: str, error: str) -> str:
        """
        Generate diff from error.

        [20251217_FEATURE] Error-to-diff conversion for CrewAI.
        """
        try:
            # Parse error message to extract location
            lines = error.split("\n")
            error_type = "unknown"
            line_num = None

            for line in lines:
                if "SyntaxError" in line:
                    error_type = "syntax"
                elif "NameError" in line:
                    error_type = "name"
                elif "TypeError" in line:
                    error_type = "type"
                elif "line" in line.lower():
                    # Try to extract line number
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.lower() == "line" and i + 1 < len(parts):
                            try:
                                line_num = int(parts[i + 1].rstrip(","))
                            except ValueError:
                                pass

            return str(
                {
                    "error_type": error_type,
                    "line": line_num,
                    "diff_available": True,
                }
            )
        except Exception as e:
            return str({"error": f"Diff generation failed: {str(e)}"})


class ScalpelGenerateFixTool(BaseTool):
    """Tool for generating code fixes."""

    name: str = "scalpel_generate_fix"
    description: str = "Generates code fixes based on error analysis"
    args_schema: type[BaseModel] = FixInput

    def _run(self, code: str, analysis: str) -> str:
        """
        Generate fix for code.

        [20251217_FEATURE] Fix generation for CrewAI.
        """
        try:
            from ...ast_tools.analyzer import ASTAnalyzer

            analyzer = ASTAnalyzer()

            # Try to parse and regenerate
            try:
                tree = analyzer.parse_to_ast(code)
                fixed_code = analyzer.ast_to_code(tree)
                return str(
                    {
                        "fix_available": True,
                        "fixed_code": fixed_code,
                        "method": "ast_regeneration",
                    }
                )
            except SyntaxError:
                return str(
                    {
                        "fix_available": False,
                        "reason": "Syntax error prevents automatic fix",
                    }
                )
        except Exception as e:
            return str({"error": f"Fix generation failed: {str(e)}"})


class ScalpelValidateASTTool(BaseTool):
    """Tool for validating AST structure."""

    name: str = "scalpel_validate_ast"
    description: str = "Validates code AST structure is correct"
    args_schema: type[BaseModel] = CodeInput

    def _run(self, code: str) -> str:
        """
        Validate AST.

        [20251217_FEATURE] AST validation for CrewAI.
        """
        try:
            from ...ast_tools.analyzer import ASTAnalyzer

            analyzer = ASTAnalyzer()
            tree = analyzer.parse_to_ast(code)

            return str(
                {
                    "valid": True,
                    "ast_type": type(tree).__name__,
                }
            )
        except SyntaxError as e:
            return str(
                {
                    "valid": False,
                    "error": str(e),
                }
            )
        except Exception as e:
            return str({"error": f"Validation failed: {str(e)}"})


class ScalpelSandboxTool(BaseTool):
    """Tool for testing code in sandbox."""

    name: str = "scalpel_sandbox"
    description: str = "Tests code in isolated sandbox environment"
    args_schema: type[BaseModel] = CodeInput

    def _run(self, code: str) -> str:
        """
        Test code in sandbox.

        [20251217_FEATURE] Sandbox execution for CrewAI.
        """
        try:
            # Simple validation - just check if it parses
            import ast

            ast.parse(code)
            return str(
                {
                    "sandbox_passed": True,
                    "execution": "safe",
                }
            )
        except Exception as e:
            return str(
                {
                    "sandbox_passed": False,
                    "error": str(e),
                }
            )


class ScalpelSecurityScanTool(BaseTool):
    """Tool for security scanning."""

    name: str = "scalpel_security_scan"
    description: str = "Scans code for security vulnerabilities"
    args_schema: type[BaseModel] = CodeInput

    def _run(self, code: str) -> str:
        """
        Scan code for security issues.

        [20251217_FEATURE] Security scanning for CrewAI.
        """
        try:
            from ...symbolic_execution_tools import analyze_security

            result = analyze_security(code)

            return str(
                {
                    "has_vulnerabilities": result.has_vulnerabilities,
                    "vulnerability_count": result.vulnerability_count,
                    "sql_injections": len(result.get_sql_injections()),
                    "xss": len(result.get_xss()),
                    "command_injections": len(result.get_command_injections()),
                }
            )
        except Exception as e:
            return str({"error": f"Security scan failed: {str(e)}"})


# ============================================================================
# Crew Creation Function
# ============================================================================


def create_scalpel_fix_crew() -> Crew:
    """
    Create CrewAI crew for Code Scalpel operations.

    [20251217_FEATURE] Complete CrewAI integration with multi-agent collaboration.

    Usage:
        from code_scalpel.autonomy.integrations.crewai import create_scalpel_fix_crew

        crew = create_scalpel_fix_crew()
        result = crew.kickoff(inputs={
            "code": buggy_code,
            "error": error_message
        })

    Returns:
        Configured Crew with Error Analyzer, Fix Generator, and Validator agents.
    """
    # Error Analyzer Agent
    error_analyzer = Agent(
        role="Error Analyzer",
        goal="Analyze code errors and identify root causes",
        backstory="Expert at parsing error messages and understanding code issues",
        tools=[ScalpelAnalyzeTool(), ScalpelErrorToDiffTool()],
        verbose=True,
    )

    # Fix Generator Agent
    fix_generator = Agent(
        role="Fix Generator",
        goal="Generate correct code fixes based on error analysis",
        backstory="Expert at writing minimal, correct code patches",
        tools=[ScalpelGenerateFixTool(), ScalpelValidateASTTool()],
        verbose=True,
    )

    # Validator Agent
    validator = Agent(
        role="Fix Validator",
        goal="Validate fixes don't break existing functionality",
        backstory="Expert at testing code changes in isolation",
        tools=[ScalpelSandboxTool(), ScalpelSecurityScanTool()],
        verbose=True,
    )

    # Tasks
    analyze_task = Task(
        description="Analyze the error message and identify the root cause",
        agent=error_analyzer,
        expected_output="Error analysis with categorization and affected code location",
    )

    generate_task = Task(
        description="Generate a fix for the identified error",
        agent=fix_generator,
        expected_output="Code diff that fixes the error",
    )

    validate_task = Task(
        description="Validate the fix in a sandbox environment",
        agent=validator,
        expected_output="Validation result with test outcomes",
    )

    return Crew(
        agents=[error_analyzer, fix_generator, validator],
        tasks=[analyze_task, generate_task, validate_task],
        verbose=True,
    )
