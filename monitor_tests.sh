#!/bin/bash
# Monitor test execution progress
# Usage: ./monitor_tests.sh

LOG_FILE="/mnt/k/backup/Develop/code-scalpel/test_results_full.log"

echo "Monitoring test execution..."
echo "Log file: $LOG_FILE"
echo ""

# Check if tests are running
if pgrep -f "pytest tests/" > /dev/null; then
    echo "✓ Tests are currently running"
    echo ""
    
    # Show last 30 lines of output
    if [ -f "$LOG_FILE" ]; then
        echo "Recent output:"
        echo "----------------------------------------"
        tail -30 "$LOG_FILE"
        echo "----------------------------------------"
        echo ""
        echo "Tests collected:"
        grep "collected" "$LOG_FILE" | tail -1
        echo ""
        echo "Latest test:"
        grep "PASSED\|FAILED" "$LOG_FILE" | tail -5
    else
        echo "Log file not created yet..."
    fi
else
    echo "✗ Tests are not running"
    echo ""
    
    if [ -f "$LOG_FILE" ]; then
        echo "Final results:"
        echo "========================================
"
        grep -A 5 "short test summary\|passed.*failed\|warnings in" "$LOG_FILE" | tail -10
    else
        echo "No log file found"
    fi
fi
