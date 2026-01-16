"""
Base agent framework for AI agents using Code Scalpel MCP tools.

This module provides the foundation for building AI agents that leverage Code Scalpel's
surgical code analysis and modification capabilities. Agents follow the OODA loop:
Observe → Orient → Decide → Act.

The base agent provides:
- MCP tool integration
- Context management
- Error handling
- Logging and telemetry
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# Import MCP tools for agent use
from code_scalpel.mcp.tools.context import get_file_context, get_symbol_references
from code_scalpel.mcp.tools.extraction import extract_code, update_symbol
from code_scalpel.mcp.tools.symbolic import simulate_refactor


class AgentContext:
    """Context information for agent operations."""

    def __init__(self):
        self.workspace_root: Optional[str] = None
        self.current_file: Optional[str] = None
        self.recent_operations: List[Dict[str, Any]] = []
        self.knowledge_base: Dict[str, Any] = {}

        # TODO [COMMUNITY]: Phase 1 - Core Context Management (25 items, 20 tests each)
        # Purpose: Establish robust context tracking and basic persistence
        # TODO [COMMUNITY]: Add context persistence to file/database (SQLite, JSON)
        # TODO [COMMUNITY]: Add context versioning and rollback support
        # TODO [COMMUNITY]: Add knowledge_base serialization for learning across sessions
        # TODO [COMMUNITY]: Implement context compression for large histories
        # TODO [COMMUNITY]: Add context cleanup and pruning strategies
        # TODO [COMMUNITY]: Create context query and search capabilities
        # TODO [COMMUNITY]: Implement context indexing for fast retrieval
        # TODO [COMMUNITY]: Add context statistics and analytics
        # TODO [COMMUNITY]: Create context visualization tools
        # TODO [COMMUNITY]: Implement context validation and integrity checks
        # TODO [COMMUNITY]: Add context migration utilities
        # TODO [COMMUNITY]: Create context backup and restore
        # TODO [COMMUNITY]: Implement context export to multiple formats
        # TODO [COMMUNITY]: Add context import from external sources
        # TODO [COMMUNITY]: Create context merging and consolidation
        # TODO [COMMUNITY]: Implement context diff and comparison
        # TODO [COMMUNITY]: Add context tagging and categorization
        # TODO [COMMUNITY]: Create context filtering and selection
        # TODO [COMMUNITY]: Implement context priority management
        # TODO [COMMUNITY]: Add context expiration and TTL
        # TODO [COMMUNITY]: Create context access control
        # TODO [COMMUNITY]: Implement context audit logging
        # TODO [COMMUNITY]: Add context metrics and monitoring
        # TODO [COMMUNITY]: Create context testing utilities
        # TODO [COMMUNITY]: Implement context documentation generation

        # TODO [PRO]: Phase 2 - Advanced Context Features (25 items, 25 tests each)
        # Purpose: Add intelligent context management and learning capabilities
        # TODO [PRO]: Implement context-aware recommendations
        # TODO [PRO]: Add ML-based context relevance scoring
        # TODO [PRO]: Create context summarization and abstraction
        # TODO [PRO]: Implement semantic context search
        # TODO [PRO]: Add context clustering and grouping
        # TODO [PRO]: Create context pattern recognition
        # TODO [PRO]: Implement context anomaly detection
        # TODO [PRO]: Add context prediction and forecasting
        # TODO [PRO]: Create context dependency tracking
        # TODO [PRO]: Implement context impact analysis
        # TODO [PRO]: Add cross-session context correlation
        # TODO [PRO]: Create context-based debugging assistance
        # TODO [PRO]: Implement context replay for testing
        # TODO [PRO]: Add context simulation capabilities
        # TODO [PRO]: Create context performance optimization
        # TODO [PRO]: Implement distributed context management
        # TODO [PRO]: Add context synchronization across agents
        # TODO [PRO]: Create context federation
        # TODO [PRO]: Implement context caching strategies
        # TODO [PRO]: Add context prefetching
        # TODO [PRO]: Create context streaming
        # TODO [PRO]: Implement context batching
        # TODO [PRO]: Add context compression algorithms
        # TODO [PRO]: Create context encryption
        # TODO [PRO]: Implement context access patterns analysis

        # TODO [ENTERPRISE]: Phase 3 - Enterprise Context Management (25 items, 30 tests each)
        # Purpose: Enterprise-grade context governance and compliance
        # TODO [ENTERPRISE]: Implement multi-tenant context isolation
        # TODO [ENTERPRISE]: Add context compliance tracking (SOX, GDPR)
        # TODO [ENTERPRISE]: Create context retention policies
        # TODO [ENTERPRISE]: Implement context data sovereignty
        # TODO [ENTERPRISE]: Add context encryption at rest and in transit
        # TODO [ENTERPRISE]: Create context key management integration
        # TODO [ENTERPRISE]: Implement context tokenization
        # TODO [ENTERPRISE]: Add context anonymization and pseudonymization
        # TODO [ENTERPRISE]: Create context PII detection and redaction
        # TODO [ENTERPRISE]: Implement context RBAC and ABAC
        # TODO [ENTERPRISE]: Add context fine-grained permissions
        # TODO [ENTERPRISE]: Create context delegation and impersonation
        # TODO [ENTERPRISE]: Implement context audit trail immutability
        # TODO [ENTERPRISE]: Add context digital signatures
        # TODO [ENTERPRISE]: Create context blockchain integration
        # TODO [ENTERPRISE]: Implement context provenance tracking
        # TODO [ENTERPRISE]: Add context lineage visualization
        # TODO [ENTERPRISE]: Create context impact assessment
        # TODO [ENTERPRISE]: Implement context risk scoring
        # TODO [ENTERPRISE]: Add context SLA monitoring
        # TODO [ENTERPRISE]: Create context disaster recovery
        # TODO [ENTERPRISE]: Implement context high availability
        # TODO [ENTERPRISE]: Add context geo-replication
        # TODO [ENTERPRISE]: Create context failover automation
        # TODO [ENTERPRISE]: Implement context capacity planning

    def add_operation(self, operation: str, result: Any, success: bool = True):
        """Record an operation and its result."""
        # [20251215_BUGFIX] Use a monotonic clock even when no asyncio loop is running
        try:
            timestamp = asyncio.get_running_loop().time()
        except RuntimeError:
            timestamp = time.monotonic()

        self.recent_operations.append(
            {
                "operation": operation,
                "result": result,
                "success": success,
                "timestamp": timestamp,
            }
        )

    def get_recent_context(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent operations for context."""
        return self.recent_operations[-limit:]


class BaseCodeAnalysisAgent(ABC):
    """
    Base class for AI agents that use Code Scalpel MCP tools.

    Agents should implement the OODA loop:
    1. Observe: Gather information about the codebase
    2. Orient: Analyze and understand the context
    3. Decide: Determine what actions to take
    4. Act: Execute changes safely
    """

    def __init__(self, workspace_root: Optional[str] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.context = AgentContext()
        self.workspace_root = workspace_root
        self._setup_logging()

    @property
    def workspace_root(self) -> Optional[str]:
        """[20260104_BUGFIX] Keep workspace_root accessible on the agent while syncing context."""
        return self.context.workspace_root

    @workspace_root.setter
    def workspace_root(self, value: Optional[str]) -> None:
        self.context.workspace_root = value

    def _setup_logging(self):
        """Setup logging for the agent."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f"%(asctime)s - {self.__class__.__name__} - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    # MCP Tool Integration Methods

    async def observe_file(self, file_path: str) -> Dict[str, Any]:
        """Observe a file using get_file_context tool."""
        try:
            result = await get_file_context(file_path)
            self.context.add_operation("observe_file", result, result.success)
            return result.model_dump()
        except Exception as e:
            self.logger.error(f"Failed to observe file {file_path}: {e}")
            self.context.add_operation("observe_file", str(e), False)
            return {"success": False, "error": str(e)}

    async def find_symbol_usage(
        self, symbol_name: str, project_root: Optional[str] = None
    ) -> Dict[str, Any]:
        """Find all usages of a symbol using get_symbol_references tool."""
        try:
            result = await get_symbol_references(symbol_name, project_root)
            self.context.add_operation("find_symbol_usage", result, result.success)
            return result.model_dump()
        except Exception as e:
            self.logger.error(f"Failed to find symbol {symbol_name}: {e}")
            self.context.add_operation("find_symbol_usage", str(e), False)
            return {"success": False, "error": str(e)}

    async def analyze_code_security(self, code: str) -> Dict[str, Any]:
        """Analyze code for security issues using security_scan tool."""
        try:
            from code_scalpel.mcp.tools.security import security_scan

            result = await security_scan(code)
            self.context.add_operation("analyze_security", result, True)
            return result.model_dump()
        except Exception as e:
            self.logger.error(f"Failed to analyze security: {e}")
            self.context.add_operation("analyze_security", str(e), False)
            return {"success": False, "error": str(e)}

    async def extract_function(
        self, file_path: str, function_name: str
    ) -> Dict[str, Any]:
        """Extract a specific function using extract_code tool."""
        try:
            result = await extract_code(file_path, "function", function_name)
            self.context.add_operation("extract_function", result, result.success)
            return result.model_dump()
        except Exception as e:
            self.logger.error(f"Failed to extract function {function_name}: {e}")
            self.context.add_operation("extract_function", str(e), False)
            return {"success": False, "error": str(e)}

    async def simulate_code_change(
        self, original_code: str, new_code: str
    ) -> Dict[str, Any]:
        """Simulate a code change to verify safety using simulate_refactor tool."""
        try:
            result = await simulate_refactor(original_code, new_code)
            self.context.add_operation("simulate_change", result, True)
            return result.model_dump()
        except Exception as e:
            self.logger.error(f"Failed to simulate change: {e}")
            self.context.add_operation("simulate_change", str(e), False)
            return {"success": False, "error": str(e)}

    async def apply_safe_change(
        self, file_path: str, target_type: str, target_name: str, new_code: str
    ) -> Dict[str, Any]:
        """Apply a safe code change using update_symbol tool."""
        try:
            result = await update_symbol(file_path, target_type, target_name, new_code)
            self.context.add_operation("apply_change", result, result.success)
            return result.model_dump()
        except Exception as e:
            self.logger.error(f"Failed to apply change: {e}")
            self.context.add_operation("apply_change", str(e), False)
            return {"success": False, "error": str(e)}

    # Abstract Methods for Agent Logic

    @abstractmethod
    async def observe(self, target: str) -> Dict[str, Any]:
        """Observe the target (file, function, etc.) and gather information."""
        pass

    @abstractmethod
    async def orient(self, observations: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze observations and build understanding."""
        pass

    @abstractmethod
    async def decide(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Decide what actions to take based on analysis."""
        pass

    @abstractmethod
    async def act(self, decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the decided actions safely."""
        pass

    # Main Agent Loop

    async def execute_ooda_loop(self, target: str) -> Dict[str, Any]:
        """
        Execute the complete OODA loop for a given target.

        Returns:
            Dict containing the results of each phase and overall success
        """
        # TODO [COMMUNITY]: Phase 1 - Core OODA Loop (25 items, 20 tests each)
        # Purpose: Implement robust OODA loop execution with safety guarantees
        # TODO [COMMUNITY]: Add loop timeout and graceful cancellation
        # TODO [COMMUNITY]: Add telemetry/metrics collection for agent performance
        # TODO [COMMUNITY]: Add circuit breaker pattern for external tool failures
        # TODO [COMMUNITY]: Implement loop state machine with clear transitions
        # TODO [COMMUNITY]: Add phase result validation
        # TODO [COMMUNITY]: Create phase retry logic with backoff
        # TODO [COMMUNITY]: Implement phase checkpoint saving
        # TODO [COMMUNITY]: Add phase rollback on failure
        # TODO [COMMUNITY]: Create phase dependency tracking
        # TODO [COMMUNITY]: Implement phase execution tracing
        # TODO [COMMUNITY]: Add phase performance profiling
        # TODO [COMMUNITY]: Create phase resource monitoring
        # TODO [COMMUNITY]: Implement phase error categorization
        # TODO [COMMUNITY]: Add phase logging and debugging
        # TODO [COMMUNITY]: Create phase audit trail
        # TODO [COMMUNITY]: Implement phase result caching
        # TODO [COMMUNITY]: Add phase result validation
        # TODO [COMMUNITY]: Create phase result enrichment
        # TODO [COMMUNITY]: Implement phase timeout enforcement
        # TODO [COMMUNITY]: Add phase cancellation handling
        # TODO [COMMUNITY]: Create phase failure recovery
        # TODO [COMMUNITY]: Implement phase health checks
        # TODO [COMMUNITY]: Add phase monitoring and alerting
        # TODO [COMMUNITY]: Create phase documentation generation
        # TODO [COMMUNITY]: Implement phase testing utilities

        # TODO [PRO]: Phase 2 - Advanced OODA Features (25 items, 25 tests each)
        # Purpose: Add intelligent loop optimization and advanced capabilities
        # TODO [PRO]: Support async phase execution with parallel processing
        # TODO [PRO]: Add human-in-the-loop approval gates before Act phase
        # TODO [PRO]: Implement adaptive phase timeout
        # TODO [PRO]: Add phase result streaming
        # TODO [PRO]: Create phase batching for efficiency
        # TODO [PRO]: Implement phase prioritization
        # TODO [PRO]: Add phase scheduling and queuing
        # TODO [PRO]: Create phase load balancing
        # TODO [PRO]: Implement phase resource allocation
        # TODO [PRO]: Add phase cost optimization
        # TODO [PRO]: Create phase performance tuning
        # TODO [PRO]: Implement phase A/B testing
        # TODO [PRO]: Add phase versioning
        # TODO [PRO]: Create phase migration support
        # TODO [PRO]: Implement phase composition and chaining
        # TODO [PRO]: Add conditional phase execution
        # TODO [PRO]: Create dynamic phase selection
        # TODO [PRO]: Implement phase skip logic
        # TODO [PRO]: Add phase early termination
        # TODO [PRO]: Create phase speculation and prefetching
        # TODO [PRO]: Implement phase memoization
        # TODO [PRO]: Add phase result aggregation
        # TODO [PRO]: Create multi-target OODA loop
        # TODO [PRO]: Implement nested OODA loops
        # TODO [PRO]: Add OODA loop composition patterns

        # TODO [ENTERPRISE]: Phase 3 - Enterprise OODA Orchestration (25 items, 30 tests each)
        # Purpose: Enterprise-grade OODA orchestration and governance
        # TODO [ENTERPRISE]: Implement distributed OODA loop execution
        # TODO [ENTERPRISE]: Add OODA loop federation
        # TODO [ENTERPRISE]: Create OODA loop orchestration across clusters
        # TODO [ENTERPRISE]: Implement OODA loop high availability
        # TODO [ENTERPRISE]: Add OODA loop disaster recovery
        # TODO [ENTERPRISE]: Create OODA loop geo-distribution
        # TODO [ENTERPRISE]: Implement OODA loop compliance tracking
        # TODO [ENTERPRISE]: Add OODA loop audit requirements
        # TODO [ENTERPRISE]: Create OODA loop policy enforcement
        # TODO [ENTERPRISE]: Implement OODA loop SLA monitoring
        # TODO [ENTERPRISE]: Add OODA loop contract verification
        # TODO [ENTERPRISE]: Create OODA loop liability tracking
        # TODO [ENTERPRISE]: Implement OODA loop provenance
        # TODO [ENTERPRISE]: Add OODA loop explainability
        # TODO [ENTERPRISE]: Create OODA loop bias detection
        # TODO [ENTERPRISE]: Implement OODA loop fairness evaluation
        # TODO [ENTERPRISE]: Add OODA loop security hardening
        # TODO [ENTERPRISE]: Create OODA loop penetration testing
        # TODO [ENTERPRISE]: Implement OODA loop vulnerability scanning
        # TODO [ENTERPRISE]: Add OODA loop threat modeling
        # TODO [ENTERPRISE]: Create OODA loop incident response
        # TODO [ENTERPRISE]: Implement OODA loop forensics support
        # TODO [ENTERPRISE]: Add OODA loop capacity planning
        # TODO [ENTERPRISE]: Create OODA loop scalability testing
        # TODO [ENTERPRISE]: Implement OODA loop performance benchmarking
        try:
            self.logger.info(f"Starting OODA loop for target: {target}")

            # Observe
            observations = await self.observe(target)
            if not observations.get("success", False):
                return {
                    "success": False,
                    "phase": "observe",
                    "error": observations.get("error"),
                }

            # Orient
            analysis = await self.orient(observations)
            if not analysis.get("success", False):
                return {
                    "success": False,
                    "phase": "orient",
                    "error": analysis.get("error"),
                }

            # Decide
            decisions = await self.decide(analysis)
            if not decisions.get("success", False):
                return {
                    "success": False,
                    "phase": "decide",
                    "error": decisions.get("error"),
                }

            # Act
            actions = await self.act(decisions)
            success = actions.get("success", False)

            result = {
                "success": success,
                "phases": {
                    "observe": observations,
                    "orient": analysis,
                    "decide": decisions,
                    "act": actions,
                },
                "context": self.context.get_recent_context(),
            }

            self.logger.info(f"OODA loop completed with success: {success}")
            return result

        except Exception as e:
            self.logger.error(f"OODA loop failed: {e}")
            return {"success": False, "error": str(e)}

    # Utility Methods

    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current agent context."""
        return {
            "workspace_root": self.context.workspace_root,
            "current_file": self.context.current_file,
            "recent_operations_count": len(self.context.recent_operations),
            "knowledge_base_keys": list(self.context.knowledge_base.keys()),
        }
