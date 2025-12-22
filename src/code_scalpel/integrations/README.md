# Integrations Module

**Purpose:** External framework and API integrations

## Overview

This module provides integrations with:
- AI agent frameworks (AutoGen, CrewAI)
- REST API server for MCP tools
- Future: LangChain, Claude API (placeholders)

## Key Components

### rest_api_server.py (16,710 LOC)
REST API wrapper for MCP tools:
- `MCPServerConfig` - Server configuration
- `create_app()` - Flask app factory
- `run_server()` - Server launcher
- Exposes all 20 MCP tools as HTTP endpoints

**Endpoints:**
- `POST /analyze_code` - Analyze code structure
- `POST /extract_code` - Extract functions/classes
- `POST /security_scan` - Scan for vulnerabilities
- ... (20 total)

**Example:**
```python
from code_scalpel.integrations import create_app, run_server

# Create Flask app
app = create_app()

# Run server
run_server(port=8080, host="0.0.0.0")
```

### autogen.py (8,193 LOC)
AutoGen framework integration:
- `AutogenScalpel` - Wrapper class for AutoGen agents
- Tool registration for MCP functions
- Async execution support
- Multi-agent code analysis workflows

**Example:**
```python
from code_scalpel.integrations import AutogenScalpel
import autogen

scalpel = AutogenScalpel()
agent = autogen.AssistantAgent(
    name="CodeAnalyzer",
    llm_config={"tools": scalpel.get_tools()}
)
```

### crewai.py (20,465 LOC)
CrewAI framework integration:
- `CrewAIScalpel` - Wrapper for CrewAI crews
- Task definitions for code analysis
- Agent role definitions (Analyzer, Security Auditor, Refactorer)
- Multi-step analysis pipelines

**Example:**
```python
from code_scalpel.integrations import CrewAIScalpel
from crewai import Crew

scalpel = CrewAIScalpel()
crew = Crew(
    agents=scalpel.get_agents(),
    tasks=scalpel.get_tasks()
)
result = crew.kickoff()
```

### claude.py (Placeholder)
Future: Direct Claude API integration

### langchain.py (Placeholder)
Future: LangChain tool integration

## Usage Patterns

### REST API Server
```bash
# Start server
python -m code_scalpel.integrations.rest_api_server

# Make request
curl -X POST http://localhost:8080/analyze_code \
  -H "Content-Type: application/json" \
  -d '{"code": "def foo(): return 1"}'
```

### AutoGen Agent
```python
from code_scalpel.integrations import AutogenScalpel
import autogen

scalpel = AutogenScalpel()
assistant = autogen.AssistantAgent(
    name="CodeReviewer",
    system_message="You are a code reviewer using Code Scalpel tools",
    llm_config={"tools": scalpel.get_tools()}
)

user_proxy = autogen.UserProxyAgent(name="User")
user_proxy.initiate_chat(
    assistant,
    message="Analyze this file for security issues: app.py"
)
```

### CrewAI Crew
```python
from code_scalpel.integrations import CrewAIScalpel

scalpel = CrewAIScalpel()
crew = scalpel.create_analysis_crew()
result = crew.kickoff(inputs={"file_path": "src/main.py"})
```

## Integration

Used by:
- External AI frameworks (AutoGen, CrewAI)
- HTTP clients (curl, Postman, frontend apps)
- CI/CD pipelines (GitHub Actions, Jenkins)

## v3.0.5 Status

- REST API: Stable, 100% coverage
- AutoGen: Beta, 80% coverage
- CrewAI: Beta, 75% coverage
- Claude/LangChain: Planned for v3.1.0
