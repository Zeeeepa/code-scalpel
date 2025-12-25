"""
Kafka Taint Tracking - Kafka message taint flow analysis.

[20251225_FEATURE] Created as part of Project Reorganization Phase 3.

This module provides Kafka producer/consumer taint tracking:
- taint_tracker.py: Kafka message taint flow analysis across producers and consumers
"""

from .taint_tracker import (
    KafkaTaintTracker,
    KafkaAnalysisResult,
    KafkaTaintBridge,
    KafkaTopicInfo,
    KafkaProducer,
    KafkaConsumer,
    KafkaLibrary,
    KafkaPatternType,
    KafkaRiskLevel,
)

__all__ = [
    "KafkaTaintTracker",
    "KafkaAnalysisResult",
    "KafkaTaintBridge",
    "KafkaTopicInfo",
    "KafkaProducer",
    "KafkaConsumer",
    "KafkaLibrary",
    "KafkaPatternType",
    "KafkaRiskLevel",
]
