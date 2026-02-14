from typing import TYPE_CHECKING

from code_scalpel.lsp.codemods.base import CodeAction
from code_scalpel.core.interfaces.editable import Editable

if TYPE_CHECKING:
    from code_scalpel.lsp.server import CodegenLanguageServer


class MoveSymbolToFile(CodeAction):
    name = "Move Symbol to File"

    def is_applicable(self, server: "CodegenLanguageServer", node: Editable) -> bool:
        return True

    def execute(self, server: "CodegenLanguageServer", node: Editable) -> None:
        target_file = server.window_show_message_request(
            "Select the file to move the symbol to",
            server.codebase.files,
        ).result(timeout=10)
        if target_file is None:
            return
        server.codebase.move_symbol(node.parent_symbol, target_file)
