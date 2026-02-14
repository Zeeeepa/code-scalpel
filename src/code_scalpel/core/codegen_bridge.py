"""
Codegen Bridge Module

Provides a lightweight bridge to Codegen's core functionality.
"""

import sys
from pathlib import Path
from typing import Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Tier(Enum):
    """Access tier levels"""
    COMMUNITY = "community"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class CodegenBridge:
    """Bridge to Codegen functionality"""
    
    def __init__(self, codegen_path: Optional[Path] = None):
        self.codegen_path = codegen_path or self._find_codegen()
        self._codegen_available = False
        
        if self.codegen_path:
            self._initialize_codegen()
    
    def _find_codegen(self) -> Optional[Path]:
        """Attempt to find Codegen installation"""
        try:
            import codegen
            return Path(codegen.__file__).parent.parent
        except ImportError:
            possible_paths = [
                Path("/tmp/Zeeeepa/codegen/src"),
                Path.home() / "codegen" / "src",
            ]
            for path in possible_paths:
                if (path / "codegen" / "sdk").exists():
                    return path
        return None
    
    def _initialize_codegen(self):
        """Initialize Codegen components"""
        try:
            if str(self.codegen_path) not in sys.path:
                sys.path.insert(0, str(self.codegen_path))
            
            from codegen.sdk.codebase.codebase_context import Codebase
            self._codebase_class = Codebase
            self._codegen_available = True
            logger.info(f"Codegen initialized from {self.codegen_path}")
        except Exception as e:
            logger.error(f"Failed to initialize Codegen: {e}")
            self._codegen_available = False
    
    @property
    def is_available(self) -> bool:
        return self._codegen_available
    
    def create_codebase(self, workspace_path: Path, **kwargs) -> Any:
        if not self.is_available:
            raise RuntimeError("Codegen is not available")
        return self._codebase_class(workspace_path, **kwargs)


_bridge: Optional[CodegenBridge] = None


def get_bridge() -> CodegenBridge:
    global _bridge
    if _bridge is None:
        _bridge = CodegenBridge()
    return _bridge

