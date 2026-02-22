import ast
from code_scalpel.mcp.helpers.analyze_helpers import _compute_halstead_metrics_python

code = """
def calculate(x, y):
    return x + y * 2
"""
tree = ast.parse(code)
metrics = _compute_halstead_metrics_python(tree)
print(metrics)
