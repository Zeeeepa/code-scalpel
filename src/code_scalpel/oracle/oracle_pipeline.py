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

from code_scalpel.analysis.project_crawler import ProjectCrawler
from code_scalpel.oracle.constraint_analyzer import ConstraintAnalyzer
from code_scalpel.oracle.spec_generator import SpecGenerator
from code_scalpel.oracle.symbol_extractor import SymbolExtractor

logger = logging.getLogger(__name__)


class OraclePipeline:
    """Serverless constraint injection pipeline.

    Chains together all Oracle components with tier-aware limits.
    """

    def __init__(self, repo_root: str | Path, tier: str = "community"):
        """Initialize the Oracle pipeline.

        Args:
            repo_root: Root directory of the codebase to analyze
            tier: Tier level (community, pro, enterprise) that determines limits
        """
        self.repo_root = Path(repo_root).resolve()
        self.tier = tier

        # Initialize components
        self.symbol_extractor = SymbolExtractor()
        self.constraint_analyzer = ConstraintAnalyzer()
        self.spec_generator = SpecGenerator()

        # Get tier-based scanner limits
        self.scanner_limits = self._get_scanner_limits(tier)

    @staticmethod
    def _get_scanner_limits(tier: str) -> Dict[str, int]:
        """Get scanner limits for a given tier.

        Args:
            tier: Tier level (community, pro, enterprise)

        Returns:
            Dict with max_files and max_depth
        """
        limits = {
            "community": {"max_files": 50, "max_depth": 2},
            "pro": {"max_files": 2000, "max_depth": 10},
            "enterprise": {"max_files": 100000, "max_depth": 50},
        }
        return limits.get(tier, limits["community"])

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

        logger.info(f"[Oracle Pipeline] tier={self.tier}, " f"limits={self.scanner_limits}, " f"file={file_path}")

        # Step 1: Scan with tier-limited visibility
        logger.debug("[Oracle] Step 1: Crawling project with tier limits...")
        crawler = ProjectCrawler(
            str(self.repo_root),
            max_files=self.scanner_limits["max_files"],
            max_depth=self.scanner_limits["max_depth"],
        )
        crawl_result = crawler.crawl()
        scanned_files = crawl_result.total_files
        logger.debug(f"[Oracle] Crawled {scanned_files} files")

        # Step 2: Extract symbols from crawled files
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
            graph=None,
            governance_config=governance_config,
            max_depth=self.scanner_limits["max_depth"],
        )

        # Step 4: Generate Markdown spec
        logger.debug("[Oracle] Step 4: Generating Markdown spec...")
        spec = self.spec_generator.generate_constraint_spec(
            file_path=str(target_file),
            instruction=instruction,
            graph=None,  # TODO: Pass built graph
            governance_config=governance_config,
            tier=self.tier,
            max_graph_depth=self.scanner_limits["max_depth"],
            max_context_lines=self._get_context_lines(self.tier),
        )

        logger.info(f"[Oracle] Spec generated: {len(spec.markdown)} chars")
        return spec.markdown

    @staticmethod
    def _get_context_lines(tier: str) -> int:
        """Get max context lines for a tier.

        Args:
            tier: Tier level

        Returns:
            Max context lines to include in spec
        """
        return {
            "community": 100,
            "pro": 200,
            "enterprise": 1000,
        }.get(tier, 100)


async def generate_constraint_spec_async(
    repo_root: str | Path,
    file_path: str,
    instruction: str,
    tier: str = "community",
    governance_config: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate constraint spec asynchronously.

    This is a convenience wrapper for use in async contexts.

    Args:
        repo_root: Root directory of codebase
        file_path: Path to target file
        instruction: Implementation instruction
        tier: Tier level (community, pro, enterprise)
        governance_config: Optional governance configuration

    Returns:
        Markdown constraint specification
    """
    import asyncio

    pipeline = OraclePipeline(repo_root, tier)
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
    tier: str = "community",
    governance_config: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate constraint spec synchronously.

    This is the main entry point for the Oracle pipeline.

    Args:
        repo_root: Root directory of codebase
        file_path: Path to target file
        instruction: Implementation instruction
        tier: Tier level (community, pro, enterprise)
        governance_config: Optional governance configuration

    Returns:
        Markdown constraint specification
    """
    pipeline = OraclePipeline(repo_root, tier)
    return pipeline.generate_constraint_spec(file_path, instruction, governance_config)
