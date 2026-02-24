#!/bin/bash
# Execute generated code and capture output

set -e

WORK_DIR="generated-code"
LOG_FILE="$WORK_DIR/execution.log"

{
    echo "=== AI Code Execution Log ==="
    echo "Start Time: $(date)"
    echo "Working Directory: $(pwd)/$WORK_DIR"
    echo ""
    
    # Check if directory exists
    if [[ ! -d "$WORK_DIR" ]]; then
        echo "ERROR: $WORK_DIR directory not found"
        exit 1
    fi
    
    cd "$WORK_DIR"
    
    # Detect project type and execute
    if [[ -f "requirements.txt" ]]; then
        echo "=== Python Project Detected ==="
        echo "Installing dependencies..."
        if ! pip install -r requirements.txt 2>&1; then
            echo "ERROR: Failed to install dependencies"
            exit 1
        fi
        
        echo ""
        echo "=== Running main.py ==="
        if ! python main.py 2>&1; then
            echo "ERROR: main.py execution failed"
            exit 1
        fi
    
    elif [[ -f "package.json" ]]; then
        echo "=== Node.js Project Detected ==="
        echo "Installing dependencies..."
        if ! npm install 2>&1; then
            echo "ERROR: Failed to install dependencies"
            exit 1
        fi
        
        echo ""
        echo "=== Running main.js ==="
        if ! node main.js 2>&1; then
            echo "ERROR: main.js execution failed"
            exit 1
        fi
    
    elif [[ -f "main.py" ]]; then
        echo "=== Standalone Python Script ==="
        if ! python main.py 2>&1; then
            echo "ERROR: main.py execution failed"
            exit 1
        fi
    
    elif [[ -f "main.js" ]]; then
        echo "=== Standalone JavaScript ==="
        if ! node main.js 2>&1; then
            echo "ERROR: main.js execution failed"
            exit 1
        fi
    
    else
        echo "ERROR: No recognizable project type found"
        echo "Expected: requirements.txt, package.json, main.py, or main.js"
        exit 1
    fi
    
    echo ""
    echo "=== Execution Successful ==="
    echo "End Time: $(date)"
    
} | tee "$LOG_FILE"

exit 0
