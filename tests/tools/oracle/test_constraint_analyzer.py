"""Test suite for ConstraintAnalyzer.

Tests graph-based architectural constraint analysis.
"""

from unittest.mock import MagicMock

from code_scalpel.oracle.constraint_analyzer import ConstraintAnalyzer
from code_scalpel.oracle.models import TopologyRule


class MockGraph:
    """Mock UniversalGraph for testing."""

    def __init__(self, predecessors_map=None, successors_map=None, cycles_map=None):
        """Initialize mock graph."""
        self.predecessors_map = predecessors_map or {}
        self.successors_map = successors_map or {}
        self.cycles_map = cycles_map or {}

    def predecessors(self, node):
        """Get predecessors of a node."""
        return self.predecessors_map.get(node, [])

    def successors(self, node):
        """Get successors of a node."""
        return self.successors_map.get(node, [])

    def find_cycles(self):
        """Find cycles in the graph."""
        return self.cycles_map.get("cycles", [])


class TestConstraintAnalyzer:
    """Test cases for ConstraintAnalyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ConstraintAnalyzer()

    def test_analyze_file_no_graph(self):
        """Test analyzing a file without a graph returns basic constraints."""
        constraints = self.analyzer.analyze_file("src/auth.py")

        assert constraints is not None
        assert constraints.file_path == "src/auth.py"
        assert constraints.callers == []
        assert constraints.callees == []
        assert constraints.circular_dependencies == []
        assert constraints.depth == 5  # Default depth

    def test_analyze_file_with_graph(self):
        """Test analyzing a file with graph data."""
        graph = MockGraph(
            predecessors_map={"src/auth.py": ["src/routes.py", "src/services.py"]},
            successors_map={"src/auth.py": ["src/utils.py", "src/models.py"]},
        )

        constraints = self.analyzer.analyze_file("src/auth.py", graph=graph)

        assert constraints.file_path == "src/auth.py"
        assert len(constraints.callers) == 2
        assert "src/routes.py" in constraints.callers
        assert "src/services.py" in constraints.callers
        assert len(constraints.callees) == 2
        assert "src/utils.py" in constraints.callees
        assert "src/models.py" in constraints.callees

    def test_analyze_file_with_circular_dependencies(self):
        """Test analyzing a file with circular dependencies."""
        cycles = [
            ["src/auth.py", "src/models.py", "src/services.py"],
            ["src/cache.py", "src/db.py"],
        ]
        graph = MockGraph(cycles_map={"cycles": cycles})

        constraints = self.analyzer.analyze_file("src/auth.py", graph=graph)

        assert constraints.file_path == "src/auth.py"
        assert len(constraints.circular_dependencies) == 2
        assert "src/models.py" in constraints.circular_dependencies
        assert "src/services.py" in constraints.circular_dependencies

    def test_analyze_file_custom_depth(self):
        """Test analyzing with custom max depth."""
        constraints = self.analyzer.analyze_file("src/auth.py", max_depth=10)

        assert constraints.depth == 10

    def test_get_callers(self):
        """Test getting callers (inbound edges)."""
        graph = MockGraph(
            predecessors_map={
                "src/auth.py": ["src/routes.py", "src/api.py", "src/cli.py"]
            }
        )

        callers = self.analyzer._get_callers("src/auth.py", graph)

        assert len(callers) == 3
        assert "src/routes.py" in callers
        assert "src/api.py" in callers
        assert "src/cli.py" in callers

    def test_get_callers_no_predecessors(self):
        """Test getting callers when there are none."""
        graph = MockGraph(predecessors_map={})

        callers = self.analyzer._get_callers("src/auth.py", graph)

        assert callers == []

    def test_get_callers_no_graph_method(self):
        """Test handling graph without predecessors method."""
        graph = MagicMock(spec=[])

        callers = self.analyzer._get_callers("src/auth.py", graph)

        assert callers == []

    def test_get_callees(self):
        """Test getting callees (outbound edges)."""
        graph = MockGraph(
            successors_map={
                "src/auth.py": ["src/utils.py", "src/models.py", "src/db.py"]
            }
        )

        callees = self.analyzer._get_callees("src/auth.py", graph)

        assert len(callees) == 3
        assert "src/utils.py" in callees
        assert "src/models.py" in callees
        assert "src/db.py" in callees

    def test_get_callees_no_successors(self):
        """Test getting callees when there are none."""
        graph = MockGraph(successors_map={})

        callees = self.analyzer._get_callees("src/auth.py", graph)

        assert callees == []

    def test_detect_circular_dependencies(self):
        """Test detecting circular dependencies."""
        cycles = [
            ["src/auth.py", "src/models.py", "src/services.py"],
            ["src/utils.py", "src/validators.py"],
        ]
        graph = MockGraph(cycles_map={"cycles": cycles})

        circular = self.analyzer._detect_circular_dependencies("src/auth.py", graph)

        assert len(circular) == 2
        assert "src/models.py" in circular
        assert "src/services.py" in circular
        # File itself should not be in the list
        assert "src/auth.py" not in circular

    def test_detect_circular_dependencies_file_not_in_cycle(self):
        """Test when file is not in any cycle."""
        cycles = [["src/utils.py", "src/validators.py"]]
        graph = MockGraph(cycles_map={"cycles": cycles})

        circular = self.analyzer._detect_circular_dependencies("src/auth.py", graph)

        assert circular == []

    def test_detect_circular_dependencies_no_find_cycles_method(self):
        """Test handling graph without find_cycles method."""
        graph = MagicMock(spec=[])

        circular = self.analyzer._detect_circular_dependencies("src/auth.py", graph)

        assert circular == []

    def test_add_topology_rule(self):
        """Test adding a topology rule."""
        rule = TopologyRule(
            name="no-views-to-utils",
            description="Views cannot import utils",
            from_layer="src/views",
            to_layer="src/utils",
            action="DENY",
            severity="HIGH",
        )

        self.analyzer.add_topology_rule(rule)

        assert "no-views-to-utils" in self.analyzer.topology_rules
        assert self.analyzer.topology_rules["no-views-to-utils"] == rule

    def test_check_topology_violations_no_violations(self):
        """Test checking topology when no violations occur."""
        rule = TopologyRule(
            name="no-views-to-utils",
            description="Views cannot import utils",
            from_layer="src/views",
            to_layer="src/utils",
            action="DENY",
            severity="HIGH",
        )
        self.analyzer.add_topology_rule(rule)

        # File is in views, but imports from services (not utils)
        violations = self.analyzer.check_topology_violations(
            "src/views/dashboard.py",
            ["src/services/auth.py"],
            [rule],
        )

        assert violations == []

    def test_check_topology_violations_with_violations(self):
        """Test checking topology when violations exist."""
        rule = TopologyRule(
            name="no-views-to-utils",
            description="Views cannot import utils",
            from_layer="src/views",
            to_layer="src/utils",
            action="DENY",
            severity="HIGH",
        )

        # File is in views, imports from utils
        violations = self.analyzer.check_topology_violations(
            "src/views/dashboard.py",
            ["src/utils/helpers.py"],
            [rule],
        )

        assert len(violations) == 1
        assert violations[0].source_file == "src/views/dashboard.py"
        assert violations[0].target_file == "src/utils/helpers.py"
        assert violations[0].violation_type == "import"
        assert violations[0].rule == rule

    def test_check_topology_violations_multiple_violations(self):
        """Test checking topology with multiple violations."""
        rule = TopologyRule(
            name="no-views-to-utils",
            description="Views cannot import utils",
            from_layer="src/views",
            to_layer="src/utils",
            action="DENY",
            severity="HIGH",
        )

        violations = self.analyzer.check_topology_violations(
            "src/views/dashboard.py",
            ["src/utils/helpers.py", "src/utils/validators.py", "src/services/auth.py"],
            [rule],
        )

        assert len(violations) == 2
        # Only utils imports should violate
        assert all(v.target_file.startswith("src/utils") for v in violations)

    def test_check_topology_violations_allow_action(self):
        """Test that ALLOW rules don't generate violations."""
        rule = TopologyRule(
            name="allow-views-to-services",
            description="Views can import services",
            from_layer="src/views",
            to_layer="src/services",
            action="ALLOW",
            severity="LOW",
        )

        violations = self.analyzer.check_topology_violations(
            "src/views/dashboard.py",
            ["src/services/auth.py"],
            [rule],
        )

        assert violations == []

    def test_check_topology_violations_no_rules(self):
        """Test checking topology with no rules defined."""
        violations = self.analyzer.check_topology_violations(
            "src/views/dashboard.py",
            ["src/utils/helpers.py"],
        )

        assert violations == []

    def test_matches_pattern_direct_prefix(self):
        """Test pattern matching with direct prefix."""
        assert ConstraintAnalyzer._matches_pattern(
            "src/views/dashboard.py", "src/views"
        )
        assert ConstraintAnalyzer._matches_pattern("src/views/home.py", "src/views")
        assert not ConstraintAnalyzer._matches_pattern(
            "src/utils/helpers.py", "src/views"
        )

    def test_matches_pattern_glob(self):
        """Test pattern matching with glob patterns."""
        assert ConstraintAnalyzer._matches_pattern(
            "src/views/dashboard.py", "src/views/*"
        )
        assert ConstraintAnalyzer._matches_pattern("src/views/home.py", "src/views/*")
        assert not ConstraintAnalyzer._matches_pattern(
            "src/utils/helpers.py", "src/views/*"
        )

    def test_load_governance_rules_no_config(self):
        """Test loading governance rules with no config."""
        self.analyzer.load_governance_rules({})

        assert self.analyzer.topology_rules == {}

    def test_load_governance_rules_empty_config(self):
        """Test loading governance rules with empty config."""
        self.analyzer.load_governance_rules({})

        assert self.analyzer.topology_rules == {}

    def test_load_governance_rules_from_config(self):
        """Test loading governance rules from configuration."""
        governance_config = {
            "oracle": {
                "graph_constraints": {
                    "forbidden_edges": [
                        {
                            "from": "src/views",
                            "to": "src/utils",
                            "name": "no-views-to-utils",
                            "reason": "Views should not import utilities",
                            "action": "DENY",
                            "severity": "HIGH",
                        },
                        {
                            "from": "src/models",
                            "to": "src/views",
                            "name": "no-models-to-views",
                            "reason": "Models should not depend on views",
                            "action": "DENY",
                            "severity": "CRITICAL",
                        },
                    ]
                }
            }
        }

        self.analyzer.load_governance_rules(governance_config)

        assert len(self.analyzer.topology_rules) == 2
        assert "no-views-to-utils" in self.analyzer.topology_rules
        assert "no-models-to-views" in self.analyzer.topology_rules

        rule1 = self.analyzer.topology_rules["no-views-to-utils"]
        assert rule1.from_layer == "src/views"
        assert rule1.to_layer == "src/utils"
        assert rule1.severity == "HIGH"

    def test_load_governance_rules_with_defaults(self):
        """Test loading governance rules with default values."""
        governance_config = {
            "oracle": {
                "graph_constraints": {
                    "forbidden_edges": [
                        {
                            "from": "src/views",
                            "to": "src/db",
                            # Missing: name, reason, action, severity
                        }
                    ]
                }
            }
        }

        self.analyzer.load_governance_rules(governance_config)

        assert len(self.analyzer.topology_rules) == 1
        rule = list(self.analyzer.topology_rules.values())[0]
        assert rule.name == "src/views->src/db"  # Default name
        assert rule.action == "DENY"  # Default action
        assert rule.severity == "HIGH"  # Default severity
        assert rule.description == "Architectural boundary violation"  # Default

    def test_constraint_analyzer_error_handling(self):
        """Test that analyzer handles exceptions gracefully."""
        # Create a graph that raises an exception
        graph = MagicMock()
        graph.predecessors.side_effect = RuntimeError("Graph query failed")

        constraints = self.analyzer.analyze_file("src/auth.py", graph=graph)

        # Should return basic constraints despite error
        assert constraints.file_path == "src/auth.py"
        assert constraints.callers == []

    def test_analyze_file_with_governance_config(self):
        """Test analyzing with governance configuration."""
        graph = MockGraph(
            predecessors_map={"src/auth.py": ["src/views.py"]},
        )
        governance_config = {
            "oracle": {
                "graph_constraints": {
                    "forbidden_edges": [
                        {
                            "from": "src/views.py",
                            "to": "src/auth.py",
                            "action": "DENY",
                        }
                    ]
                }
            }
        }

        constraints = self.analyzer.analyze_file(
            "src/auth.py",
            graph=graph,
            governance_config=governance_config,
        )

        assert constraints.file_path == "src/auth.py"
        assert len(constraints.callers) == 1
