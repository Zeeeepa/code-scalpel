# Type stubs for javalang package
from . import tree as tree
from . import ast as ast
from . import parser as parser

class parse:
    @staticmethod
    def parse(code: str) -> tree.CompilationUnit: ...
