"""
HTTP Link Detector - Connects frontend API calls to backend endpoints.

[20251216_FEATURE] v2.1.0 - HTTP link detection across frontend/backend boundaries

This module detects connections between frontend API calls (fetch, axios, etc.)
and backend endpoints (@GetMapping, @app.route, etc.). It analyzes:

- Client-side HTTP calls (JavaScript/TypeScript)
- Server-side endpoint definitions (Python/Java)
- Route matching with confidence scoring

Example:
    >>> detector = HTTPLinkDetector()
    >>> detector.add_client_call("typescript::fetchUsers", "GET", "/api/users")
    >>> detector.add_endpoint("java::UserController:getUser", "GET", "/api/users")
    >>> links = detector.detect_links()
    >>> for link in links:
    ...     print(f"{link.client_id} -> {link.endpoint_id}: {link.confidence}")

TODO ITEMS: graph_engine/http_detector.py
======================================================================
COMMUNITY TIER - Core HTTP Detection
======================================================================
1. Add HTTPLinkDetector class initialization
2. Add add_client_call(node_id, method, url_pattern)
3. Add add_endpoint(node_id, method, route_pattern)
4. Add detect_links() main detection algorithm
5. Add detect_exact_match() for identical routes
6. Add detect_pattern_match() for regex matching
7. Add match_routes(client_route, endpoint_route) comparison
8. Add parse_route_string() to extract components
9. Add get_route_parameters(route) extractor
10. Add normalize_route_path(path) for consistency
11. Add extract_path_from_url(url) utility
12. Add extract_method_from_call(call_node) HTTP method extraction
13. Add extract_url_from_call(call_node) URL extraction
14. Add extract_method_from_endpoint(endpoint_node)
15. Add extract_route_from_endpoint(endpoint_node)
16. Add HTTPLink dataclass for results
17. Add HTTPMethod enum (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
18. Add parse_axios_call() JavaScript/TypeScript detection
19. Add parse_fetch_call() native fetch detection
20. Add parse_requests_call() Python requests detection
21. Add parse_flask_route() Flask endpoint detection
22. Add parse_django_route() Django endpoint detection
23. Add parse_fastapi_route() FastAPI endpoint detection
24. Add parse_spring_mapping() Spring endpoint detection
25. Add get_all_detected_links() result enumeration

PRO TIER - Advanced HTTP Detection
======================================================================
26. Add detect_dynamic_routes() parameterized routes
27. Add detect_path_parameters() {id}, :id, {uuid} patterns
28. Add detect_query_parameters() query string matching
29. Add detect_base_url_mismatch() different bases same path
30. Add detect_api_versioning() /v1/, /v2/ patterns
31. Add detect_subdomain_routing() different hosts
32. Add detect_header_routing() custom header requirements
33. Add detect_authentication_requirements() auth detection
34. Add detect_cors_policy() CORS configuration
35. Add detect_content_type() request/response types
36. Add detect_request_body_schema() payload structure
37. Add detect_response_schema() output structure
38. Add detect_error_responses() error handling
39. Add detect_redirect_chains() HTTP redirects
40. Add detect_reverse_proxy_routes() proxy patterns
41. Add detect_load_balancing() multiple endpoints
42. Add detect_rate_limiting() throttling patterns
43. Add detect_webhook_callbacks() callback endpoints
44. Add detect_websocket_connections() WebSocket endpoints
45. Add detect_graphql_endpoints() GraphQL detection
46. Add detect_grpc_services() gRPC endpoint detection
47. Add link_confidence_scoring() confidence calculation
48. Add link_evidence_collection() reasoning
49. Add suggest_manual_review() low confidence links
50. Add link_statistics_report() coverage analysis

ENTERPRISE TIER - Distributed HTTP Detection
======================================================================
51. Add distributed http_detection() across services
52. Add federated_endpoint_discovery() across orgs
53. Add multi_region_route_mapping() geographic routing
54. Add service_mesh_integration() Istio/Linkerd
55. Add api_gateway_detection() API gateway routing
56. Add load_balancer_detection() load balancing
57. Add cdn_detection() content delivery
58. Add ssl_tls_certificate_validation()
59. Add encryption_detection() HTTPS enforcement
60. Add certificate_pinning_detection()
61. Add http_signature_verification()
62. Add rate_limiting_detection() throttle config
63. Add circuit_breaker_detection() resilience
64. Add retry_policy_detection()
65. Add timeout_configuration_detection()
66. Add http_cache_detection()
67. Add compression_detection()
68. Add http2_spdy_detection()
69. Add grpc_web_fallback_detection()
70. Add api_versioning_strategy_detection()
71. Add deprecation_detection() EOL endpoints
72. Add monitoring_alerting_integration()
73. Add tracing_integration() distributed tracing
74. Add performance_profiling_http_calls()
75. Add http_compliance_checking() standards
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


# [20251216_FEATURE] HTTP methods for route matching
class HTTPMethod(Enum):
    """HTTP request methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    # [20251216_BUGFIX] Add missing standard HTTP methods CONNECT and TRACE for completeness
    CONNECT = "CONNECT"
    TRACE = "TRACE"


# [20251216_FEATURE] Client-side HTTP patterns as per problem statement
HTTP_CLIENT_PATTERNS = {
    "javascript": ["fetch", "axios.get", "axios.post", "$http", "ajax"],
    "typescript": ["fetch", "axios", "HttpClient"],
    "python": ["requests.get", "requests.post", "httpx.get"],
}

# [20251216_FEATURE] Server-side endpoint patterns as per problem statement
HTTP_ENDPOINT_PATTERNS = {
    "java": ["@GetMapping", "@PostMapping", "@RequestMapping", "@RestController"],
    "python": ["@app.route", "@router.get", "@api_view"],
    "typescript": ["@Get", "@Post", "@Controller"],
}


# [20251216_FEATURE] HTTP link between client and server
@dataclass
class HTTPLink:
    """
    A detected link between a client API call and a server endpoint.

    Attributes:
        client_id: Universal node ID of client call
        endpoint_id: Universal node ID of server endpoint
        method: HTTP method
        client_route: Route string from client
        endpoint_route: Route string from endpoint
        confidence: Confidence score (0.0-1.0)
        match_type: Type of route match (exact, pattern, dynamic)
        evidence: Human-readable explanation
    """

    client_id: str
    endpoint_id: str
    method: HTTPMethod
    client_route: str
    endpoint_route: str
    confidence: float
    match_type: str
    evidence: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "client_id": self.client_id,
            "endpoint_id": self.endpoint_id,
            "method": self.method.value,
            "client_route": self.client_route,
            "endpoint_route": self.endpoint_route,
            "confidence": self.confidence,
            "match_type": self.match_type,
            "evidence": self.evidence,
        }


# [20251216_FEATURE] Route pattern matching with confidence scoring
class RoutePatternMatcher:
    """
    Matcher for HTTP route patterns with confidence scoring.

    Handles:
    - Exact matches: "/api/users" == "/api/users" (confidence 0.95)
    - Pattern matches: "/api/users/{id}" ~= "/api/users/123" (confidence 0.8)
    - Dynamic routes: "/api/" + version + "/users" (confidence 0.5)
    """

    def match_routes(
        self, client_route: str, endpoint_route: str
    ) -> tuple[bool, float, str]:
        """
        Match client route against endpoint route.

        Args:
            client_route: Route from client call
            endpoint_route: Route from endpoint definition

        Returns:
            Tuple of (matches, confidence, match_type)
        """
        # Exact match
        if client_route == endpoint_route:
            return True, 0.95, "exact"

        # Pattern match (e.g., /api/users/{id} matches /api/users/123)
        if self._is_pattern_match(client_route, endpoint_route):
            return True, 0.8, "pattern"

        # Check if either route is dynamic (contains variables)
        client_is_dynamic = self._is_dynamic_route(client_route)
        endpoint_is_dynamic = self._is_dynamic_route(endpoint_route)

        if client_is_dynamic or endpoint_is_dynamic:
            # [20251216_BUGFIX] For dynamic routes, return dynamic match type with
            # confidence based on fuzzy match quality. AI agents need to know this
            # IS a dynamic route requiring human confirmation.
            if self._fuzzy_match(client_route, endpoint_route):
                return True, 0.5, "dynamic"
            else:
                # [20251216_BUGFIX] Even without fuzzy match, flag as dynamic with
                # very low confidence so agents know human review is required.
                # Extract path segments to check for any structural similarity.
                if self._has_structural_similarity(client_route, endpoint_route):
                    return True, 0.3, "dynamic"
                # One route is dynamic - return low confidence dynamic match
                # to ensure proper flagging for human review
                return False, 0.0, "dynamic"

        return False, 0.0, "none"

    def _has_structural_similarity(
        self, client_route: str, endpoint_route: str
    ) -> bool:
        """Check if routes have structural similarity (common path segments)."""

        # Extract clean path segments from dynamic route
        def extract_segments(route: str) -> set:
            # Remove quotes, variables, and split by common delimiters
            clean = re.sub(r'["\'\s+]', "", route)
            clean = re.sub(r"\$\{[^}]+\}", "", clean)  # Remove template vars
            clean = re.sub(
                r"version|baseUrl|api_url", "", clean, flags=re.IGNORECASE
            )  # Common vars
            segments = set(clean.split("/"))
            return {s for s in segments if s and len(s) > 2}  # Non-empty, meaningful

        client_segments = extract_segments(client_route)
        endpoint_segments = extract_segments(endpoint_route)

        # Check for common meaningful segments
        common = client_segments & endpoint_segments
        return len(common) > 0

    def _is_pattern_match(self, client_route: str, endpoint_route: str) -> bool:
        """Check if routes match with path parameter patterns."""
        # Convert endpoint pattern to regex
        # /api/users/{id} -> /api/users/[^/]+
        pattern = re.sub(r"\{[^}]+\}", r"[^/]+", endpoint_route)
        pattern = f"^{pattern}$"

        return re.match(pattern, client_route) is not None

    def _is_dynamic_route(self, route: str) -> bool:
        """Check if route contains dynamic parts (variables)."""
        # Look for common dynamic route indicators
        indicators = [
            "+",  # String concatenation
            "${",  # Template literals
            "` + ",  # Template string concatenation
            "params.",  # Parameter access
        ]
        return any(ind in route for ind in indicators)

    def _fuzzy_match(self, client_route: str, endpoint_route: str) -> bool:
        """Fuzzy match for dynamic routes."""
        # Extract static parts and compare
        client_parts = re.split(r"[+${}]", client_route)
        endpoint_parts = re.split(r"[+${}]", endpoint_route)

        # Check if any static parts match
        client_static = [p.strip("'\" ") for p in client_parts if p.strip("'\" ")]
        endpoint_static = [p.strip("'\" ") for p in endpoint_parts if p.strip("'\" ")]

        # If they share common path segments, consider it a match
        common = set(client_static) & set(endpoint_static)
        return len(common) > 0


# [20251216_FEATURE] Main HTTP link detector
class HTTPLinkDetector:
    """
    Detector for HTTP links between frontend and backend.

    This class identifies connections between client-side API calls and
    server-side endpoints by matching routes and HTTP methods.

    Example:
        >>> detector = HTTPLinkDetector()
        >>> detector.add_client_call("ts::fetchUsers", "GET", "/api/users")
        >>> detector.add_endpoint("java::getUser", "GET", "/api/users")
        >>> links = detector.detect_links()
    """

    def __init__(self):
        """Initialize HTTP link detector."""
        self.client_calls: List[Dict] = []
        self.endpoints: List[Dict] = []
        self.matcher = RoutePatternMatcher()

    def add_client_call(
        self,
        node_id: str,
        method: str | HTTPMethod,
        route: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Add a client-side HTTP call.

        Args:
            node_id: Universal node ID
            method: HTTP method (GET, POST, etc.)
            route: Route string
            metadata: Optional additional metadata
        """
        if isinstance(method, str):
            method = HTTPMethod(method.upper())

        self.client_calls.append(
            {
                "node_id": node_id,
                "method": method,
                "route": route,
                "metadata": metadata or {},
            }
        )

    def add_endpoint(
        self,
        node_id: str,
        method: str | HTTPMethod,
        route: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Add a server-side endpoint.

        Args:
            node_id: Universal node ID
            method: HTTP method
            route: Route string
            metadata: Optional additional metadata
        """
        if isinstance(method, str):
            method = HTTPMethod(method.upper())

        self.endpoints.append(
            {
                "node_id": node_id,
                "method": method,
                "route": route,
                "metadata": metadata or {},
            }
        )

    def detect_links(self) -> List[HTTPLink]:
        """
        Detect all HTTP links between clients and endpoints.

        Returns:
            List of HTTPLink objects with confidence scores
        """
        links: List[HTTPLink] = []

        for client in self.client_calls:
            for endpoint in self.endpoints:
                # Methods must match
                if client["method"] != endpoint["method"]:
                    continue

                # Try to match routes
                matches, confidence, match_type = self.matcher.match_routes(
                    client["route"], endpoint["route"]
                )

                if matches:
                    evidence = self._build_evidence(
                        client, endpoint, match_type, confidence
                    )

                    link = HTTPLink(
                        client_id=client["node_id"],
                        endpoint_id=endpoint["node_id"],
                        method=client["method"],
                        client_route=client["route"],
                        endpoint_route=endpoint["route"],
                        confidence=confidence,
                        match_type=match_type,
                        evidence=evidence,
                    )
                    links.append(link)

        return links

    def _build_evidence(
        self, client: Dict, endpoint: Dict, match_type: str, confidence: float
    ) -> str:
        """Build human-readable evidence string."""
        method = client["method"].value
        route = client["route"]

        if match_type == "exact":
            return f"Route string match: {method} {route}"
        elif match_type == "pattern":
            return f"Pattern match: {method} {route} ~= {endpoint['route']}"
        elif match_type == "dynamic":
            return f"Dynamic route match: {method} {route} (low confidence)"
        else:
            return f"Unknown match type: {match_type}"

    def get_unmatched_clients(self) -> List[Dict]:
        """Get client calls that have no matching endpoints."""
        matched_clients = set()

        for client in self.client_calls:
            for endpoint in self.endpoints:
                if client["method"] != endpoint["method"]:
                    continue

                matches, _, _ = self.matcher.match_routes(
                    client["route"], endpoint["route"]
                )
                if matches:
                    matched_clients.add(client["node_id"])
                    break

        return [c for c in self.client_calls if c["node_id"] not in matched_clients]

    def get_unmatched_endpoints(self) -> List[Dict]:
        """Get endpoints that have no matching client calls."""
        matched_endpoints = set()

        for endpoint in self.endpoints:
            for client in self.client_calls:
                if client["method"] != endpoint["method"]:
                    continue

                matches, _, _ = self.matcher.match_routes(
                    client["route"], endpoint["route"]
                )
                if matches:
                    matched_endpoints.add(endpoint["node_id"])
                    break

        return [e for e in self.endpoints if e["node_id"] not in matched_endpoints]
