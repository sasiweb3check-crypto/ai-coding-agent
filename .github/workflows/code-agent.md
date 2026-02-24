---
on: 
  issues: 
    types: [opened]

permissions: 
  contents: write
  issues: write
  pull-requests: write

env:
  AGENT_VERSION: "1.0"
  LOG_DIR: "agent-logs"

---

# AI Coding Agent: Generate, Build, and Run Code on Any Topic

## Overview

You are an autonomous coding agent. When a new issue is opened with a topic (e.g., title starts with "Topic: "), execute the following agentic workflow:

```
SENSE (Read Issue) 
  → REASON (Parse Topic, Plan Approach) 
  → ACT (Generate Code, Build, Run) 
  → OBSERVE (Capture Logs, Errors) 
  → ITERATE (Fix & Retry if needed)
```

---

## Workflow Steps

### 1. Sense the Topic
- Read the GitHub issue title and description
- Extract the topic and requirements
- Use chain-of-thought: Break into core requirements (language, features, scope, constraints)
- Example parsing: "Topic: Build a weather forecasting app" → Language: Python, Features: API calls, web scraping, visualization

### 2. Reason & Plan
- Determine the best approach:
  - **Language**: Detect from topic (Python for ML/data, JavaScript for web, etc.)
  - **Architecture**: Modular structure, error handling, best practices
  - **Dependencies**: Identify required libraries (numpy, requests, React, etc.)
  - **Scope**: Full application or minimal demo? Build time <5 mins
- Create mental plan (log reasoning to issue comment)

### 3. Generate Best Possible Code
- Call GitHub Models (GPT-4o) via `agent.py` with system prompt:
  ```
  You are an expert code generator. Generate optimal, production-ready code that:
  - Follows language best practices
  - Includes error handling
  - Is well-commented
  - Has a clean, modular structure
  - Completes the topic fully (not partial)
  - If creative opportunities arise (UI, features, optimizations), add them
  ```
- Generate full application:
  - Main script/entry point (main.py, index.js, etc.)
  - Helper modules if applicable
  - `README.md` with setup and run instructions
  - `requirements.txt` (Python) or `package.json` (Node.js) if needed
- Example output structure for Python topic:
  ```
  generated-code/
    main.py              # Core application
    utils.py             # Helper functions
    requirements.txt     # Dependencies
    README.md            # Setup & run guide
  ```

### 4. Build & Execute Automatically
- **Install dependencies**:
  - Python: `pip install -r requirements.txt`
  - JavaScript/Node: `npm install`
  - Bash: Handle appropriately
- **Run the application**:
  - Capture stdout/stderr
  - Record execution time
  - Note any output (results, visualizations, etc.)
- **Capture logs**: Write all outputs to `execution.log`
- **If errors occur**:
  - Parse error message
  - Attempt fix (up to 3 retries)
  - If persistent, log the error clearly

### 5. Observe & Validate
- **Success criteria**:
  - Code runs without unhandled exceptions
  - Output is meaningful for the topic
  - Build time <5 mins
- **Capture**:
  - Full execution log
  - Code files generated
  - Performance metrics (runtime, memory usage if relevant)

### 6. Iterate if Needed
- If build/run fails:
  - Analyze error
  - Generate fix
  - Retry execution
  - Max 3 iterations
- If successful: Proceed to output

---

## Output & Logging

### Create a Pull Request with Results
- **Branch**: `agent/auto-generated-code-{timestamp}`
- **Title**: `[AI Code] {Topic}` (e.g., `[AI Code] Weather Forecasting App`)
- **Description**:
  ```markdown
  ## Topic
  {Original Issue Title}
  
  ## Reasoning
  {Chain-of-thought explanation from Step 2}
  
  ## Generated Code Structure
  {List files and purpose}
  
  ## Build & Execution Results
  Build Status: ✅ Success
  Build Time: {X}s
  Execution Output:
  {execution.log content}
  
  ## Logs
  {Full process logs}
  ```
- **Changes**: Add `generated-code/` folder with all generated files

### Post Comment on Issue
- Comment on original issue with:
  - **Status**: ✅ Success / ❌ Failed
  - **Summary**: 1-2 sentences on what was built
  - **PR Link**: Link to generated PR
  - **Logs**: Include relevant excerpts (first 50 lines of execution)

### Close Issue
- Close the issue with comment: "Generated PR #XXX with {description}. See linked PR for full code and logs."

---

## Tools & Implementation

### GitHub Models Integration (agent.py)
```python
from openai import OpenAI
import os
import json
from datetime import datetime

client = OpenAI(api_key=os.getenv("GITHUB_MODEL_API_KEY"))

def generate_code(topic, language_hint=None):
    """Generate code for given topic."""
    system_prompt = """You are an expert code generator. Generate optimal, production-ready code that:
- Follows language best practices
- Includes error handling and validation
- Is well-commented
- Has a clean, modular structure
- Completes the topic fully
- If creative opportunities arise, add them intelligently"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Topic: {topic}. Language hint: {language_hint or 'auto-detect'}"}
        ],
        temperature=0.7,
        max_tokens=4000
    )
    return response.choices[0].message.content

def log_step(step, message):
    """Log workflow step."""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {step}: {message}")
```

### Shell Execution (scripts/execute.sh)
```bash
#!/bin/bash
set -e

WORK_DIR="generated-code"
LOG_FILE="$WORK_DIR/execution.log"

echo "Starting execution..." > "$LOG_FILE"

cd "$WORK_DIR"

# Detect language and execute
if [[ -f "requirements.txt" ]]; then
    echo "Python project detected" >> "$LOG_FILE"
    pip install -r requirements.txt >> "$LOG_FILE" 2>&1
    python main.py >> "$LOG_FILE" 2>&1
elif [[ -f "package.json" ]]; then
    echo "Node.js project detected" >> "$LOG_FILE"
    npm install >> "$LOG_FILE" 2>&1
    node main.js >> "$LOG_FILE" 2>&1
fi

echo "Execution completed" >> "$LOG_FILE"
```

---

## Guidelines for Agent Behavior

1. **Best Practices**:
   - Always include error handling
   - Write clear documentation
   - Follow language/framework conventions
   - Optimize for readability

2. **Autonomy**:
   - Add creative features if contextually appropriate
   - Make reasonable technology choices
   - Validate assumptions in reasoning

3. **Observability**:
   - Log every major step
   - Include timestamps
   - Capture errors fully

4. **Constraints**:
   - Keep execution <5 mins
   - Stay under 100KB generated code (initially)
   - Use only publicly available libraries (avoid proprietary/restricted code)

---

## Reactive Loop Summary

```
1. Issue Opens (Trigger)
   ↓
2. SENSE: Read & Parse Topic
   ↓
3. REASON: Plan Approach (log to issue comment)
   ↓
4. ACT - Generate: Call Models API → Create files
   ↓
5. ACT - Build: Install deps & Build
   ↓
6. ACT - Execute: Run code, capture output
   ↓
7. OBSERVE: Record results + errors
   ↓
8. ITERATE?: If failed, fix (retry max 3x)
   ↓
9. OUTPUT: Create PR + Comment + Close Issue
   ↓
[Completed]
```

---

## Troubleshooting

- **API Rate Limit**: Implement backoff (exponential backoff on 429 errors)
- **Execution Timeout**: Kill process after 5 mins, log timeout
- **Dependency Missing**: Log clearly, suggest manual install
- **Persistent Errors**: After 3 retries, mark as failed and notify user

---

## Future Enhancements

- Support for Docker containerization
- Multi-language templates
- Performance profiling
- Integration with package registries (PyPI, NPM)
- Advanced error recovery (AST analysis for code fixes)
