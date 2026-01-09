#!/bin/bash
# Full test suite execution for v3.3.0 validation
# Created: 2025-01-09

cd /mnt/k/backup/Develop/code-scalpel

echo "=========================================="
echo "Code Scalpel v3.3.0 Full Test Suite"
echo "Started: $(date)"
echo "=========================================="
echo ""

# Run full test suite with coverage
pytest tests/ \
    --cov=src/code_scalpel \
    --cov-report=html \
    --cov-report=term-missing:skip-covered \
    --cov-report=json \
    -v \
    --tb=short \
    2>&1 | tee test_results_full.log

echo ""
echo "=========================================="
echo "Test Run Completed: $(date)"
echo "=========================================="
echo ""

# Extract summary
echo "Test Summary:"
grep -E "passed|failed|skipped|warnings" test_results_full.log | tail -3

echo ""
echo "Results saved to: test_results_full.log"
echo "Coverage HTML: htmlcov/index.html"
echo "Coverage JSON: coverage.json"
