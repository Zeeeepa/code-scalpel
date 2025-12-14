# Docker Build Summary - v1.5.0 Release

**Date:** December 13, 2025  
**Version:** code-scalpel v1.5.0 "Project Intelligence"  
**Build Status:** ✅ SUCCESS

---

## Build Results

### Container Images Created

| Image | Tag | Size | Status |
|-------|-----|------|--------|
| code-scalpel-mcp-server | latest | 306MB | ✅ Built |
| code-scalpel-rest-api | latest | 306MB | ✅ Built |

### Build Details

**Build Command:**
```bash
docker compose build --no-cache
```

**Build Time:** ~103 seconds total
- Multi-stage build (builder + production)
- No cached layers to ensure latest code
- Python 3.10-slim base images

### Included Components

✅ **MCP Server** (code-scalpel-mcp-server)
- Python 3.10-slim base
- Code Scalpel v1.5.0 package
- All dependencies from requirements.txt
- MCP HTTP transport (streamable-http)
- Port: 8593
- Health check enabled

✅ **REST API Server** (code-scalpel-rest-api)
- Python 3.10-slim base
- Flask-based REST API
- Code Scalpel v1.5.0 package
- Dependencies from Dockerfile.rest
- Port: 5000
- Health check enabled

---

## v1.5.0 Features Included

### New MCP Tools (3)
- ✅ `get_project_map` - Project structure analysis with language breakdown
- ✅ `get_call_graph` - Call graph generation and execution flow tracing
- ✅ `scan_dependencies` - Vulnerability scanning using OSV API

### Enhanced Features
- ✅ Language breakdown detection (9 file types)
- ✅ Entry point auto-detection (main, CLI, web frameworks)
- ✅ Circular import detection and reporting
- ✅ Performance optimizations (1.55s for 500-file projects)

### Test Coverage
- 203 v1.5.0 tests (100% passing)
- 2,045 total tests in suite
- 95%+ coverage on new modules
- 83% project-wide coverage (healthy baseline)

---

## Usage

### Start Both Services

```bash
docker compose up -d
```

This starts:
- MCP Server on http://localhost:8593
- REST API Server on http://localhost:5000

### Start Only MCP Server

```bash
docker compose up -d mcp-server
```

### Start Only REST API Server

```bash
docker compose up -d rest-api
```

### Health Checks

**MCP Server:**
```bash
curl http://localhost:8593/sse \
  -H "Accept: text/event-stream"
```

**REST API Server:**
```bash
curl http://localhost:5000/health
```

### View Logs

```bash
docker compose logs -f mcp-server
docker compose logs -f rest-api
```

### Stop Services

```bash
docker compose down
```

---

## Environment Variables

### MCP Server

- `SCALPEL_ROOT` - Project root directory (default: `/app/code`)
- `PYTHONUNBUFFERED=1` - Disable output buffering

### REST API Server

- `FLASK_ENV=production` - Flask environment (set to development for debugging)

### Customization

Edit `docker-compose.yml` to modify:
- Port mappings
- Volume mounts
- Environment variables
- Restart policies

Example: Mount local code directory
```yaml
mcp-server:
  volumes:
    - /path/to/your/code:/app/code
```

---

## Container Specifications

### MCP Server (code-scalpel-mcp-server)

```dockerfile
Image: python:3.10-slim
Size: 306MB (compressed)
Ports: 8593 (default)
Health Check: Every 30s
Command: code-scalpel mcp --http --host 0.0.0.0 --port 8593
```

### REST API Server (code-scalpel-rest-api)

```dockerfile
Image: python:3.10-slim
Size: 306MB (compressed)
Ports: 5000 (Flask default)
Health Check: Every 30s
Command: python -m code_scalpel.rest_server
```

---

## Network Configuration

Both containers connect to the nginx-proxy-manager network (if available) for load balancing.

To override, edit `docker-compose.yml`:
```yaml
networks:
  default:
    name: code-scalpel-network
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs mcp-server

# Rebuild without cache
docker compose build --no-cache
```

### Port Already in Use

Change ports in `docker-compose.yml`:
```yaml
ports:
  - "8595:8593"  # Map external 8595 to container 8593
```

### Health Check Failing

```bash
# Manual health check
docker exec code-scalpel-mcp curl http://localhost:8593/sse \
  -H "Accept: text/event-stream"

# Increase start_period if too short
healthcheck:
  start_period: 30s  # Increase if needed
```

---

## Performance Notes

- **MCP Server startup:** ~5-10 seconds
- **REST API startup:** ~3-5 seconds
- **Project analysis (500 files):** ~1.55 seconds
- **Memory usage:** ~150-200MB per service
- **Disk usage:** ~306MB per image

---

## Next Steps for Team

### For v1.5.1 Development

1. **Clone the repository** with latest code
2. **Review** [docs/internal/v1.5.1_TECHNICAL_PLAN.md](../docs/internal/v1.5.1_TECHNICAL_PLAN.md)
3. **Start development** on 3 components:
   - Import Resolution Engine (days 1-5)
   - Cross-File Extraction (days 6-10)
   - Cross-File Taint Tracking (days 11-15)

### Development Setup

```bash
# Clone repo
git clone https://github.com/tescolopio/code-scalpel.git
cd code-scalpel

# Setup development environment
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/test_*.py -v

# Or use Docker for isolation
docker compose exec mcp-server bash
```

### Documentation

- **Release Notes:** [RELEASE_NOTES_v1.5.0.md](../docs/release_notes/RELEASE_NOTES_v1.5.0.md)
- **Technical Plan:** [v1.5.1_TECHNICAL_PLAN.md](../docs/internal/v1.5.1_TECHNICAL_PLAN.md)
- **Development Roadmap:** [DEVELOPMENT_ROADMAP.md](../DEVELOPMENT_ROADMAP.md)
- **API Reference:** [docs/api_reference.md](../docs/api_reference.md)

---

## Version Information

**Code Scalpel Version:** 1.5.0 "Project Intelligence"
**Release Date:** December 13, 2025
**Build Date:** December 13, 2025
**Python Version:** 3.10
**Status:** Production Ready

---

## Support

For issues or questions:
1. Check [DEVELOPMENT_ROADMAP.md](../DEVELOPMENT_ROADMAP.md) for acceptance criteria
2. Review [docs/](../docs/) for detailed documentation
3. Check [examples/](../examples/) for usage examples
4. Run tests to verify functionality: `pytest tests/ -v`

