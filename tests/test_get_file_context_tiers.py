
import pytest
from unittest.mock import patch, MagicMock
import code_scalpel.mcp.server
import importlib
# Reload server to ensure we test the latest code
importlib.reload(code_scalpel.mcp.server)
from code_scalpel.mcp.server import get_file_context, FileContextResult

@pytest.mark.asyncio
async def test_get_file_context_community():
    with patch("code_scalpel.licensing.get_current_tier", return_value="community"):
        # Create a dummy file
        with open("dummy_community.py", "w") as f:
            f.write("def foo(): pass\n")

        try:
            result = await get_file_context("dummy_community.py")
            
            assert isinstance(result, FileContextResult)
            assert result.semantic_summary is None
            assert result.related_imports == []
            assert result.pii_redacted is False
            assert result.access_controlled is False
            
        finally:
            import os
            if os.path.exists("dummy_community.py"):
                os.remove("dummy_community.py")

@pytest.mark.asyncio
async def test_get_file_context_pro():
    with patch("code_scalpel.licensing.get_current_tier", return_value="pro"):
        with open("dummy_pro.py", "w") as f:
            f.write("def foo(): pass\n")

        try:
            result = await get_file_context("dummy_pro.py")
            assert isinstance(result, FileContextResult)
            # Current mock implementation returns these
            assert result.semantic_summary is not None
            assert "Semantic summary" in result.semantic_summary
            # related_imports_inclusion is enabled in pro
            assert result.related_imports == ["related.module.a", "related.module.b"]
            
        finally:
            import os
            if os.path.exists("dummy_pro.py"):
                os.remove("dummy_pro.py")

@pytest.mark.asyncio
async def test_get_file_context_enterprise():
    with patch("code_scalpel.licensing.get_current_tier", return_value="enterprise"):
        with open("dummy_ent.py", "w") as f:
            f.write("email = 'user@example.com'\n")

        try:
            result = await get_file_context("dummy_ent.py")
            assert isinstance(result, FileContextResult)
            assert result.semantic_summary is not None
            assert result.pii_redacted is True
            assert result.access_controlled is True
            
        finally:
            import os
            if os.path.exists("dummy_ent.py"):
                os.remove("dummy_ent.py")
