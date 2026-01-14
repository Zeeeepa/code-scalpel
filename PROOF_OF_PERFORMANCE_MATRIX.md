# PROOF_OF_PERFORMANCE_MATRIX
> [20260112_TEST] Empirical matrix benchmark across all MCP tools and tiers.
This report summarizes P95 latency and outcome per tool/tier.
## Method
- Execution: in-process tool calls (no MCP stdio framing, no HTTP)
- Standard target file: `/mnt/k/backup/Develop/code-scalpel/src/code_scalpel/mcp/server.py`
- Tier selection: real JWT licenses via `CODE_SCALPEL_LICENSE_PATH` with `CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY=1`
## Results
| Tool | Tier | Latency (P95) | Payload (median) | Outcome |
|------|------|---------------:|----------------:|---------|
| `analyze_code` | Community | 18.0ms | 712 bytes | ✅ Success |
| `analyze_code` | Enterprise | 12.4ms | 712 bytes | ✅ Success |
| `analyze_code` | Pro | 14.6ms | 712 bytes | ✅ Success |
| `code_policy_check` | Community | 1286.3ms | 16998 bytes | ✅ Success |
| `code_policy_check` | Enterprise | 4881.9ms | 506595 bytes | ✅ Success |
| `code_policy_check` | Pro | 4270.7ms | 501415 bytes | ✅ Success |
| `crawl_project` | Community | 23644.5ms | 26868 bytes | ✅ Success |
| `crawl_project` | Enterprise | 12602.7ms | 1689383 bytes | ✅ Success |
| `crawl_project` | Pro | 11353.3ms | 1725178 bytes | ✅ Success |
| `cross_file_security_scan` | Community | 56685.0ms | 574 bytes | ✅ Success |
| `cross_file_security_scan` | Enterprise | 137526.6ms | 825 bytes | ✅ Success |
| `cross_file_security_scan` | Pro | 139498.8ms | 700 bytes | ✅ Success |
| `extract_code` | Community | 576.1ms | 1688 bytes | ✅ Success |
| `extract_code` | Enterprise | 1479.2ms | 1692 bytes | ✅ Success |
| `extract_code` | Pro | 1066.5ms | 1682 bytes | ✅ Success |
| `generate_unit_tests` | Community | 5.3ms | 437 bytes | ✅ Success |
| `generate_unit_tests` | Enterprise | 14.6ms | 1887 bytes | ✅ Success |
| `generate_unit_tests` | Pro | 16.6ms | 1878 bytes | ✅ Success |
| `get_call_graph` | Community | 65580.9ms | 81938 bytes | ✅ Success |
| `get_call_graph` | Enterprise | 48311.1ms | 19979461 bytes | ✅ Success |
| `get_call_graph` | Pro | 39746.8ms | 934074 bytes | ✅ Success |
| `get_cross_file_dependencies` | Community | 29043.5ms | 1210 bytes | ✅ Success |
| `get_cross_file_dependencies` | Enterprise | 28643.7ms | 1217 bytes | ✅ Success |
| `get_cross_file_dependencies` | Pro | 29378.8ms | 1211 bytes | ✅ Success |
| `get_file_context` | Community | 13.0ms | 952 bytes | ✅ Success |
| `get_file_context` | Enterprise | 4914.8ms | 147954 bytes | ✅ Success |
| `get_file_context` | Pro | 22.4ms | 941 bytes | ✅ Success |
| `get_graph_neighborhood` | Community | 5.7ms | 534 bytes | ✅ Success |
| `get_graph_neighborhood` | Enterprise | 13.9ms | 534 bytes | ✅ Success |
| `get_graph_neighborhood` | Pro | 12.4ms | 534 bytes | ✅ Success |
| `get_project_map` | Community | 325253.6ms | 58781 bytes | ✅ Success |
| `get_project_map` | Enterprise | 1287004.5ms | 2842079 bytes | ✅ Success |
| `get_project_map` | Pro | 950992.3ms | 1054014 bytes | ✅ Success |
| `get_symbol_references` | Community | 16681.3ms | 873 bytes | ✅ Success |
| `get_symbol_references` | Enterprise | 58613.0ms | 42599 bytes | ✅ Success |
| `get_symbol_references` | Pro | 58462.3ms | 41793 bytes | ✅ Success |
| `rename_symbol` | Community | 20133.8ms | 464 bytes | ✅ Success |
| `rename_symbol` | Enterprise | 17866.4ms | 464 bytes | ✅ Success |
| `rename_symbol` | Pro | 18268.3ms | 464 bytes | ✅ Success |
| `scan_dependencies` | Community | 2001.6ms | 12794 bytes | ✅ Success |
| `scan_dependencies` | Enterprise | 46174.1ms | 16498 bytes | ✅ Success |
| `scan_dependencies` | Pro | 45713.1ms | 13501 bytes | ✅ Success |
| `security_scan` | Community | 58.8ms | 529 bytes | ✅ Success |
| `security_scan` | Enterprise | 20.5ms | 529 bytes | ✅ Success |
| `security_scan` | Pro | 23.0ms | 529 bytes | ✅ Success |
| `simulate_refactor` | Community | 10.5ms | 373 bytes | ✅ Success |
| `simulate_refactor` | Enterprise | 56.9ms | 554 bytes | ✅ Success |
| `simulate_refactor` | Pro | 62.0ms | 378 bytes | ✅ Success |
| `symbolic_execute` | Community | 5.7ms | 801 bytes | ✅ Success |
| `symbolic_execute` | Enterprise | 13.4ms | 1784 bytes | ✅ Success |
| `symbolic_execute` | Pro | 13.9ms | 1413 bytes | ✅ Success |
| `type_evaporation_scan` | Community | 9.6ms | 1929 bytes | ✅ Success |
| `type_evaporation_scan` | Enterprise | 13.5ms | 5459 bytes | ✅ Success |
| `type_evaporation_scan` | Pro | 13.9ms | 2024 bytes | ✅ Success |
| `unified_sink_detect` | Community | 7.9ms | 934 bytes | ✅ Success |
| `unified_sink_detect` | Enterprise | 14.1ms | 2470 bytes | ✅ Success |
| `unified_sink_detect` | Pro | 20.2ms | 1496 bytes | ✅ Success |
| `update_symbol` | Community | 17743.8ms | 486 bytes | ✅ Success |
| `update_symbol` | Enterprise | 15.3ms | 534 bytes | ✅ Success |
| `update_symbol` | Pro | 77166.4ms | 494 bytes | ✅ Success |
| `validate_paths` | Community | 13.6ms | 791 bytes | ✅ Success |
| `validate_paths` | Enterprise | 44.2ms | 790 bytes | ✅ Success |
| `validate_paths` | Pro | 24.3ms | 791 bytes | ✅ Success |
| `verify_policy_integrity` | Community | 82.0ms | 323 bytes | ✅ Success |
| `verify_policy_integrity` | Enterprise | 144.7ms | 732 bytes | ✅ Success |
| `verify_policy_integrity` | Pro | 89.2ms | 448 bytes | ✅ Success |

## Notes
- `scan_dependencies` may contact OSV depending on configuration; this run uses its built-in `timeout` parameter to prevent hangs.
- `verify_policy_integrity` requires `SCALPEL_MANIFEST_SECRET` for signature validation at Pro/Enterprise; failures are recorded as such if unset.
