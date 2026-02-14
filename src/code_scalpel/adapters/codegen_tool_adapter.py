"""
Codegen Tool Adapter

Base class for wrapping Codegen LangChain tools as MCP tools with tier-based access control.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging
import time

from code_scalpel.core.codegen_bridge import Tier
from code_scalpel.session.codebase_manager import get_session_manager, SessionContext

logger = logging.getLogger(__name__)


class ToolResult:
    """Result from tool execution"""
    
    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }


class CodegenToolAdapter(ABC):
    """
    Base class for adapting Codegen tools to MCP.
    
    Responsibilities:
    - Tier-based access control
    - Parameter validation
    - Error translation
    - Transaction wrapping (optional)
    - Invocation logging
    """
    
    def __init__(
        self,
        name: str,
        tier: Tier,
        requires_transaction: bool = False,
        description: Optional[str] = None
    ):
        """
        Initialize tool adapter.
        
        Args:
            name: Tool name
            tier: Required access tier
            requires_transaction: Whether tool requires transaction
            description: Tool description
        """
        self.name = name
        self.tier = tier
        self.requires_transaction = requires_transaction
        self.description = description or f"Codegen tool: {name}"
        self._session_manager = get_session_manager()
    
    def execute(
        self,
        session_id: str,
        user_tier: Tier,
        **kwargs
    ) -> ToolResult:
        """
        Execute the tool.
        
        Args:
            session_id: MCP session identifier
            user_tier: User's access tier
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
        """
        start_time = time.time()
        
        try:
            # 1. Check tier access
            if not self._check_tier_access(user_tier):
                return ToolResult(
                    success=False,
                    error=f"Access denied. Tool '{self.name}' requires {self.tier.value} tier, "
                          f"but user has {user_tier.value} tier."
                )
            
            # 2. Validate parameters
            validation_error = self._validate_parameters(**kwargs)
            if validation_error:
                return ToolResult(
                    success=False,
                    error=f"Parameter validation failed: {validation_error}"
                )
            
            # 3. Get session
            session = self._session_manager.get_session(session_id)
            if session is None:
                return ToolResult(
                    success=False,
                    error=f"Session {session_id} not found"
                )
            
            # 4. Execute with optional transaction
            if self.requires_transaction:
                result = self._execute_with_transaction(session, **kwargs)
            else:
                result = self._execute_impl(session, **kwargs)
            
            # 5. Log invocation
            duration = time.time() - start_time
            self._log_invocation(session_id, result.success, duration)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error executing tool '{self.name}' in session {session_id}: {e}",
                exc_info=True
            )
            self._log_invocation(session_id, False, duration)
            return ToolResult(
                success=False,
                error=self._translate_error(e)
            )
    
    def _check_tier_access(self, user_tier: Tier) -> bool:
        """
        Check if user has required tier access.
        
        Args:
            user_tier: User's access tier
            
        Returns:
            True if access granted
        """
        tier_hierarchy = {
            Tier.COMMUNITY: 0,
            Tier.PRO: 1,
            Tier.ENTERPRISE: 2
        }
        return tier_hierarchy[user_tier] >= tier_hierarchy[self.tier]
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        """
        Validate tool parameters.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Error message if validation fails, None otherwise
        """
        # Override in subclasses for specific validation
        return None
    
    def _execute_with_transaction(
        self,
        session: SessionContext,
        **kwargs
    ) -> ToolResult:
        """
        Execute tool within a transaction.
        
        Args:
            session: Session context
            **kwargs: Tool parameters
            
        Returns:
            Tool result
        """
        transaction_manager = self._get_transaction_manager(session)
        if transaction_manager is None:
            return ToolResult(
                success=False,
                error="Transaction manager not available"
            )
        
        try:
            # Begin transaction
            transaction_manager.begin()
            
            # Execute tool
            result = self._execute_impl(session, **kwargs)
            
            # Commit if successful
            if result.success:
                transaction_manager.commit()
            else:
                transaction_manager.rollback()
            
            return result
            
        except Exception as e:
            # Rollback on error
            try:
                transaction_manager.rollback()
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")
            raise
    
    def _get_transaction_manager(self, session: SessionContext) -> Optional[Any]:
        """Get transaction manager from session"""
        try:
            from code_scalpel.core.codegen_bridge import get_bridge
            bridge = get_bridge()
            return bridge.get_transaction_manager(session.codebase)
        except Exception as e:
            logger.error(f"Failed to get transaction manager: {e}")
            return None
    
    @abstractmethod
    def _execute_impl(
        self,
        session: SessionContext,
        **kwargs
    ) -> ToolResult:
        """
        Implement tool-specific execution logic.
        
        Args:
            session: Session context
            **kwargs: Tool parameters
            
        Returns:
            Tool result
        """
        pass
    
    def _translate_error(self, exception: Exception) -> str:
        """
        Translate exception to user-friendly error message.
        
        Args:
            exception: Exception to translate
            
        Returns:
            Error message
        """
        # Basic translation - override for specific error types
        error_type = type(exception).__name__
        error_msg = str(exception)
        return f"{error_type}: {error_msg}"
    
    def _log_invocation(
        self,
        session_id: str,
        success: bool,
        duration: float
    ):
        """
        Log tool invocation.
        
        Args:
            session_id: Session identifier
            success: Whether execution succeeded
            duration: Execution duration in seconds
        """
        logger.info(
            f"Tool '{self.name}' executed in session {session_id}: "
            f"success={success}, duration={duration:.3f}s"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get tool schema for MCP.
        
        Returns:
            Tool schema dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "tier": self.tier.value,
            "requires_transaction": self.requires_transaction,
            "parameters": self._get_parameter_schema()
        }
    
    @abstractmethod
    def _get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get parameter schema for the tool.
        
        Returns:
            Parameter schema dictionary
        """
        pass

