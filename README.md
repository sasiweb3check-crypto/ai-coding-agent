# AI Coding Agent

An autonomous AI coding agent powered by GitHub Copilot and GitHub Models that generates, builds, and runs code based on topics provided via GitHub Issues.

## Features

- **Autonomous Code Generation**: Generates optimal, production-ready code based on topics
- **Automatic Build & Execution**: Builds and runs code in a sandboxed environment
- **Full Observability**: Logs every step (reasoning, code generation, execution)
- **Multi-Language Support**: Generates code in Python, JavaScript, and more
- **Iterative Refinement**: Self-corrects errors and retries automatically
- **GitHub Integration**: Uses Issues for input, PRs for output, Actions for execution

## Architecture

```
Input (GitHub Issue) 
    ↓
Agent Core (GitHub Copilot/Models)
    ↓
Code Generation
    ↓
Execution (GitHub Actions/Shell)
    ↓
Observability (PR + Logs)
```

## Prerequisites

- GitHub Account with Copilot enabled
- GitHub CLI installed
- Access to GitHub Models (gpt-4o or equivalent)
- GitHub Actions enabled in repository

## Quick Start

1. Clone this repository
2. Configure secrets (see setup guide below)
3. Create an issue with title: `Topic: Your topic here`
4. Agent automatically triggers and logs progress

## Usage

### Create a Topic Issue

Create a new GitHub Issue with:
- **Title**: `Topic: Build a simple calculator in JavaScript`
- **Description**: Additional requirements (optional)

### Agent Execution

The workflow:
1. Detects new issue
2. Reads the topic
3. Generates optimal code
4. Builds and tests
5. Creates PR with results
6. Logs process for review

## Configuration

See [SETUP.md](docs/SETUP.md) for detailed configuration steps.

## Files

- `.github/workflows/code-agent.md` - Agent workflow definition (natural language)
- `.github/workflows/code-agent.lock.yml` - Generated workflow (YAML)
- `agent.py` - Python script for calling GitHub Models
- `scripts/` - Helper scripts for execution

## License

MIT
