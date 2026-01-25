# Code Scalpel Agents

Autonomous AI agent framework extensions for Code Scalpel - enabling code review, refactoring, testing, documentation, security analysis, metrics, and optimization agents.

## Installation

```bash
pip install codescalpel-agents
```

## Quick Start

```python
from codescalpel_agents.agents import CodeReviewAgent

agent = CodeReviewAgent()
review = await agent.observe_file("src/main.py")
```

## Features

- **7 Specialized Agents**: Review, Refactoring, Testing, Documentation, Security, Metrics, Optimization
- **Autonomous Error Fixing**: Automatically fixes issues found during analysis
- **Framework Integration**: Works with AutoGen, CrewAI, LangGraph
- **Enterprise Ready**: Built on Code Scalpel's enterprise-grade analysis engine

## Requires

- `codescalpel>=1.0.2` (core analysis engine)
- `pyautogen>=0.2.0` for AutoGen integration
- `crewai>=0.1.0` for CrewAI integration
- `langchain>=0.1.0` for LangChain integration
- `langgraph>=0.1.0` for LangGraph integration

## License

MIT
