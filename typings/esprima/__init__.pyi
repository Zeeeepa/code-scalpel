"""Type stubs for esprima - ECMAScript parsing infrastructure."""

from typing import Any, Dict, List, Optional
from esprima.nodes import Program

def parseScript(
    code: str,
    options: Optional[Dict[str, Any]] = None,
    delegate: Optional[Any] = None,
    *,
    jsx: bool = False,
    tolerant: bool = False,
    comment: bool = False,
    range: bool = False,
    loc: bool = False,
    tokens: bool = False,
) -> Program: ...
def parseModule(
    code: str,
    options: Optional[Dict[str, Any]] = None,
    delegate: Optional[Any] = None,
    *,
    jsx: bool = False,
    tolerant: bool = False,
    comment: bool = False,
    range: bool = False,
    loc: bool = False,
    tokens: bool = False,
) -> Program: ...
def parse(
    code: str,
    options: Optional[Dict[str, Any]] = None,
    delegate: Optional[Any] = None,
) -> Program: ...
def tokenize(
    code: str,
    options: Optional[Dict[str, Any]] = None,
) -> List[Any]: ...

__version__: str
