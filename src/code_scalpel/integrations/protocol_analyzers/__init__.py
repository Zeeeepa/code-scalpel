"""
Protocol Analyzers - Framework and protocol-specific security analysis.

[20251225_FEATURE] Created as part of Project Reorganization Phase 3.

This module contains protocol-specific analyzers for tracking taint flow
and security issues across different frameworks and protocols:

Subdirectories:
    graphql/: GraphQL schema tracking and drift detection
    grpc/: gRPC contract analysis
    kafka/: Kafka message taint tracking
    schema/: Protocol buffer schema drift detection
    frontend/: Frontend input tracking (React, Vue, Angular)

Usage:
    from code_scalpel.integrations.protocol_analyzers.graphql import GraphQLSchemaTracker
    from code_scalpel.integrations.protocol_analyzers.grpc import GrpcContractAnalyzer
    from code_scalpel.integrations.protocol_analyzers.kafka import KafkaTaintTracker
    from code_scalpel.integrations.protocol_analyzers.schema import SchemaDriftDetector
    from code_scalpel.integrations.protocol_analyzers.frontend import FrontendInputTracker
"""

# [20251225_FEATURE] Re-export main classes from each subdirectory
from .graphql import GraphQLSchemaTracker, GraphQLSchema, GraphQLSchemaDrift
from .grpc import GrpcContractAnalyzer, GrpcContract, GrpcService
from .kafka import KafkaTaintTracker, KafkaAnalysisResult, KafkaTaintBridge
from .schema import SchemaDriftDetector, SchemaDriftResult, ProtobufSchema
from .frontend import FrontendInputTracker, FrontendAnalysisResult, InputSource

__all__ = [
    # GraphQL
    "GraphQLSchemaTracker",
    "GraphQLSchema",
    "GraphQLSchemaDrift",
    # gRPC
    "GrpcContractAnalyzer",
    "GrpcContract",
    "GrpcService",
    # Kafka
    "KafkaTaintTracker",
    "KafkaAnalysisResult",
    "KafkaTaintBridge",
    # Schema
    "SchemaDriftDetector",
    "SchemaDriftResult",
    "ProtobufSchema",
    # Frontend
    "FrontendInputTracker",
    "FrontendAnalysisResult",
    "InputSource",
]

__version__ = "1.0.0"
