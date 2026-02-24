# AI Coding Agent - Complete Setup Guide

This guide walks you through setting up the AI Coding Agent repository on GitHub with full automation.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Create GitHub Repository](#create-github-repository)
3. [Configure GitHub Secrets](#configure-github-secrets)
4. [Set Up GitHub Actions](#set-up-github-actions)
5. [Test the Agent](#test-the-agent)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

You'll need:

### 1. GitHub Account
- Sign up at [github.com](https://github.com)
- Ensure you have administrative access to create repositories

### 2. GitHub Copilot (Optional but Recommended)
- Enable GitHub Copilot: [github.com/settings/billing](https://github.com/settings/billing)
- Copilot subscription: ~$10/month (or free for students/open source maintainers)

### 3. GitHub Models Access
- Go to [github.com/marketplace/models](https://github.com/marketplace/models)
- Browse available models (GPT-4o, Llama 3.1, Claude 3.5 Sonnet, etc.)
- Test the model playground to get your API key
- **Important**: Note your API key for later (Step 3)

### 4. GitHub CLI (Optional, for local testing)
```bash
# macOS
brew install gh

# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### 5. Python 3.8+ (for local testing)
```bash
python3 --version
pip install openai
```

---

## Create GitHub Repository

### Option A: Via GitHub Web UI (Recommended)

1. Go to [github.com/new](https://github.com/new)
2. **Repository name**: `ai-coding-agent`
3. **Description**: "Autonomous AI coding agent powered by GitHub Models and Copilot"
4. **Visibility**: 
   - Public (if you want to share)
   - Private (if you want to keep it private)
5. **Initialize with**:
   - ☐ Add a README file (we have one)
   - ☐ Add .gitignore (Python template recommended)
   - ☐ Add a license (MIT recommended)
6. Click **Create repository**

### Option B: Via GitHub CLI (Local)

```bash
gh repo create ai-coding-agent \
  --description "Autonomous AI coding agent powered by GitHub Models" \
  --public \
  --source . \
  --remote origin \
  --push
```

---

## Configure GitHub Secrets

### Why?
The agent needs API keys to call GitHub Models. Store them securely as GitHub Secrets.

### Steps:

1. Go to your repository: `github.com/yourusername/ai-coding-agent`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Add These Secrets:

#### Secret 1: AI_AGENT_MODEL_API_KEY
- **Name**: `AI_AGENT_MODEL_API_KEY`
- **Value**: Your GitHub Models API key (from Prerequisites)
  - From [github.com/marketplace/models](https://github.com/marketplace/models), click your profile → copy API key
- Click **Add secret**

#### Secret 2: GITHUB_TOKEN (Auto-configured)
- GitHub automatically provides `GITHUB_TOKEN` in workflow
- No manual setup needed (used for PR/Issue operations)

### Optional Secrets (for enhancements):
- `COPILOT_API_KEY`: If using Copilot directly
- `CUSTOM_MODEL_ENDPOINT`: For custom model endpoints

---

## Set Up GitHub Actions

### What We'll Do

Transform the workflow from markdown (`.github/workflows/code-agent.md`) into executable YAML (`.github/workflows/code-agent.yml`).

### Step 1: Create the Workflow YAML File

Create `.github/workflows/code-agent.yml` in your repository:

```yaml
name: AI Coding Agent Workflow

on:
  issues:
    types: [opened]
  push:
    branches:
      - main
    paths:
      - '.github/workflows/code-agent.md'

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  ai-code-generation:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v4
      
      - name: Set Up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install openai
      
      - name: Extract Topic from Issue
        id: extract_topic
        if: github.event_name == 'issues'
        run: |
          ISSUE_TITLE="${{ github.event.issue.title }}"
          ISSUE_BODY="${{ github.event.issue.body }}"
          
          echo "title=$ISSUE_TITLE" >> $GITHUB_OUTPUT
          echo "body=$ISSUE_BODY" >> $GITHUB_OUTPUT
          
          # Check if it's a "Topic:" issue
          if [[ "$ISSUE_TITLE" != Topic:* ]]; then
            echo "Not a topic issue, skipping"
            exit 0
          fi
          
          echo "processing=true" >> $GITHUB_OUTPUT
      
      - name: Generate Code with AI Agent
        if: steps.extract_topic.outputs.processing == 'true'
        env:
          AI_AGENT_MODEL_API_KEY: ${{ secrets.AI_AGENT_MODEL_API_KEY }}
        run: |
          python agent.py "${{ steps.extract_topic.outputs.title }}" --output generated-code
      
      - name: Build & Execute Generated Code
        if: steps.extract_topic.outputs.processing == 'true'
        run: |
          chmod +x scripts/execute.sh
          bash scripts/execute.sh || true
      
      - name: Capture Execution Logs
        if: steps.extract_topic.outputs.processing == 'true'
        id: logs
        run: |
          if [[ -f "generated-code/execution.log" ]]; then
            cat generated-code/execution.log >> $GITHUB_ENV
          else
            echo "No execution log found" >> $GITHUB_ENV
          fi
      
      - name: Create Pull Request with Generated Code
        if: steps.extract_topic.outputs.processing == 'true'
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: "AI Generated: ${{ steps.extract_topic.outputs.title }}"
          title: "[AI Code] ${{ steps.extract_topic.outputs.title }}"
          body: |
            ## Topic
            ${{ steps.extract_topic.outputs.title }}
            
            ## Description
            Automatically generated by AI Coding Agent
            
            ## Generated Files
            See generated-code/ directory for all files
            
            ## Execution Status
            Check workflow logs under .github/workflows/ for details
          branch: "agent/code-${{ github.run_number }}"
          labels: "ai-generated"
      
      - name: Comment on Issue
        if: steps.extract_topic.outputs.processing == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ **AI Agent Started Processing**\n\n' +
                    'Topic: ${{ steps.extract_topic.outputs.title }}\n\n' +
                    'Generating code and running tests...\n\n' +
                    'Check the linked PR for generated code and logs.'
            })
```

### Step 2: Commit Workflow to Repository

If you're in Codespaces or local:

```bash
# Navigate to repo
cd /workspaces/ai-coding-agent

# Copy the created workflow file (already should be there)
ls -la .github/workflows/

# Commit and push
git add .
git commit -m "Add AI coding agent workflow"
git push origin main
```

### Step 3: Verify Workflow is Enabled

1. Go to repository → **Actions** tab
2. You should see "AI Coding Agent Workflow" listed
3. If disabled, click **Enable**

---

## Test the Agent

### Test #1: Local Test (Optional, for development)

```bash
# Set API key locally
export AI_AGENT_MODEL_API_KEY="your-key-from-step-1"

# Test code generation
python agent.py "Build a simple calculator in Python"

# Check output
ls -la generated-code/
cat generated-code/main.py
```

### Test #2: Trigger via GitHub Issue (Main Test)

1. Go to your repository: `github.com/yourusername/ai-coding-agent`
2. Click **Issues** → **New Issue**
3. **Title**: `Topic: Build a simple calculator in JavaScript`
4. **Description** (optional): "Add basic arithmetic operations (add, subtract, multiply, divide)"
5. Click **Create Issue**

### Watch the Magic

1. Go to **Actions** tab
2. You'll see workflow running: "AI Coding Agent Workflow"
3. **Real-time logs**: Click the running job to see live output
4. **Success indicators**:
   - ✅ "Extract Topic" - Found the issue
   - ✅ "Generate Code" - Called AI model
   - ✅ "Build & Execute" - Built and ran code
   - ✅ "Create PR" - Generated PR with code

### Review the Output

1. After workflow completes, go to **Pull Requests** tab
2. Find PR with title `[AI Code] Topic: ...`
3. Click to view:
   - **Files changed**: `generated-code/` folder
   - **Code generated**: main.js, main.py, etc.
   - **PR Description**: Includes execution logs

### Test #3: Multiple Topics

Try different topics to see agent flexibility:

```
Topic: Build a weather CLI tool in Python
Topic: Create a React todo list component in JavaScript
Topic: Build a Fibonacci sequence generator in Bash
Topic: Simple file-based note-taking app in Python with search
```

Each creates a new PR with unique, optimized code.

---

## Troubleshooting

### Issue: Workflow doesn't trigger on new issue

**Possible Causes**:
- Workflow file has syntax errors
- Issue title doesn't contain "Topic:" prefix
- GitHub Actions permissions not granted

**Solutions**:
1. Check `.github/workflows/code-agent.yml` syntax: Go to workflow file → "Workflow runs" section
2. Re-create issue with proper title: `Topic: Your topic here`
3. Verify permissions: **Settings** → **Actions** → **General** → ensure "Read and write permissions" enabled

### Issue: "AI_AGENT_MODEL_API_KEY not set" error

**Solution**:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Verify `AI_AGENT_MODEL_API_KEY` exists
3. If missing, add it (see Step 2 above)
4. Rerun workflow: Go to **Actions** → Select workflow → **Re-run all jobs**

### Issue: Code generation fails or produces empty code

**Common Reasons**:
- API rate limit exceeded
- Model overloaded
- Topic too vague

**Solutions**:
1. Try with a more specific topic: `Topic: Build a Python script that fetches weather from OpenWeatherMap API`
2. Wait 5 minutes and retry
3. Check API logs: Go to **Actions** → Click job → Logs

### Issue: Generated code doesn't execute / "No recognizable project type"

**Solutions**:
1. Check `generated-code/` folder for files:
   ```bash
   ls -la generated-code/
   ```
2. Verify `main.py` or `main.js` exists
3. Check `execution.log` for error details:
   ```bash
   cat generated-code/execution.log
   ```

### Issue: Build time exceeds 10 minutes

**Solutions** (from `.github/workflows/code-agent.yml`):
- Workflow timeout set to 10 minutes
- If generating complex projects, increase `timeout-minutes: 15` or break into smaller steps

---

## Next Steps

### 1. Enhance the Agent
- Add support for compiled languages (Go, Rust, C++)
- Implement multi-file generation templates
- Add Docker containerization support
- Integrate with package registries (PyPI, NPM publishing)

### 2. Advanced Observability
- Set up GitHub Pages to display generated code gallery
- Add metrics dashboard (execution time, success rate)
- Integrate Slack notifications for completions

### 3. Production Hardening
- Implement code security scanning (GitHub Advanced Security)
- Add cost monitoring for API calls
- Rate limiting and quota management

### 4. Community
- Share generated projects publicly
- Create a leaderboard of generated code quality
- Build GitHub App for installation in other repos

---

## File Reference

```
ai-coding-agent/
├── .github/
│   └── workflows/
│       ├── code-agent.md                 # Agent logic (natural language)
│       └── code-agent.yml                # Executable workflow (YAML)
├── agent.py                              # Core agent script
├── scripts/
│   └── execute.sh                        # Execution helper
├── docs/
│   └── SETUP.md                          # This file
├── README.md                             # Project overview
├── requirements.txt                      # Python dependencies
└── .gitignore                            # Git ignore file
```

---

## Support

For issues or questions:
1. Check **GitHub Issues** in your repository
2. Review **Actions** logs for detailed error messages
3. Test locally with `python agent.py "Your topic"`

Happy coding! 🚀
