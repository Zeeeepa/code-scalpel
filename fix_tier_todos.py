#!/usr/bin/env python3
"""
Bulk fix TIER TODO patterns to standard TODO [TIER]: format
"""

import re
import os
from pathlib import Path

def convert_tier_blocks_to_todos(content: str) -> str:
    """Convert TIER1/TIER2/TIER3 TODO blocks to individual TODO items."""
    
    # Pattern 1: [20251224_TIER1_TODO] FEATURE: description with dash-list items
    # Convert to: TODO [COMMUNITY][FEATURE]: description followed by TODO [COMMUNITY]: items
    def fix_tier_block_pattern(match):
        date_tag = match.group(1)  # 20251224
        tier_num = match.group(2)  # 1, 2, or 3
        tag_type = match.group(3)  # FEATURE, BUGFIX, ENHANCEMENT
        description = match.group(4)  # Feature description
        items = match.group(5)  # The dashed list or remaining content
        
        # Map tier numbers to tier names
        tier_map = {'1': 'COMMUNITY', '2': 'PRO', '3': 'ENTERPRISE'}
        tier_name = tier_map.get(tier_num, 'PRO')
        
        # Process the items list
        result_lines = [f"        TODO [{tier_name}][{tag_type}]: {description}"]
        
        # Extract dashed items
        if items:
            item_lines = items.strip().split('\n')
            for item_line in item_lines:
                # Remove leading "- " or "  - "
                clean_item = item_line.strip()
                if clean_item.startswith('- '):
                    clean_item = clean_item[2:].strip()
                if clean_item:
                    result_lines.append(f"        TODO [{tier_name}]: {clean_item}")
        
        return '\n'.join(result_lines)
    
    # Updated pattern to match the docstring format
    pattern = r'\[(\d{8})_TIER([123])_TODO\]\s+([A-Z]+):\s+([^\n]+)\n((?:\s{6,}-\s+[^\n]*\n)*)'
    content = re.sub(pattern, fix_tier_block_pattern, content)
    
    # Pattern 2: Handle remaining individual TIER TODO comments (lines without dashes)
    # [20251224_TIER2_TODO] FEATURE: description -> TODO [PRO][FEATURE]: description
    def fix_individual_tier(match):
        date_tag = match.group(1)
        tier_num = match.group(2)
        tag_type = match.group(3)
        description = match.group(4)
        
        tier_map = {'1': 'COMMUNITY', '2': 'PRO', '3': 'ENTERPRISE'}
        tier_name = tier_map.get(tier_num, 'PRO')
        
        return f"        TODO [{tier_name}][{tag_type}]: {description}"
    
    individual_pattern = r'\[\d{8}_TIER([123])_TODO\]\s+([A-Z]+):\s+([^\n]+)'
    content = re.sub(individual_pattern, fix_individual_tier, content)
    
    return content

def process_file(filepath: str) -> int:
    """Process a single file and return number of replacements made."""
    with open(filepath, 'r') as f:
        original = f.read()
    
    converted = convert_tier_blocks_to_todos(original)
    
    if original != converted:
        with open(filepath, 'w') as f:
            f.write(converted)
        
        # Count the number of changes
        changes = len(re.findall(r'\[202\d{4}_TIER', original)) - len(re.findall(r'\[202\d{4}_TIER', converted))
        return changes
    
    return 0

def main():
    ast_tools_dir = Path('src/code_scalpel/ast_tools')
    files_to_process = [
        'transformer.py',
        'type_inference.py',
        'utils.py',
        'validator.py',
        'visualizer.py',
        'call_graph.py',
        'cross_file_extractor.py',
        'control_flow.py'
    ]
    
    total_changes = 0
    for filename in files_to_process:
        filepath = ast_tools_dir / filename
        if filepath.exists():
            changes = process_file(str(filepath))
            if changes > 0:
                print(f"✓ {filename}: Fixed {changes} TIER TODO patterns")
                total_changes += changes
            else:
                print(f"- {filename}: No changes needed")
        else:
            print(f"✗ {filename}: File not found")
    
    print(f"\nTotal replacements: {total_changes}")

if __name__ == '__main__':
    main()
