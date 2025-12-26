import pytest


@pytest.mark.asyncio
async def test_get_call_graph_community_applies_limits(monkeypatch, tmp_path):
    import code_scalpel.mcp.server as server

    (tmp_path / "mod.py").write_text(
        """

def f0():
    f1(); f2(); f3(); f4(); f5()

def f1():
    return 1

def f2():
    return 2

def f3():
    return 3

def f4():
    return 4

def f5():
    return 5
"""
    )

    monkeypatch.setattr(server, "_get_current_tier", lambda: "community")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_depth": 2, "max_nodes": 3},
            "capabilities": [
                "static_call_graph",
                "caller_analysis",
                "callee_analysis",
                "mermaid_diagram_generation",
            ],
        },
        raising=False,
    )

    result = await server.get_call_graph(
        project_root=str(tmp_path), entry_point="f0", depth=10
    )

    assert result.success is True
    assert len(result.nodes) == 3
    assert result.nodes_truncated is True
    assert result.truncation_warning is not None
    assert "upgrade" not in result.truncation_warning.lower()


@pytest.mark.asyncio
async def test_get_call_graph_pro_polymorphism_resolution(monkeypatch, tmp_path):
    import code_scalpel.mcp.server as server

    (tmp_path / "a.py").write_text(
        """

class A:
    def foo(self):
        self.bar()

    def bar(self):
        return 1


def main():
    a = A()
    a.foo()
"""
    )

    monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_depth": None, "max_nodes": None},
            "capabilities": [
                "static_call_graph",
                "caller_analysis",
                "callee_analysis",
                "mermaid_diagram_generation",
                "polymorphism_resolution",
            ],
        },
        raising=False,
    )

    result = await server.get_call_graph(
        project_root=str(tmp_path), entry_point="main", depth=10
    )

    assert result.success is True
    assert any(e.callee.endswith(":A.foo") for e in result.edges)
    assert any(e.callee.endswith(":A.bar") for e in result.edges)


@pytest.mark.asyncio
async def test_get_call_graph_enterprise_adds_metadata(monkeypatch, tmp_path):
    import code_scalpel.mcp.server as server

    (tmp_path / "mod.py").write_text(
        """

def unused():
    return 0


def used():
    return 1


def main():
    return used()
"""
    )

    monkeypatch.setattr(server, "_get_current_tier", lambda: "enterprise")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_depth": None, "max_nodes": None},
            "capabilities": [
                "static_call_graph",
                "caller_analysis",
                "callee_analysis",
                "mermaid_diagram_generation",
                "hot_path_identification",
                "dead_code_detection",
            ],
        },
        raising=False,
    )

    result = await server.get_call_graph(project_root=str(tmp_path), entry_point=None)

    assert result.success is True
    assert isinstance(result.hot_nodes, list)
    assert isinstance(result.dead_code_candidates, list)
    assert any(s.endswith(":unused") for s in result.dead_code_candidates)
