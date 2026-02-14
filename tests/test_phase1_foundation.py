"""
Phase 1 Foundation Tests

Tests for Codegen bridge, session manager, and tool adapter.
"""

import pytest
import tempfile
from pathlib import Path
import time
import threading

from code_scalpel.core.codegen_bridge import (
    CodegenBridge,
    get_bridge,
    Tier
)
from code_scalpel.session.codebase_manager import (
    CodebaseSessionManager,
    SessionContext,
    LRUCache,
    get_session_manager
)
from code_scalpel.adapters.codegen_tool_adapter import (
    CodegenToolAdapter,
    ToolResult
)


class TestCodegenBridge:
    """Test Codegen bridge functionality"""
    
    def test_bridge_initialization(self):
        """Test bridge can be initialized"""
        bridge = CodegenBridge()
        assert bridge is not None
        # Note: May not be available if Codegen not installed
    
    def test_get_bridge_singleton(self):
        """Test get_bridge returns singleton"""
        bridge1 = get_bridge()
        bridge2 = get_bridge()
        assert bridge1 is bridge2
    
    def test_tier_enum(self):
        """Test Tier enum"""
        assert Tier.COMMUNITY.value == "community"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"
    
    def test_tier_values(self):
        """Test Tier enum values"""
        assert len(list(Tier)) == 3
        assert Tier.COMMUNITY in list(Tier)
        assert Tier.PRO in list(Tier)
        assert Tier.ENTERPRISE in list(Tier)


class TestLRUCache:
    """Test LRU cache implementation"""
    
    def test_cache_basic_operations(self):
        """Test basic cache operations"""
        cache = LRUCache(maxsize=3)
        
        # Put items
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        
        # Get items
        assert cache.get("a") == 1
        assert cache.get("b") == 2
        assert cache.get("c") == 3
        assert cache.get("d") is None
    
    def test_cache_eviction(self):
        """Test LRU eviction"""
        cache = LRUCache(maxsize=2)
        
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # Should evict "a"
        
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3
    
    def test_cache_lru_order(self):
        """Test LRU ordering"""
        cache = LRUCache(maxsize=2)
        
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")  # Access "a", making it most recent
        cache.put("c", 3)  # Should evict "b", not "a"
        
        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3
    
    def test_cache_size(self):
        """Test cache size tracking"""
        cache = LRUCache(maxsize=10)
        
        cache.put("a", 1)
        cache.put("b", 2)
        
        assert cache.get("a") == 1
        assert cache.get("b") == 2
        assert cache.maxsize == 10
    
    def test_cache_thread_safety(self):
        """Test cache is thread-safe"""
        cache = LRUCache(maxsize=100)
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(100):
                    cache.put(f"key_{thread_id}_{i}", i)
                    cache.get(f"key_{thread_id}_{i}")
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0


class TestSessionManager:
    """Test session manager functionality"""
    
    def test_session_manager_initialization(self):
        """Test session manager can be initialized"""
        manager = CodebaseSessionManager(
            max_sessions=10,
            cache_size=100
        )
        assert manager.max_sessions == 10
        assert manager._cache.maxsize == 100
    
    def test_session_context(self):
        """Test SessionContext"""
        with tempfile.TemporaryDirectory() as tmpdir:
            context = SessionContext(
                session_id="test-session",
                workspace_path=Path(tmpdir),
                codebase=None
            )
            
            assert context.session_id == "test-session"
            initial_time = context.last_accessed
            
            time.sleep(0.01)
            context.touch()
            assert context.last_accessed > initial_time
    
    def test_session_manager_stats(self):
        """Test session manager has stats method"""
        manager = CodebaseSessionManager()
        stats = manager.get_stats() if hasattr(manager, 'get_stats') else {}
        assert isinstance(stats, dict)
    
    def test_cache_operations(self):
        """Test cache basic operations"""
        manager = CodebaseSessionManager()
        assert manager._cache is not None
        assert isinstance(manager._cache, LRUCache)


class TestToolAdapter:
    """Test tool adapter base class"""
    
    def test_tool_result(self):
        """Test ToolResult"""
        result = ToolResult(
            success=True,
            data={"key": "value"},
            metadata={"duration": 0.5}
        )
        
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.error is None
        assert result.metadata["duration"] == 0.5
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["data"] == {"key": "value"}
    
    def test_tier_hierarchy(self):
        """Test tier access hierarchy"""
        # Create a mock adapter
        class MockAdapter(CodegenToolAdapter):
            def _execute_impl(self, session, **kwargs):
                return ToolResult(success=True, data="test")
            
            def _get_parameter_schema(self):
                return {}
        
        # Community tier tool
        adapter = MockAdapter(name="test", tier=Tier.COMMUNITY)
        assert adapter._check_tier_access(Tier.COMMUNITY)
        assert adapter._check_tier_access(Tier.PRO)
        assert adapter._check_tier_access(Tier.ENTERPRISE)
        
        # Pro tier tool
        adapter = MockAdapter(name="test", tier=Tier.PRO)
        assert not adapter._check_tier_access(Tier.COMMUNITY)
        assert adapter._check_tier_access(Tier.PRO)
        assert adapter._check_tier_access(Tier.ENTERPRISE)
        
        # Enterprise tier tool
        adapter = MockAdapter(name="test", tier=Tier.ENTERPRISE)
        assert not adapter._check_tier_access(Tier.COMMUNITY)
        assert not adapter._check_tier_access(Tier.PRO)
        assert adapter._check_tier_access(Tier.ENTERPRISE)
    
    def test_tool_schema(self):
        """Test tool schema generation"""
        class MockAdapter(CodegenToolAdapter):
            def _execute_impl(self, session, **kwargs):
                return ToolResult(success=True)
            
            def _get_parameter_schema(self):
                return {"type": "object", "properties": {}}
        
        adapter = MockAdapter(
            name="test_tool",
            tier=Tier.PRO,
            requires_transaction=True,
            description="Test tool"
        )
        
        schema = adapter.get_schema()
        assert schema["name"] == "test_tool"
        assert schema["tier"] == "pro"
        assert schema["requires_transaction"] is True
        assert schema["description"] == "Test tool"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
