"""Oracle Pipeline: Serverless Constraint Injection.

[20260126_PHASE1B] Core pipeline that chains:
- ProjectCrawler → Scan files with tier-limited visibility
- SymbolExtractor → Parse symbols from each file
- UniversalGraph → Build dependency graph
- ConstraintAnalyzer → Check governance rules
- SpecGenerator → Format as Markdown

This is the "Perception Layer" of Code Scalpel:
- Input: file_path + instruction + tier
- Processing: Pure CPU (no network, no LLM)
- Output: Markdown constraint spec (<200ms)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from code_scalpel.lib_scalpel.graph_engine.scanner import ProjectScanner
from code_scalpel.lib_scalpel.analysis.constraint_analyzer import ConstraintAnalyzer
from code_scalpel.lib_scalpel.analysis.spec_generator import SpecGenerator
from code_scalpel.lib_scalpel.visitors.symbol_extractor import SymbolExtractor

logger = logging.getLogger(__name__)


class OraclePipeline:
    """Serverless constraint injection pipeline.

    Chains together all Oracle components with tier-aware limits.
    """

    def __init__(self, repo_root: str | Path, max_files: int = 50, max_depth: int = 2):
        """Initialize the Oracle pipeline.

        Args:
            repo_root: Root directory of the codebase to analyze
            max_files: Maximum number of files to scan
            max_depth: Maximum directory depth to traverse
        """
        self.repo_root = Path(repo_root).resolve()
        self.max_files = max_files
        self.max_depth = max_depth

        # Initialize components
        self.symbol_extractor = SymbolExtractor()
        self.constraint_analyzer = ConstraintAnalyzer()
        self.spec_generator = SpecGenerator()

    def generate_constraint_spec(
        self,
        file_path: str,
        instruction: str,
        governance_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate constraint spec for a file using the full pipeline.

        Args:
            file_path: Path to the target file
            instruction: What needs to be implemented
            governance_config: Optional governance configuration

        Returns:
            Markdown constraint specification

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If instruction is empty
            SyntaxError: If file has syntax errors
        """
        # Validate inputs
        if not file_path:
            raise ValueError("file_path is required")
        if not instruction:
            raise ValueError("instruction is required")

        target_file = Path(file_path).resolve()
        if not target_file.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(
            f"[Oracle Pipeline] limits=max_files:{self.max_files}, max_depth:{self.max_depth}, "
            f"file={file_path}"
        )

        # Step 1: Scan with tier-limited visibility
        logger.debug("[Oracle] Step 1: Scanning project with limits...")
        scanner = ProjectScanner(
            root_dir=str(self.repo_root),
            max_files=self.max_files,
            max_depth=self.max_depth,
        )
        graph = scanner.scan()
        scanned_files = len(graph.nodes)
        logger.debug(f"[Oracle] Scanned {scanned_files} nodes in graph")

        # Step 2: Extract symbols from target file
        logger.debug("[Oracle] Step 2: Extracting symbols...")
        # For now, extract symbols from the target file only
        # (Full pipeline integration will extract from all crawled files)
        try:
            _ = self.symbol_extractor.extract_from_file(str(target_file))
            # TODO: Use symbol_table to build graph with UniversalGraph
        except SyntaxError as e:
            logger.error(f"[Oracle] Syntax error in {file_path}: {e}")
            raise

        # Step 3: Analyze constraints (governance rules, etc.)
        logger.debug("[Oracle] Step 3: Analyzing constraints...")
        # TODO: Build graph from crawled symbols and use constraints
        _ = self.constraint_analyzer.analyze_file(
            str(target_file),
            graph=graph,
            governance_config=governance_config,
            max_depth=self.max_depth,
        )

        # Step 4: Generate Markdown spec
        logger.debug("[Oracle] Step 4: Generating Markdown spec...")
        spec = self.spec_generator.generate_constraint_spec(
            file_path=str(target_file),
            instruction=instruction,
            graph=graph,
            governance_config=governance_config,
            tier="library",
            max_graph_depth=self.max_depth,
            max_context_lines=self._get_context_lines(self.max_files),
        )

        logger.info(f"[Oracle] Spec generated: {len(spec.markdown)} chars")
        return spec.markdown

    @staticmethod
    def _get_context_lines(max_files: int) -> int:
        """Get max context lines based on scan size.

        Larger scans can handle more context. Formula:
        - 50 files: 100 lines
        - 100 files: 110 lines
        - 2000 files: 300 lines
        - 100000 files: 1000 lines (capped)

        Args:
            max_files: Maximum files in scan

        Returns:
            Max context lines to include in spec
        """
        # Formula: base (100) + bonus (1 line per 10 files), capped at 1000
        return min(100 + (max_files // 10), 1000)


async def generate_constraint_spec_async(
    repo_root: str | Path,
    file_path: str,
    instruction: str,
    max_files: int = 50,
    max_depth: int = 2,
    governance_config: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate constraint spec asynchronously.

    This is a convenience wrapper for use in async contexts.

    Args:
        repo_root: Root directory of codebase
        file_path: Path to target file
        instruction: Implementation instruction
        max_files: Maximum number of files to scan
        max_depth: Maximum directory depth to traverse
        governance_config: Optional governance configuration

    Returns:
        Markdown constraint specification
    """
    import asyncio

    pipeline = OraclePipeline(repo_root, max_files=max_files, max_depth=max_depth)
    return await asyncio.to_thread(
        pipeline.generate_constraint_spec,
        file_path,
        instruction,
        governance_config,
    )


def generate_constraint_spec_sync(
    repo_root: str | Path,
    file_path: str,
    instruction: str,
    max_files: int = 50,
    max_depth: int = 2,
    governance_config: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate constraint spec synchronously.

    This is the main entry point for the Oracle pipeline.

    Args:
        repo_root: Root directory of codebase
        file_path: Path to target file
        instruction: Implementation instruction
        max_files: Maximum number of files to scan
        max_depth: Maximum directory depth to traverse
        governance_config: Optional governance configuration

    Returns:
        Markdown constraint specification
    """
    pipeline = OraclePipeline(repo_root, max_files=max_files, max_depth=max_depth)
    return pipeline.generate_constraint_spec(file_path, instruction, governance_config)
