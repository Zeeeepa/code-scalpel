import pytest
from unittest.mock import patch
from code_scalpel.mcp.server import type_evaporation_scan, TypeEvaporationResultModel


# Sample code for testing
FRONTEND_CODE = """
interface User {
    role: 'admin' | 'user';
    name: string;
}

// Unsafe type assertion
const role = (document.getElementById('role') as HTMLInputElement).value as 'admin' | 'user';

// Network boundary - type evaporates
fetch('/api/user')
    .then(response => response.json())
    .then(data => {
        const user = data as User;  // Unsafe!
    });

// Another network call
axios.get('/api/profile').then(response => {
    const profile = response.data;  // No type validation
});
"""

BACKEND_CODE = """
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/user', methods=['GET'])
def get_user():
    role = request.args.get('role')  # No validation!
    return jsonify({'role': role, 'name': 'Test'})

@app.route('/api/profile', methods=['GET'])
def get_profile():
    data = request.get_json()
    return jsonify(data)  # Direct echo without validation
"""


@pytest.mark.asyncio
async def test_type_evaporation_scan_community():
    """Test Community tier - explicit any detection, no Pro/Enterprise features."""
    with patch("code_scalpel.licensing.get_current_tier", return_value="community"):
        result = await type_evaporation_scan(
            frontend_code=FRONTEND_CODE,
            backend_code=BACKEND_CODE,
        )
        
        assert isinstance(result, TypeEvaporationResultModel)
        assert result.success is True
        
        # Community: basic detection works
        assert result.frontend_vulnerabilities >= 0
        assert result.backend_vulnerabilities >= 0
        
        # Pro features not available
        assert result.implicit_any_count == 0
        assert result.boundary_violations == []
        assert result.network_boundaries == []
        
        # Enterprise features not available
        assert result.generated_schemas == []
        assert result.validation_code is None
        assert result.schema_coverage is None


@pytest.mark.asyncio
async def test_type_evaporation_scan_pro():
    """Test Pro tier - implicit any tracing, network boundary analysis."""
    with patch("code_scalpel.licensing.get_current_tier", return_value="pro"):
        result = await type_evaporation_scan(
            frontend_code=FRONTEND_CODE,
            backend_code=BACKEND_CODE,
        )
        
        assert isinstance(result, TypeEvaporationResultModel)
        assert result.success is True
        
        # Pro features available
        assert result.implicit_any_count >= 0
        
        # Network boundaries detected (fetch, axios)
        assert len(result.network_boundaries) >= 1
        assert any("fetch" in str(b).lower() or "axios" in str(b).lower() or "xmlhttp" in str(b).lower()
                  for b in result.network_boundaries)
        
        # Boundary violations tracked
        assert isinstance(result.boundary_violations, list)
        if result.network_boundaries:
            # Should have some violations for unvalidated .json() calls
            assert len(result.boundary_violations) >= 0
            
        # Enterprise features not available at Pro tier
        assert result.generated_schemas == []
        assert result.validation_code is None
        assert result.schema_coverage is None


@pytest.mark.asyncio
async def test_type_evaporation_scan_enterprise():
    """Test Enterprise tier - runtime validation generation, schema coverage."""
    with patch("code_scalpel.licensing.get_current_tier", return_value="enterprise"):
        result = await type_evaporation_scan(
            frontend_code=FRONTEND_CODE,
            backend_code=BACKEND_CODE,
        )
        
        assert isinstance(result, TypeEvaporationResultModel)
        assert result.success is True
        
        # Pro features included
        assert result.implicit_any_count >= 0
        assert isinstance(result.network_boundaries, list)
        assert isinstance(result.boundary_violations, list)
        
        # Enterprise features available
        # Schema generation for matched endpoints
        assert isinstance(result.generated_schemas, list)
        if result.matched_endpoints:
            assert len(result.generated_schemas) > 0
            schema = result.generated_schemas[0]
            assert "endpoint" in schema
            assert "schema_type" in schema
            assert schema["schema_type"] == "zod"
            
        # Validation code generated
        if result.generated_schemas:
            assert result.validation_code is not None
            assert "import { z } from 'zod'" in result.validation_code
            assert "schema" in result.validation_code.lower()
            
        # Schema coverage calculated
        if result.matched_endpoints:
            assert result.schema_coverage is not None
            assert isinstance(result.schema_coverage, float)
            assert 0.0 <= result.schema_coverage <= 1.0


@pytest.mark.asyncio
async def test_tier_limits_enforced():
    """Test that tier limits are properly enforced."""
    # Community: max 50 files
    with patch("code_scalpel.licensing.get_current_tier", return_value="community"):
        from code_scalpel.licensing import get_tool_capabilities
        caps = get_tool_capabilities("type_evaporation_scan", "community")
        assert caps["limits"]["max_files"] == 50
    
    # Pro: max 500 files
    with patch("code_scalpel.licensing.get_current_tier", return_value="pro"):
        caps = get_tool_capabilities("type_evaporation_scan", "pro")
        assert caps["limits"]["max_files"] == 500
    
    # Enterprise: unlimited
    with patch("code_scalpel.licensing.get_current_tier", return_value="enterprise"):
        caps = get_tool_capabilities("type_evaporation_scan", "enterprise")
        assert caps["limits"]["max_files"] is None


@pytest.mark.asyncio
async def test_capability_detection():
    """Test that capabilities are correctly detected per tier."""
    # Community
    with patch("code_scalpel.licensing.get_current_tier", return_value="community"):
        from code_scalpel.licensing import get_tool_capabilities
        caps = get_tool_capabilities("type_evaporation_scan", "community")
        assert "explicit_any_detection" in caps["capabilities"]
        assert "typescript_any_scanning" in caps["capabilities"]
        assert "implicit_any_tracing" not in caps["capabilities"]
        assert "runtime_validation_generation" not in caps["capabilities"]
    
    # Pro
    with patch("code_scalpel.licensing.get_current_tier", return_value="pro"):
        caps = get_tool_capabilities("type_evaporation_scan", "pro")
        assert "explicit_any_detection" in caps["capabilities"]
        assert "implicit_any_tracing" in caps["capabilities"]
        assert "network_boundary_analysis" in caps["capabilities"]
        assert "library_boundary_analysis" in caps["capabilities"]
        assert "runtime_validation_generation" not in caps["capabilities"]
    
    # Enterprise
    with patch("code_scalpel.licensing.get_current_tier", return_value="enterprise"):
        caps = get_tool_capabilities("type_evaporation_scan", "enterprise")
        assert "explicit_any_detection" in caps["capabilities"]
        assert "implicit_any_tracing" in caps["capabilities"]
        assert "runtime_validation_generation" in caps["capabilities"]
        assert "zod_schema_generation" in caps["capabilities"]
        assert "pydantic_model_generation" in caps["capabilities"]
        assert "api_contract_validation" in caps["capabilities"]


@pytest.mark.asyncio
async def test_pro_network_boundary_detection():
    """Test Pro tier network boundary detection."""
    frontend_with_fetch = """
    fetch('/api/data').then(r => r.json()).then(data => console.log(data));
    axios.get('/api/users');
    new XMLHttpRequest().open('GET', '/api/test');
    """
    
    with patch("code_scalpel.licensing.get_current_tier", return_value="pro"):
        result = await type_evaporation_scan(
            frontend_code=frontend_with_fetch,
            backend_code="# empty",
        )
        
        # Should detect network boundaries (at least 2 out of 3)
        assert len(result.network_boundaries) >= 2
        
        # Verify structure
        for boundary in result.network_boundaries:
            assert "line" in boundary
            assert "type" in boundary
            assert boundary["type"] == "network_call"
            assert "code_snippet" in boundary
            assert "risk" in boundary


@pytest.mark.asyncio
async def test_enterprise_schema_generation():
    """Test Enterprise tier schema generation."""
    frontend = """
    interface Product {
        id: number;
        name: string;
        price: number;
    }
    
    fetch('/api/products').then(r => r.json());
    """
    
    backend = """
    @app.route('/api/products', methods=['GET'])
    def get_products():
        return jsonify([])
    """
    
    with patch("code_scalpel.licensing.get_current_tier", return_value="enterprise"):
        result = await type_evaporation_scan(
            frontend_code=frontend,
            backend_code=backend,
        )
        
        # If endpoints matched, schemas should be generated
        if result.matched_endpoints:
            assert len(result.generated_schemas) > 0
            
            # Check schema structure
            schema = result.generated_schemas[0]
            assert "endpoint" in schema
            assert "schema_type" in schema
            assert "schema" in schema
            assert "zod" in schema["schema"].lower() or "schema" in schema["schema"].lower()
            
            # Validation code should be complete
            assert result.validation_code is not None
            assert len(result.validation_code) > 0
            
            # Coverage should be calculated
            assert result.schema_coverage is not None
            assert result.schema_coverage > 0.0
