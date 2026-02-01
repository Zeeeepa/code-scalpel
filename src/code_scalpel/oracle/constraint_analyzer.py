"""Constraint analyzer for graph-based architectural constraints.

[20260126_FEATURE] Analyze dependencies and apply architectural rules.

Queries the UniversalGraph to extract:
- Callers (functions/files that call this file)
- Callees (functions/files that this file calls)
- Architectural violations (forbidden edges)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from code_scalpel.oracle.models import (
    GraphConstraints,
    TopologyRule,
    TopologyViolation,
)

logger = logging.getLogger(__name__)


class ConstraintAnalyzer:
    """Analyzes graphs and architectural constraints."""

    def __init__(self):
        """Initialize the analyzer."""
        self.topology_rules: Dict[str, TopologyRule] = {}

    def analyze_file(
        self,
        file_path: str,
        graph: Any = None,
        governance_config: Optional[Dict[str, Any]] = None,
        max_depth: int = 5,
    ) -> GraphConstraints:
        """Analyze constraints for a file.

        Args:
            file_path: Path to target file
            graph: UniversalGraph instance (optional)
            governance_config: Governance configuration (optional)
            max_depth: Maximum graph traversal depth

        Returns:
            GraphConstraints with dependencies and rules
        """
        constraints = GraphConstraints(file_path=file_path, depth=max_depth)

        # If no graph provided, return basic constraints
        if graph is None:
            logger.debug(
                f"No graph provided for {file_path}, returning basic constraints"
            )
            return constraints

        try:
            # Get callers (inbound edges)
            callers = self._get_callers(file_path, graph, max_depth)
            constraints.callers = callers

            # Get callees (outbound edges)
            callees = self._get_callees(file_path, graph, max_depth)
            constraints.callees = callees

            # Get circular dependencies
            circular = self._detect_circular_dependencies(file_path, graph)
            constraints.circular_dependencies = circular

        except Exception as e:
            logger.warning(f"Error analyzing graph for {file_path}: {e}")

        return constraints

    def _get_callers(
        self,
        file_path: str,
        graph: Any,
        max_depth: int = 1,
    ) -> List[str]:
        """Get inbound edges (who calls this file).

        Args:
            file_path: Target file path
            graph: UniversalGraph instance
            max_depth: Max traversal depth

        Returns:
            List of caller identifiers
        """
        callers = []

        try:
            # Try to get predecessors (inbound edges)
            if hasattr(graph, "predecessors"):
                for pred in graph.predecessors(file_path):
                    callers.append(str(pred))

        except Exception as e:
            logger.debug(f"Error getting callers for {file_path}: {e}")

        return callers

    def _get_callees(
        self,
        file_path: str,
        graph: Any,
        max_depth: int = 1,
    ) -> List[str]:
        """Get outbound edges (what this file calls).

        Args:
            file_path: Target file path
            graph: UniversalGraph instance
            max_depth: Max traversal depth

        Returns:
            List of callee identifiers
        """
        callees = []

        try:
            # Try to get successors (outbound edges)
            if hasattr(graph, "successors"):
                for succ in graph.successors(file_path):
                    callees.append(str(succ))

        except Exception as e:
            logger.debug(f"Error getting callees for {file_path}: {e}")

        return callees

    def _detect_circular_dependencies(
        self,
        file_path: str,
        graph: Any,
    ) -> List[str]:
        """Detect circular dependencies involving this file.

        Args:
            file_path: Target file path
            graph: UniversalGraph instance

        Returns:
            List of files in circular dependency
        """
        circular = []

        try:
            # Try to detect cycles using existing graph methods
            if hasattr(graph, "find_cycles"):
                cycles = graph.find_cycles()
                for cycle in cycles:
                    if file_path in cycle:
                        # Remove the file itself, keep others in cycle
                        other_files = [f for f in cycle if f != file_path]
                        circular.extend(other_files)

        except Exception as e:
            logger.debug(f"Error detecting cycles for {file_path}: {e}")

        return circular

    def add_topology_rule(self, rule: TopologyRule) -> None:
        """Register a topology rule.

        Args:
            rule: TopologyRule to register
        """
        self.topology_rules[rule.name] = rule

    def check_topology_violations(
        self,
        file_path: str,
        imported_files: List[str],
        topology_rules: Optional[List[TopologyRule]] = None,
    ) -> List[TopologyViolation]:
        """Check for architectural rule violations.

        Args:
            file_path: File being analyzed
            imported_files: Files being imported
            topology_rules: List of rules to check

        Returns:
            List of violations found
        """
        violations = []

        rules = topology_rules or list(self.topology_rules.values())

        for rule in rules:
            if rule.action != "DENY":
                continue

            # Check if file_path is in the "from" layer
            if self._matches_pattern(file_path, rule.from_layer):
                # Check if imported files are in the "to" layer
                for imported in imported_files:
                    if self._matches_pattern(imported, rule.to_layer):
                        violation = TopologyViolation(
                            rule=rule,
                            source_file=file_path,
                            target_file=imported,
                            violation_type="import",
                            message=f"Forbidden: {rule.name} - {file_path} imports {imported}",
                        )
                        violations.append(violation)

        return violations

    @staticmethod
    def _matches_pattern(file_path: str, pattern: str) -> bool:
        """Check if a file path matches a layer pattern.

        Args:
            file_path: File path to check
            pattern: Pattern like "src/views" or "src/views/*"

        Returns:
            True if matches
        """
        path = Path(file_path)

        # Handle glob patterns
        if pattern.endswith("/*"):
            base_pattern = pattern[:-2]  # Remove /*
            return str(path).startswith(base_pattern)

        # Direct prefix match
        return str(path).startswith(pattern)

    def load_governance_rules(
        self,
        governance_config: Dict[str, Any],
    ) -> None:
        """Load topology rules from governance configuration.

        Args:
            governance_config: Governance YAML config dict
        """
        if not governance_config:
            return

        oracle_config = governance_config.get("oracle", {})
        graph_config = oracle_config.get("graph_constraints", {})
        forbidden_edges = graph_config.get("forbidden_edges", [])

        for edge in forbidden_edges:
            rule = TopologyRule(
                name=edge.get("name", f"{edge['from']}->{edge['to']}"),
                description=edge.get("reason", "Architectural boundary violation"),
                from_layer=edge.get("from"),
                to_layer=edge.get("to"),
                action=edge.get("action", "DENY"),
                severity=edge.get("severity", "HIGH"),
            )
            self.add_topology_rule(rule)
