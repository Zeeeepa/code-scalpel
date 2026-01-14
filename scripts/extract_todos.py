#!/usr/bin/env python3
"""
TODO Extraction and Analysis Tool for Code Scalpel

This script systematically extracts and analyzes TODO items from the codebase,
generating reports organized by module, tier, and priority.

Usage:
    python scripts/extract_todos.py [options]

Options:
    --output-dir DIR    Output directory for reports (default: docs/todo_reports/)
    --format FORMAT     Output format: markdown, json, csv (default: markdown)
    --by-tier          Group TODOs by tier (COMMUNITY, PRO, ENTERPRISE)
    --by-module        Group TODOs by module
    --by-file          Generate file-by-file breakdown
    --stats-only       Generate statistics summary only
    --update-roadmap   Auto-update roadmap documents

Examples:
    # Generate full report
    python scripts/extract_todos.py --by-module --by-tier

    # Update roadmap with latest counts
    python scripts/extract_todos.py --update-roadmap

    # Export to CSV for tracking
    python scripts/extract_todos.py --format csv --output-dir reports/
"""

import os
import re
import json
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TodoItem:
    """Represents a single TODO item"""
    file_path: str
    line_number: int
    tier: str  # COMMUNITY, PRO, ENTERPRISE, UNSPECIFIED
    category: str  # FEATURE, ENHANCEMENT, BUGFIX, DOCUMENTATION, TEST
    text: str
    module: str  # Top-level module name
    priority: str  # Critical, High, Medium, Low


class TodoExtractor:
    """Extract and analyze TODO items from Code Scalpel codebase"""

    def __init__(self, src_dir: str = "src/code_scalpel"):
        self.src_dir = Path(src_dir)
        self.todos: List[TodoItem] = []
        self.stats = defaultdict(int)

    def extract_todos(self) -> List[TodoItem]:
        """Extract all TODO items from Python files"""
        for py_file in self.src_dir.rglob("*.py"):
            self._extract_from_file(py_file)

        return self.todos

    def _extract_from_file(self, file_path: Path):
        """Extract TODOs from a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, start=1):
                if 'TODO' in line:
                    todo = self._parse_todo_line(
                        str(file_path),
                        line_num,
                        line
                    )
                    if todo:
                        self.todos.append(todo)
                        self.stats['total'] += 1
                        self.stats[f'tier_{todo.tier}'] += 1
                        self.stats[f'module_{todo.module}'] += 1

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def _parse_todo_line(self, file_path: str, line_num: int, line: str) -> TodoItem:
        """Parse a TODO line and extract metadata"""
        # Determine tier
        tier = 'UNSPECIFIED'
        if '[COMMUNITY]' in line or 'TODO [COMMUNITY]' in line:
            tier = 'COMMUNITY'
        elif '[PRO]' in line or 'TODO [PRO]' in line:
            tier = 'PRO'
        elif '[ENTERPRISE]' in line or 'TODO [ENTERPRISE]' in line:
            tier = 'ENTERPRISE'

        # Determine category
        category = 'UNSPECIFIED'
        if '[FEATURE]' in line:
            category = 'FEATURE'
        elif '[ENHANCEMENT]' in line:
            category = 'ENHANCEMENT'
        elif '[BUGFIX]' in line or '[BUG]' in line:
            category = 'BUGFIX'
        elif '[DOCUMENTATION]' in line or '[DOC]' in line:
            category = 'DOCUMENTATION'
        elif '[TEST]' in line:
            category = 'TEST'

        # Extract module name
        rel_path = Path(file_path).relative_to(self.src_dir)
        module = rel_path.parts[0] if rel_path.parts else 'unknown'

        # Determine priority based on keywords
        priority = self._infer_priority(line, module)

        # Clean up text
        text = line.strip()
        # Remove comment markers
        text = re.sub(r'^#\s*', '', text)
        text = re.sub(r'^\s*//\s*', '', text)

        return TodoItem(
            file_path=str(rel_path),
            line_number=line_num,
            tier=tier,
            category=category,
            text=text,
            module=module,
            priority=priority
        )

    def _infer_priority(self, line: str, module: str) -> str:
        """Infer priority based on keywords and module"""
        line_lower = line.lower()

        # Critical keywords
        if any(word in line_lower for word in [
            'critical', 'security', 'vulnerability', 'urgent',
            'blocking', 'broken', 'crash'
        ]):
            return 'Critical'

        # Critical modules
        if module in ['security', 'symbolic_execution_tools', 'tiers']:
            if 'document' not in line_lower:
                return 'Critical'

        # High priority keywords
        if any(word in line_lower for word in [
            'important', 'must', 'required', 'necessary',
            'performance', 'optimization'
        ]):
            return 'High'

        # Documentation is usually medium priority
        if 'document' in line_lower or 'doc' in line_lower:
            return 'Medium'

        # Default
        return 'Medium'

    def generate_stats_report(self) -> str:
        """Generate statistics summary"""
        total = self.stats['total']

        report = f"""# Code Scalpel TODO Statistics

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total TODOs:** {total}

## By Tier
- COMMUNITY: {self.stats['tier_COMMUNITY']} ({self.stats['tier_COMMUNITY']/total*100:.1f}%)
- PRO: {self.stats['tier_PRO']} ({self.stats['tier_PRO']/total*100:.1f}%)
- ENTERPRISE: {self.stats['tier_ENTERPRISE']} ({self.stats['tier_ENTERPRISE']/total*100:.1f}%)
- UNSPECIFIED: {self.stats['tier_UNSPECIFIED']} ({self.stats['tier_UNSPECIFIED']/total*100:.1f}%)

## By Module
"""

        # Sort modules by count
        module_stats = [(k.replace('module_', ''), v)
                        for k, v in self.stats.items()
                        if k.startswith('module_')]
        module_stats.sort(key=lambda x: x[1], reverse=True)

        for module, count in module_stats:
            report += f"- **{module}**: {count} ({count/total*100:.1f}%)\n"

        return report

    def generate_module_report(self) -> str:
        """Generate detailed report by module"""
        modules = defaultdict(list)
        for todo in self.todos:
            modules[todo.module].append(todo)

        report = "# TODO Items by Module\n\n"

        # Sort by count
        sorted_modules = sorted(modules.items(),
                                key=lambda x: len(x[1]),
                                reverse=True)

        for module, todos in sorted_modules:
            report += f"## {module}/ ({len(todos)} TODOs)\n\n"

            # Group by tier
            by_tier = defaultdict(list)
            for todo in todos:
                by_tier[todo.tier].append(todo)

            for tier in ['COMMUNITY', 'PRO', 'ENTERPRISE', 'UNSPECIFIED']:
                tier_todos = by_tier[tier]
                if tier_todos:
                    report += f"### {tier} Tier ({len(tier_todos)} items)\n\n"
                    for todo in tier_todos[:10]:  # Show first 10
                        report += f"- [{todo.file_path}#{todo.line_number}] {todo.text}\n"
                    if len(tier_todos) > 10:
                        report += f"- *... and {len(tier_todos) - 10} more*\n"
                    report += "\n"

        return report

    def export_json(self, output_path: str):
        """Export TODOs as JSON"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_todos': len(self.todos),
            'stats': dict(self.stats),
            'todos': [asdict(todo) for todo in self.todos]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    def export_csv(self, output_path: str):
        """Export TODOs as CSV"""
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'file_path', 'line_number', 'tier', 'category',
                'module', 'priority', 'text'
            ])
            writer.writeheader()
            for todo in self.todos:
                writer.writerow(asdict(todo))


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract and analyze TODO items from Code Scalpel'
    )
    parser.add_argument(
        '--output-dir',
        default='docs/todo_reports',
        help='Output directory for reports'
    )
    parser.add_argument(
        '--format',
        choices=['markdown', 'json', 'csv', 'all'],
        default='markdown',
        help='Output format'
    )
    parser.add_argument(
        '--by-tier',
        action='store_true',
        help='Group by tier'
    )
    parser.add_argument(
        '--by-module',
        action='store_true',
        help='Group by module'
    )
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Generate stats only'
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract TODOs
    extractor = TodoExtractor()
    print("Extracting TODOs...")
    extractor.extract_todos()
    print(f"Found {len(extractor.todos)} TODO items")

    # Generate reports
    if args.stats_only or args.format == 'markdown' or args.format == 'all':
        stats_report = extractor.generate_stats_report()
        stats_path = output_dir / 'todo_statistics.md'
        with open(stats_path, 'w') as f:
            f.write(stats_report)
        print(f"Statistics report: {stats_path}")

    if args.by_module or args.format == 'markdown' or args.format == 'all':
        module_report = extractor.generate_module_report()
        module_path = output_dir / 'todos_by_module.md'
        with open(module_path, 'w') as f:
            f.write(module_report)
        print(f"Module report: {module_path}")

    if args.format == 'json' or args.format == 'all':
        json_path = output_dir / 'todos.json'
        extractor.export_json(str(json_path))
        print(f"JSON export: {json_path}")

    if args.format == 'csv' or args.format == 'all':
        csv_path = output_dir / 'todos.csv'
        extractor.export_csv(str(csv_path))
        print(f"CSV export: {csv_path}")


if __name__ == '__main__':
    main()
