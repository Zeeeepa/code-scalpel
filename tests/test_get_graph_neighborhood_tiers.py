import pytest


@pytest.mark.asyncio
async def test_get_graph_neighborhood_community_applies_limits(monkeypatch, tmp_path):
    import code_scalpel.mcp.server as server

    # Small project with a call chain main -> a -> b
    (tmp_path / "mod.py").write_text(
        """

def main():
    a()


def a():
    b()


def b():
    return 1
"""
    )

    monkeypatch.setattr(server, "_get_current_tier", lambda: "community")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_k": 1, "max_nodes": 1},
            "capabilities": {"basic_neighborhood"},
        },
        raising=False,
    )

    result = await server.get_graph_neighborhood(
        center_node_id="mod.py:main",
        k=5,
        max_nodes=100,
        direction="both",
        project_root=str(tmp_path),
    )

    assert result.success is True
    assert result.k == 1
    assert result.truncated is True
    assert len(result.nodes) <= 1
    if result.truncation_warning:
        assert "upgrade" not in result.truncation_warning.lower()


@pytest.mark.asyncio
async def test_get_graph_neighborhood_pro_uses_advanced_variant_cache(monkeypatch, tmp_path):
    import code_scalpel.mcp.server as server

    (tmp_path / "mod.py").write_text(
        """

def main():
    a()


def a():
    b()


def b():
    return 1
"""
    )

    monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_k": 5, "max_nodes": 100},
            "capabilities": {"basic_neighborhood", "advanced_neighborhood"},
        },
        raising=False,
    )

    called = {"variant": None}

    original = server._get_cached_graph

    def _wrapped(project_root, cache_variant="default"):
        called["variant"] = cache_variant
        return original(project_root, cache_variant=cache_variant)

    monkeypatch.setattr(server, "_get_cached_graph", _wrapped)

    result = await server.get_graph_neighborhood(
        center_node_id="mod.py:main",
        k=2,
        max_nodes=50,
        project_root=str(tmp_path),
    )

    assert result.success is True
    assert called["variant"] == "advanced"


@pytest.mark.asyncio
async def test_get_graph_neighborhood_enterprise_adds_metrics(monkeypatch, tmp_path):
    import code_scalpel.mcp.server as server

    # main calls a and b; b calls c
    (tmp_path / "mod.py").write_text(
        """

def c():
    return 1


def b():
    return c()


def a():
    return 0


def main():
    a(); b()
"""
    )

    monkeypatch.setattr(server, "_get_current_tier", lambda: "enterprise")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_k": None, "max_nodes": None},
            "capabilities": {
                "basic_neighborhood",
                "advanced_neighborhood",
                "custom_traversal",
            },
        },
        raising=False,
    )

    result = await server.get_graph_neighborhood(
        center_node_id="mod.py:main",
        k=2,
        max_nodes=50,
        project_root=str(tmp_path),
    )

    assert result.success is True
    assert hasattr(result.nodes[0], "in_degree")
    assert hasattr(result.nodes[0], "out_degree")
    assert isinstance(result.hot_nodes, list)
