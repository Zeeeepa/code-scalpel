#!/usr/bin/env python3
"""
[20260114_FEATURE] TODO Extraction and Analysis Tool for Code Scalpel

This script systematically extracts and analyzes TODO/FIXME/HACK items from the
entire codebase, generating reports organized by module, tier, priority, and file.

Integrated into the pre-release checklist pipeline.

Usage:
    python scripts/extract_todos.py [options]

Options:
    --output-dir DIR    Output directory for reports (default: docs/todo_reports/)
    --format FORMAT     Output format: markdown, json, csv, all (default: markdown)
    --by-tier          Group TODOs by tier (COMMUNITY, PRO, ENTERPRISE)
    --by-module        Group TODOs by module
    --by-file          Generate file-by-file breakdown
    --stats-only       Generate statistics summary only
    --update-roadmap   Auto-update roadmap documents
    --full-scan        Scan entire repo, not just src/ (default: True)

Examples:
    # Generate full roadmap report
    python scripts/extract_todos.py --format all

    # Quick statistics
    python scripts/extract_todos.py --stats-only

    # Export to CSV for tracking
    python scripts/extract_todos.py --format csv --output-dir reports/
"""

import os
import re
import json
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TodoItem:
    """Represents a single TODO item"""
    file_path: str
    line_number: int
    tag: str  # TODO, FIXME, HACK, XXX, NOTE, BUG
    tier: str  # COMMUNITY, PRO, ENTERPRISE, UNSPECIFIED
    category: str  # FEATURE, ENHANCEMENT, BUGFIX, DOCUMENTATION, TEST
    text: str
    module: str  # Top-level module name
    priority: str  # Critical, High, Medium, Low
    date_tag: Optional[str] = None  # [20260114_*] style tags


class TodoExtractor:
    """Extract and analyze TODO items from Code Scalpel codebase"""
    
    # File extensions to scan
    CODE_EXTENSIONS = {
        ".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".rs",
        ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".swift",
        ".kt", ".scala", ".html", ".css", ".scss", ".sass", ".less",
        ".vue", ".svelte", ".sql", ".sh", ".bash", ".zsh", ".yaml",
        ".yml", ".toml", ".md", ".rst",
    }
    
    # Directories to skip
    SKIP_DIRS = {
        "__pycache__", "node_modules", ".git", ".venv", "venv",
        "dist", "build", ".tox", ".mypy_cache", ".pytest_cache",
        "htmlcov", ".eggs", ".scalpel_cache", ".code-scalpel",
        "dist_protected", "build_protected",
    }
    
    # Tags to extract
    TODO_TAGS = {"TODO", "FIXME", "HACK", "XXX", "NOTE", "BUG", "OPTIMIZE", "REVIEW"}
    
    # Pattern for date tags like [20260114_FEATURE]
    DATE_TAG_PATTERN = re.compile(r'\[(\d{8}_\w+)\]')

    def __init__(self, root_dir: str = ".", src_only: bool = False):
        self.root_dir = Path(root_dir).resolve()
        self.src_dir = self.root_dir / "src" / "code_scalpel"
        self.src_only = src_only
        self.todos: List[TodoItem] = []
        self.stats = defaultdict(int)
    
    def _should_skip_dir(self, dir_name: str) -> bool:
        """Check if directory should be skipped."""
        return dir_name in self.SKIP_DIRS or dir_name.startswith(".")
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """Check if file should be scanned."""
        return file_path.suffix.lower() in self.CODE_EXTENSIONS

    def extract_todos(self) -> List[TodoItem]:
        """Extract all TODO items from code files"""
        scan_dir = self.src_dir if self.src_only else self.root_dir
        
        for root, dirs, files in os.walk(scan_dir):
            # Filter out directories to skip
            dirs[:] = [d for d in dirs if not self._should_skip_dir(d)]
            
            for file_name in files:
                file_path = Path(root) / file_name
                if self._should_scan_file(file_path):
                    self._extract_from_file(file_path)

        return self.todos

    def _extract_from_file(self, file_path: Path):
        """Extract TODOs from a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, start=1):
                # Check for any TODO-style tag
                line_upper = line.upper()
                for tag in self.TODO_TAGS:
                    if tag in line_upper:
                        todo = self._parse_todo_line(
                            str(file_path),
                            line_num,
                            line,
                            tag
                        )
                        if todo:
                            self.todos.append(todo)
                            self.stats['total'] += 1
                            self.stats[f'tag_{todo.tag}'] += 1
                            self.stats[f'tier_{todo.tier}'] += 1
                            self.stats[f'module_{todo.module}'] += 1
                            self.stats[f'priority_{todo.priority}'] += 1
                        break  # Only count once per line

        except Exception as e:
            pass  # Silently skip files that can't be read

    def _parse_todo_line(self, file_path: str, line_num: int, line: str, tag: str) -> TodoItem:
        """Parse a TODO line and extract metadata"""
        # Determine tier
        tier = 'UNSPECIFIED'
        if '[COMMUNITY]' in line or f'{tag} [COMMUNITY]' in line.upper():
            tier = 'COMMUNITY'
        elif '[PRO]' in line or f'{tag} [PRO]' in line.upper():
            tier = 'PRO'
        elif '[ENTERPRISE]' in line or f'{tag} [ENTERPRISE]' in line.upper():
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
        elif '[SECURITY]' in line:
            category = 'SECURITY'
        elif '[REFACTOR]' in line:
            category = 'REFACTOR'
        elif '[PERF]' in line or '[PERFORMANCE]' in line:
            category = 'PERFORMANCE'

        # Extract module name from path
        try:
            file_p = Path(file_path)
            if self.src_dir.exists() and file_p.is_relative_to(self.src_dir):
                rel_path = file_p.relative_to(self.src_dir)
                module = rel_path.parts[0] if rel_path.parts else 'unknown'
            elif file_p.is_relative_to(self.root_dir):
                rel_path = file_p.relative_to(self.root_dir)
                module = rel_path.parts[0] if rel_path.parts else 'root'
            else:
                module = 'external'
        except (ValueError, TypeError):
            module = 'unknown'

        # Determine priority based on keywords and tag
        priority = self._infer_priority(line, module, tag)
        
        # Extract date tag if present
        date_match = self.DATE_TAG_PATTERN.search(line)
        date_tag = date_match.group(1) if date_match else None

        # Clean up text
        text = line.strip()
        # Remove comment markers
        text = re.sub(r'^#\s*', '', text)
        text = re.sub(r'^\s*//\s*', '', text)
        text = re.sub(r'^\s*\*\s*', '', text)
        text = re.sub(r'^\s*/\*\s*', '', text)
        text = re.sub(r'\s*\*/\s*$', '', text)
        
        # Get relative path for display
        try:
            display_path = str(Path(file_path).relative_to(self.root_dir))
        except ValueError:
            display_path = file_path

        return TodoItem(
            file_path=display_path,
            line_number=line_num,
            tag=tag,
            tier=tier,
            category=category,
            text=text,
            module=module,
            priority=priority,
            date_tag=date_tag
        )

    def _infer_priority(self, line: str, module: str, tag: str) -> str:
        """Infer priority based on keywords, module, and tag"""
        line_lower = line.lower()
        
        # FIXME and BUG tags are higher priority by default
        if tag in ('FIXME', 'BUG'):
            default_priority = 'High'
        elif tag in ('HACK', 'XXX'):
            default_priority = 'High'
        else:
            default_priority = 'Medium'

        # Critical keywords
        if any(word in line_lower for word in [
            'critical', 'security', 'vulnerability', 'urgent',
            'blocking', 'broken', 'crash', 'p0'
        ]):
            return 'Critical'

        # Critical modules
        if module in ['security', 'symbolic_execution_tools', 'tiers', 'licensing']:
            if 'document' not in line_lower:
                return 'Critical'

        # High priority keywords
        if any(word in line_lower for word in [
            'important', 'must', 'required', 'necessary',
            'performance', 'optimization', 'p1'
        ]):
            return 'High'
        
        # Low priority keywords
        if any(word in line_lower for word in [
            'nice to have', 'optional', 'eventually', 'someday',
            'minor', 'cosmetic', 'p3'
        ]):
            return 'Low'

        # Documentation is usually medium priority
        if 'document' in line_lower or 'doc' in line_lower:
            return 'Medium'

        return default_priority

    def generate_stats_report(self) -> str:
        """Generate statistics summary"""
        total = self.stats['total']
        if total == 0:
            return "# Code Scalpel TODO Statistics\n\nNo TODO items found."

        report = f"""# Code Scalpel TODO Statistics

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Items:** {total}

## By Tag

| Tag | Count | % |
|-----|------:|--:|
"""
        for tag in sorted(self.TODO_TAGS):
            count = self.stats.get(f'tag_{tag}', 0)
            if count > 0:
                report += f"| {tag} | {count} | {count/total*100:.1f}% |\n"

        report += """
## By Priority

| Priority | Count | % |
|----------|------:|--:|
"""
        for priority in ['Critical', 'High', 'Medium', 'Low']:
            count = self.stats.get(f'priority_{priority}', 0)
            report += f"| {priority} | {count} | {count/total*100:.1f}% |\n"

        report += """
## By Tier

| Tier | Count | % |
|------|------:|--:|
"""
        for tier in ['COMMUNITY', 'PRO', 'ENTERPRISE', 'UNSPECIFIED']:
            count = self.stats.get(f'tier_{tier}', 0)
            report += f"| {tier} | {count} | {count/total*100:.1f}% |\n"

        report += """
## By Module

| Module | Count | % |
|--------|------:|--:|
"""

        # Sort modules by count
        module_stats = [(k.replace('module_', ''), v)
                        for k, v in self.stats.items()
                        if k.startswith('module_')]
        module_stats.sort(key=lambda x: x[1], reverse=True)

        for module, count in module_stats[:20]:  # Top 20
            report += f"| {module} | {count} | {count/total*100:.1f}% |\n"
        
        if len(module_stats) > 20:
            report += f"| *...{len(module_stats) - 20} more* | | |\n"

        return report

    def generate_module_report(self) -> str:
        """Generate detailed report by module"""
        modules = defaultdict(list)
        for todo in self.todos:
            modules[todo.module].append(todo)

        report = """# TODO Items by Module

This document is auto-generated by `scripts/extract_todos.py` as part of the pre-release checklist.

"""

        # Sort by count
        sorted_modules = sorted(modules.items(),
                                key=lambda x: len(x[1]),
                                reverse=True)

        for module, todos in sorted_modules:
            report += f"## {module}/ ({len(todos)} items)\n\n"

            # Group by priority within module
            by_priority = defaultdict(list)
            for todo in todos:
                by_priority[todo.priority].append(todo)

            for priority in ['Critical', 'High', 'Medium', 'Low']:
                priority_todos = by_priority[priority]
                if priority_todos:
                    report += f"### {priority} Priority ({len(priority_todos)} items)\n\n"
                    for todo in priority_todos[:15]:  # Show first 15
                        date_info = f" `{todo.date_tag}`" if todo.date_tag else ""
                        tier_info = f" [{todo.tier}]" if todo.tier != 'UNSPECIFIED' else ""
                        report += f"- **[{todo.tag}]**{tier_info} {todo.text[:100]}{'...' if len(todo.text) > 100 else ''}\n"
                        report += f"  - 📁 [{todo.file_path}]({todo.file_path}#L{todo.line_number}){date_info}\n"
                    if len(priority_todos) > 15:
                        report += f"- *... and {len(priority_todos) - 15} more*\n"
                    report += "\n"

        return report
    
    def generate_roadmap_report(self) -> str:
        """Generate comprehensive roadmap document organized by priority"""
        report = f"""# Code Scalpel - TODO Roadmap

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Items:** {len(self.todos)}

This document tracks all TODO/FIXME/HACK items in the codebase.
Auto-generated by `scripts/extract_todos.py` as part of the pre-release checklist.

---

## Summary

| Metric | Count |
|--------|------:|
"""
        for tag in ['TODO', 'FIXME', 'HACK', 'BUG', 'NOTE', 'XXX']:
            count = self.stats.get(f'tag_{tag}', 0)
            if count > 0:
                report += f"| {tag} | {count} |\n"
        
        report += f"| **Total** | **{len(self.todos)}** |\n"
        
        report += """
| Priority | Count |
|----------|------:|
"""
        for priority in ['Critical', 'High', 'Medium', 'Low']:
            count = self.stats.get(f'priority_{priority}', 0)
            report += f"| {priority} | {count} |\n"

        report += """
---

## Critical Priority Items

These items should be addressed before release.

"""
        critical = [t for t in self.todos if t.priority == 'Critical']
        if critical:
            for todo in critical[:30]:
                report += f"- **[{todo.tag}]** {todo.text[:120]}{'...' if len(todo.text) > 120 else ''}\n"
                report += f"  - 📁 [{todo.file_path}]({todo.file_path}#L{todo.line_number})\n"
            if len(critical) > 30:
                report += f"\n*... and {len(critical) - 30} more critical items*\n"
        else:
            report += "*No critical items found.*\n"

        report += """
---

## High Priority Items

These items should be addressed soon.

"""
        high = [t for t in self.todos if t.priority == 'High']
        if high:
            # Group by module
            by_module = defaultdict(list)
            for todo in high:
                by_module[todo.module].append(todo)
            
            for module, todos in sorted(by_module.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
                report += f"### {module}/ ({len(todos)} items)\n\n"
                for todo in todos[:5]:
                    report += f"- **[{todo.tag}]** {todo.text[:100]}{'...' if len(todo.text) > 100 else ''}\n"
                    report += f"  - 📁 [{todo.file_path}]({todo.file_path}#L{todo.line_number})\n"
                if len(todos) > 5:
                    report += f"- *... and {len(todos) - 5} more in this module*\n"
                report += "\n"
        else:
            report += "*No high priority items found.*\n"

        report += """
---

## Items by File

<details>
<summary>Click to expand file-by-file listing</summary>

"""
        # Group by file
        by_file = defaultdict(list)
        for todo in self.todos:
            by_file[todo.file_path].append(todo)
        
        for file_path, todos in sorted(by_file.items()):
            report += f"### [{file_path}]({file_path})\n\n"
            for todo in sorted(todos, key=lambda x: x.line_number):
                report += f"- **L{todo.line_number}** [{todo.tag}] {todo.text[:80]}{'...' if len(todo.text) > 80 else ''}\n"
            report += "\n"

        report += """
</details>

---

*This document is auto-generated. Do not edit manually.*
"""
        return report

    def export_json(self, output_path: str):
        """Export TODOs as JSON"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_items': len(self.todos),
            'stats': {
                'by_tag': {k.replace('tag_', ''): v for k, v in self.stats.items() if k.startswith('tag_')},
                'by_priority': {k.replace('priority_', ''): v for k, v in self.stats.items() if k.startswith('priority_')},
                'by_tier': {k.replace('tier_', ''): v for k, v in self.stats.items() if k.startswith('tier_')},
                'by_module': {k.replace('module_', ''): v for k, v in self.stats.items() if k.startswith('module_')},
            },
            'items': [asdict(todo) for todo in self.todos]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    def export_csv(self, output_path: str):
        """Export TODOs as CSV"""
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'file_path', 'line_number', 'tag', 'tier', 'category',
                'module', 'priority', 'date_tag', 'text'
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
        default='all',
        help='Output format (default: all)'
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
    parser.add_argument(
        '--src-only',
        action='store_true',
        help='Scan only src/code_scalpel (default: scan entire repo)'
    )
    parser.add_argument(
        '--roadmap',
        action='store_true',
        help='Generate comprehensive roadmap document'
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract TODOs
    extractor = TodoExtractor(src_only=args.src_only)
    print("Extracting TODO/FIXME/HACK items...")
    extractor.extract_todos()
    print(f"Found {len(extractor.todos)} items")

    # Generate reports
    if args.stats_only or args.format in ('markdown', 'all'):
        stats_report = extractor.generate_stats_report()
        stats_path = output_dir / 'TODO_STATISTICS.md'
        with open(stats_path, 'w') as f:
            f.write(stats_report)
        print(f"Statistics report: {stats_path}")

    if args.by_module or args.format in ('markdown', 'all'):
        module_report = extractor.generate_module_report()
        module_path = output_dir / 'TODO_BY_MODULE.md'
        with open(module_path, 'w') as f:
            f.write(module_report)
        print(f"Module report: {module_path}")
    
    if args.roadmap or args.format in ('markdown', 'all'):
        roadmap_report = extractor.generate_roadmap_report()
        roadmap_path = output_dir / 'TODO_ROADMAP.md'
        with open(roadmap_path, 'w') as f:
            f.write(roadmap_report)
        print(f"Roadmap report: {roadmap_path}")

    if args.format in ('json', 'all'):
        json_path = output_dir / 'todos.json'
        extractor.export_json(str(json_path))
        print(f"JSON export: {json_path}")

    if args.format in ('csv', 'all'):
        csv_path = output_dir / 'todos.csv'
        extractor.export_csv(str(csv_path))
        print(f"CSV export: {csv_path}")
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Total items: {len(extractor.todos)}")
    print(f"  TODO:  {extractor.stats.get('tag_TODO', 0)}")
    print(f"  FIXME: {extractor.stats.get('tag_FIXME', 0)}")
    print(f"  HACK:  {extractor.stats.get('tag_HACK', 0)}")
    print(f"  BUG:   {extractor.stats.get('tag_BUG', 0)}")
    print(f"  NOTE:  {extractor.stats.get('tag_NOTE', 0)}")
    print(f"\nBy Priority:")
    print(f"  Critical: {extractor.stats.get('priority_Critical', 0)}")
    print(f"  High:     {extractor.stats.get('priority_High', 0)}")
    print(f"  Medium:   {extractor.stats.get('priority_Medium', 0)}")
    print(f"  Low:      {extractor.stats.get('priority_Low', 0)}")


if __name__ == '__main__':
    main()
