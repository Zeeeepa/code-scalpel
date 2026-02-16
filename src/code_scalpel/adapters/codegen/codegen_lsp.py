"""
Codegen LSP Adapter

Direct imports from Codegen SDK LSP extension - no reimplementation.
Provides Language Server Protocol functionality with tier unification.
"""

# Import all LSP modules
from codegen.extensions.lsp import (
    completion as _completion,
    definition as _definition,
    document_symbol as _document_symbol,
    execute as _execute,
    io as _io,
    kind as _kind,
    lsp as _lsp,
    progress as _progress,
    protocol as _protocol,
    range as _range,
    server as _server,
    utils as _utils,
)

# Re-export with tier unification
# All LSP functionality is now Community tier accessible

# Module re-exports
completion = _completion
definition = _definition
document_symbol = _document_symbol
execute = _execute
io = _io
kind = _kind
lsp = _lsp
progress = _progress
protocol = _protocol
range = _range
server = _server
utils = _utils

__all__ = [
    'completion',
    'definition',
    'document_symbol',
    'execute',
    'io',
    'kind',
    'lsp',
    'progress',
    'protocol',
    'range',
    'server',
    'utils',
]

