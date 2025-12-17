"""
Example: Autonomy Audit Trail Usage

# [20251217_FEATURE] v3.0.0 Autonomy - Audit trail demonstration

This example demonstrates how to use the autonomy audit trail for
tracking autonomous operations with full traceability.
"""

import time
from datetime import datetime, timedelta
from code_scalpel.autonomy import AutonomyAuditTrail


def simulate_fix_loop():
    """
    Simulate an autonomous fix loop with nested operations.
    
    Demonstrates:
    - Parent-child operation tracking
    - Success and failure recording
    - Duration tracking
    - Metadata capture
    """
    print("=" * 70)
    print("AUTONOMY AUDIT TRAIL EXAMPLE")
    print("=" * 70)
    
    # Create audit trail
    audit = AutonomyAuditTrail()
    print(f"\nSession ID: {audit.current_session_id}")
    print(f"Storage Path: {audit.storage_path}\n")
    
    # Simulate Fix Loop 1: Syntax Error (Success)
    print("1. Simulating syntax error fix...")
    start_time = time.time()
    
    parent_id = audit.record(
        event_type="FIX_LOOP_START",
        operation="fix_syntax_error",
        input_data={
            "file": "example.py",
            "error": "SyntaxError: invalid syntax",
            "line": 42
        },
        output_data={
            "fixed": True,
            "changes": "Added missing colon"
        },
        success=True,
        duration_ms=int((time.time() - start_time) * 1000),
        metadata={"severity": "HIGH", "auto_fix": True}
    )
    
    print(f"   ✓ Parent operation recorded: {parent_id}")
    
    # Child operation 1: Error Analysis
    start_time = time.time()
    child1_id = audit.record(
        event_type="ERROR_ANALYSIS",
        operation="analyze_syntax_error",
        input_data={
            "error_message": "SyntaxError: invalid syntax",
            "code_context": "if x == 1\n    print('hello')"
        },
        output_data={
            "cause": "missing colon after if statement",
            "confidence": 0.95
        },
        success=True,
        duration_ms=int((time.time() - start_time) * 1000),
        parent_id=parent_id,
        metadata={"analyzer": "AST-based"}
    )
    print(f"   ✓ Child operation recorded: {child1_id}")
    
    # Child operation 2: Fix Generation
    start_time = time.time()
    child2_id = audit.record(
        event_type="FIX_GENERATION",
        operation="generate_fix",
        input_data={
            "cause": "missing colon",
            "line": 42
        },
        output_data={
            "fix": "if x == 1:",
            "diff": "+if x == 1:"
        },
        success=True,
        duration_ms=int((time.time() - start_time) * 1000),
        parent_id=parent_id
    )
    print(f"   ✓ Child operation recorded: {child2_id}")
    
    # Child operation 3: Sandbox Execution
    start_time = time.time()
    child3_id = audit.record(
        event_type="SANDBOX_EXECUTION",
        operation="verify_fix",
        input_data={
            "fixed_code": "if x == 1:\n    print('hello')"
        },
        output_data={
            "verified": True,
            "tests_passed": True
        },
        success=True,
        duration_ms=int((time.time() - start_time) * 1000),
        parent_id=parent_id
    )
    print(f"   ✓ Child operation recorded: {child3_id}\n")
    
    # Simulate Fix Loop 2: Complex Error (Failure)
    print("2. Simulating complex error fix (fails)...")
    start_time = time.time()
    
    parent2_id = audit.record(
        event_type="FIX_LOOP_START",
        operation="fix_type_error",
        input_data={
            "file": "complex.py",
            "error": "TypeError: unsupported operand type",
            "line": 100
        },
        output_data={
            "fixed": False,
            "reason": "Complex type inference required"
        },
        success=False,
        duration_ms=int((time.time() - start_time) * 1000),
        metadata={"severity": "MEDIUM", "escalated": True}
    )
    print(f"   ✗ Failed operation recorded: {parent2_id}\n")
    
    # Query operations
    print("3. Querying audit trail...")
    
    # Get operation trace
    print(f"\n   Operation trace for {parent_id}:")
    trace = audit.get_operation_trace(parent_id)
    for entry in trace:
        indent = "      " if entry.parent_id else "   "
        status = "✓" if entry.success else "✗"
        print(f"{indent}{status} {entry.event_type}: {entry.operation} ({entry.duration_ms}ms)")
    
    # Get session summary
    print("\n4. Session Summary:")
    summary = audit.get_session_summary()
    print(f"   Total Operations: {summary['total_operations']}")
    print(f"   Successful: {summary['successful']}")
    print(f"   Failed: {summary['failed']}")
    print(f"   Total Duration: {summary['total_duration_ms']}ms")
    print(f"   Event Types: {summary['event_types']}\n")
    
    # Export to different formats
    print("5. Exporting audit trail...")
    
    # JSON export
    json_export = audit.export(format="json")
    print(f"   ✓ JSON export: {len(json_export)} characters")
    
    # CSV export
    csv_export = audit.export(format="csv")
    print(f"   ✓ CSV export: {len(csv_export.splitlines())} lines")
    
    # HTML export
    html_export = audit.export(format="html")
    print(f"   ✓ HTML export: {len(html_export)} characters")
    
    # Filtered export
    success_only = audit.export(format="json", success_only=True)
    print(f"   ✓ Success-only export: {len(success_only)} characters\n")
    
    # Save reports
    print("6. Saving reports...")
    
    report_dir = audit.storage_path / audit.current_session_id / "reports"
    report_dir.mkdir(exist_ok=True)
    
    with open(report_dir / "audit_report.json", 'w') as f:
        f.write(json_export)
    print(f"   ✓ Saved JSON report to {report_dir / 'audit_report.json'}")
    
    with open(report_dir / "audit_report.csv", 'w') as f:
        f.write(csv_export)
    print(f"   ✓ Saved CSV report to {report_dir / 'audit_report.csv'}")
    
    with open(report_dir / "audit_report.html", 'w') as f:
        f.write(html_export)
    print(f"   ✓ Saved HTML report to {report_dir / 'audit_report.html'}")
    
    print("\n" + "=" * 70)
    print("EXAMPLE COMPLETE")
    print("=" * 70)
    print(f"\nView the HTML report in your browser:")
    print(f"file://{report_dir.absolute() / 'audit_report.html'}\n")


def demonstrate_filtering():
    """
    Demonstrate filtering capabilities.
    """
    print("\n" + "=" * 70)
    print("FILTERING DEMONSTRATION")
    print("=" * 70)
    
    audit = AutonomyAuditTrail()
    
    # Record various operations
    print("\n1. Recording operations with different types and statuses...")
    
    for i in range(3):
        audit.record(
            event_type="ERROR_ANALYSIS",
            operation=f"analyze_{i}",
            input_data={"error": f"error_{i}"},
            output_data={"cause": f"cause_{i}"},
            success=True,
            duration_ms=100 + i * 10
        )
    
    for i in range(2):
        audit.record(
            event_type="FIX_GENERATION",
            operation=f"generate_{i}",
            input_data={"cause": f"cause_{i}"},
            output_data={"fix": f"fix_{i}"},
            success=i == 0,  # First succeeds, second fails
            duration_ms=200 + i * 20
        )
    
    print("   ✓ Recorded 5 operations (3 analyses, 2 generations)")
    
    # Filter by event type
    print("\n2. Filter by event type (ERROR_ANALYSIS only):")
    filtered = audit.export(format="json", event_types=["ERROR_ANALYSIS"])
    import json
    data = json.loads(filtered)
    print(f"   Filtered operations: {len(data['operations'])}")
    
    # Filter by success
    print("\n3. Filter by success (successful only):")
    success_only = audit.export(format="json", success_only=True)
    data = json.loads(success_only)
    print(f"   Successful operations: {len(data['operations'])}")
    
    # Combined filters
    print("\n4. Combined filter (ERROR_ANALYSIS + successful):")
    combined = audit.export(
        format="json",
        event_types=["ERROR_ANALYSIS"],
        success_only=True
    )
    data = json.loads(combined)
    print(f"   Filtered operations: {len(data['operations'])}")
    
    print("\n" + "=" * 70)


def demonstrate_compliance_reporting():
    """
    Demonstrate compliance and debugging use cases.
    """
    print("\n" + "=" * 70)
    print("COMPLIANCE & DEBUGGING DEMONSTRATION")
    print("=" * 70)
    
    audit = AutonomyAuditTrail()
    
    print("\n1. Recording operations for compliance...")
    
    # Simulate a series of autonomous operations
    operations = [
        ("CODE_REVIEW", "review_pr", True, 450),
        ("SECURITY_SCAN", "scan_vulnerabilities", True, 2300),
        ("CODE_MODIFICATION", "apply_fix", True, 890),
        ("TEST_EXECUTION", "run_tests", False, 5600),
        ("ROLLBACK", "undo_changes", True, 120),
    ]
    
    for event_type, operation, success, duration in operations:
        audit.record(
            event_type=event_type,
            operation=operation,
            input_data={"timestamp": datetime.now().isoformat()},
            output_data={"completed": success},
            success=success,
            duration_ms=duration,
            metadata={"compliance": True, "auditor": "system"}
        )
    
    print(f"   ✓ Recorded {len(operations)} compliance events")
    
    # Generate compliance report
    print("\n2. Generating compliance report...")
    summary = audit.get_session_summary()
    
    print(f"\n   Compliance Summary:")
    print(f"   - Total Events: {summary['total_operations']}")
    print(f"   - Success Rate: {summary['successful'] / summary['total_operations'] * 100:.1f}%")
    print(f"   - Total Time: {summary['total_duration_ms']}ms")
    print(f"   - Event Breakdown:")
    for event_type, count in summary['event_types'].items():
        print(f"     • {event_type}: {count}")
    
    # Export for audit
    print("\n3. Exporting for external audit...")
    audit_export = audit.export(format="json")
    
    # Verify integrity
    print("\n4. Verifying data integrity...")
    entries = audit._load_entries()
    print(f"   ✓ All entries have input hashes: {all(e.input_hash for e in entries)}")
    print(f"   ✓ All entries have output hashes: {all(e.output_hash for e in entries)}")
    print(f"   ✓ All entries are timestamped: {all(e.timestamp for e in entries)}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run all demonstrations
    simulate_fix_loop()
    demonstrate_filtering()
    demonstrate_compliance_reporting()
    
    print("\n✓ All demonstrations complete!")
    print("\nKey Features Demonstrated:")
    print("  • Immutable audit entries with cryptographic hashes")
    print("  • Parent-child operation tracking")
    print("  • Multi-format export (JSON, CSV, HTML)")
    print("  • Filtering by time, type, and success")
    print("  • Operation tracing and session summaries")
    print("  • Compliance and debugging support")
