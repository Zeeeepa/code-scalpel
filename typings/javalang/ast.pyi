# Type stubs for javalang.ast module
from typing import Optional, Tuple

class Node:
    position: Optional[Tuple[int, int]]
    def __init__(self) -> None: ...
