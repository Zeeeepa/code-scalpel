# Type stubs for javalang.parser module
from typing import Optional, Tuple

class JavaSyntaxError(Exception):
    position: Optional[Tuple[int, int]]
    description: str
