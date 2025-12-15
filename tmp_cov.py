"""Utility to summarize coverage gaps from the latest XML report."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple


# [20251214_TEST] Inspect release coverage to target largest gaps for additional tests.
def load_coverage(path: Path) -> ET.Element:
    """Load coverage XML and return the root element."""

    return ET.parse(path).getroot()


def collect_misses(
    root: ET.Element, limit: int = 15
) -> List[Tuple[int, str, float, List[int]]]:
    """Return the top files with uncovered lines along with sample line numbers."""

    misses: List[Tuple[int, str, float, List[int]]] = []
    for cls in root.findall(".//class"):
        uncovered = [
            int(line.attrib["number"])
            for line in cls.findall("./lines/line")
            if int(line.attrib["hits"]) == 0
        ]
        if uncovered:
            misses.append(
                (
                    len(uncovered),
                    cls.attrib["filename"],
                    float(cls.attrib.get("line-rate", 0)),
                    uncovered[:30],
                )
            )

    misses.sort(reverse=True)
    return misses[:limit]


def main() -> None:
    coverage_path = Path("release_artifacts/v1.5.4/coverage_20251214.xml")
    root = load_coverage(coverage_path)
    total_line_rate = float(root.attrib["line-rate"]) * 100
    print(f"line coverage: {total_line_rate:.2f}%")
    for count, fname, lr, sample in collect_misses(root):
        print(f"{fname:60} misses={count:4d} line_rate={lr:.3f} sample={sample}")

    targets = {
        "code_scalpel/code_analyzer.py",
        "code_scalpel/ast_tools/cross_file_extractor.py",
        "code_scalpel/ir/normalizers/javascript_normalizer.py",
    }

    for cls in root.findall(".//class"):
        if cls.attrib.get("filename") not in targets:
            continue

        missing = [
            int(line.attrib["number"])
            for line in cls.findall("./lines/line")
            if int(line.attrib["hits"]) == 0
        ]
        if missing:
            print(f"\n{cls.attrib['filename']} missing lines: {missing}")


if __name__ == "__main__":
    main()
