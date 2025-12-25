"""
Security Analyzers - Core security analysis tools.

[20251225_FEATURE] Created as part of Project Reorganization Issue #8.

This module contains the core security analysis tools:
- security_analyzer.py: Main vulnerability detection engine
- taint_tracker.py: Data flow taint tracking
- unified_sink_detector.py: Polyglot sink detection
- cross_file_taint.py: Cross-file taint flow analysis
"""

from .security_analyzer import SecurityAnalyzer, SecurityAnalysisResult
from .taint_tracker import TaintTracker, TaintLevel, TaintInfo
from .unified_sink_detector import UnifiedSinkDetector, DetectedSink
from .cross_file_taint import CrossFileTaintTracker

__all__ = [
    # Security Analyzer
    "SecurityAnalyzer",
    "SecurityAnalysisResult",
    # Taint Tracker
    "TaintTracker",
    "TaintLevel",
    "TaintInfo",
    # Unified Sink Detector
    "UnifiedSinkDetector",
    "DetectedSink",
    # Cross-File Taint
    "CrossFileTaintTracker",
]
