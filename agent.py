#!/usr/bin/env python3
"""
AI Coding Agent - Code Generation Module
Generates optimal code based on topics using GitHub Models
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)


class AICodeAgent:
    """Autonomous AI Code Generator"""
    
    def __init__(self, api_key=None):
        """Initialize the agent with GitHub Models API key"""
        self.api_key = api_key or os.getenv("GITHUB_MODEL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GITHUB_MODEL_API_KEY environment variable not set. "
                "Set it to your GitHub Models API key."
            )
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://models.inference.ai.azure.com"  # GitHub Models endpoint
        )
        self.log_buffer = []
    
    def log(self, level, message):
        """Log a message with timestamp"""
        timestamp = datetime.now().isoformat()
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        self.log_buffer.append(log_msg)
    
    def reasoning_step(self, topic):
        """Step 1: Parse topic and create reasoning"""
        self.log("SENSE", f"Reading topic: {topic}")
        
        # Use reasoning prompt
        reasoning_prompt = f"""Analyze this topic and provide structured reasoning:

Topic: {topic}

Provide:
1. Language (Python/JavaScript/Bash/etc)
2. Core Features (3-5 key features needed)
3. Architecture (modular approach)
4. Dependencies (key libraries)
5. Scope (full app or minimal demo)
6. Creative opportunities (optional features to make it better)

Format as JSON."""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": reasoning_prompt}],
            temperature=0.5,
            max_tokens=1000
        )
        
        reasoning = response.choices[0].message.content
        self.log("REASON", f"Analysis complete:\n{reasoning}")
        return reasoning
    
    def generate_code_step(self, topic, reasoning):
        """Step 2: Generate optimal code"""
        self.log("ACT-GENERATE", "Starting code generation...")
        
        generation_prompt = f"""Based on this topic and reasoning, generate complete, production-ready code:

Topic: {topic}

Reasoning/Analysis:
{reasoning}

Requirements:
- Complete, working code (not snippets)
- Best practices and error handling
- Well-commented and modular
- Include setup/run instructions in docstring
- Use popular, stable libraries only
- Make it creative where appropriate

Generate the full code. Include:
1. Main script/entry point
2. Helper functions/modules if needed
3. Comments on architecture
4. Error handling throughout

Output ONLY the code, ready to run."""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": generation_prompt}],
            temperature=0.7,
            max_tokens=4000
        )
        
        code = response.choices[0].message.content
        self.log("ACT-GENERATE", f"Generated code ({len(code)} chars)")
        return code
    
    def generate_requirements(self, topic, code):
        """Step 3: Generate requirements.txt if Python"""
        req_prompt = f"""Given this topic and code, what Python packages are needed?

Topic: {topic}

Code snippet:
{code[:500]}...

List ONLY package names and versions (one per line), like:
requests==2.28.1
numpy==1.23.0

If no external packages needed, return: # No external dependencies"""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": req_prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        requirements = response.choices[0].message.content
        self.log("ACT-GENERATE", "Generated requirements")
        return requirements
    
    def save_generated_code(self, topic, code, requirements=None):
        """Save generated code to files"""
        output_dir = Path("generated-code")
        output_dir.mkdir(exist_ok=True)
        
        # Detect language and save main file
        if "import" in code and ("import os" in code or "import sys" in code or "def " in code):
            main_file = output_dir / "main.py"
            language = "python"
        else:
            main_file = output_dir / "main.js"
            language = "javascript"
        
        # Write main code
        with open(main_file, "w") as f:
            f.write(code)
        self.log("OBSERVE", f"Saved code to {main_file}")
        
        # Write requirements
        if requirements and language == "python":
            req_file = output_dir / "requirements.txt"
            with open(req_file, "w") as f:
                f.write(requirements)
            self.log("OBSERVE", f"Saved requirements to {req_file}")
        
        # Save metadata
        metadata = {
            "topic": topic,
            "language": language,
            "generated_at": datetime.now().isoformat(),
            "files": [str(main_file)]
        }
        with open(output_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        return output_dir
    
    def generate_full(self, topic):
        """Execute full agent workflow"""
        self.log("START", f"Generating code for topic: {topic}")
        
        try:
            # Step 1: Reasoning
            reasoning = self.reasoning_step(topic)
            
            # Step 2: Generate code
            code = self.generate_code_step(topic, reasoning)
            
            # Step 3: Generate requirements (if Python)
            requirements = None
            if "python" in reasoning.lower():
                requirements = self.generate_requirements(topic, code)
            
            # Step 4: Save files
            output_dir = self.save_generated_code(topic, code, requirements)
            
            self.log("SUCCESS", f"Generated code saved to {output_dir}")
            return {
                "status": "success",
                "output_dir": str(output_dir),
                "logs": "\n".join(self.log_buffer),
                "files": list(output_dir.glob("*"))
            }
        
        except Exception as e:
            self.log("ERROR", str(e))
            return {
                "status": "error",
                "error": str(e),
                "logs": "\n".join(self.log_buffer)
            }


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="AI Coding Agent - Generate code from topics")
    parser.add_argument("topic", help="Topic for code generation (e.g., 'Build a weather app')")
    parser.add_argument("--api-key", help="GitHub Models API key (or set GITHUB_MODEL_API_KEY env var)")
    parser.add_argument("--output", default="generated-code", help="Output directory")
    
    args = parser.parse_args()
    
    try:
        agent = AICodeAgent(api_key=args.api_key)
        result = agent.generate_full(args.topic)
        
        print("\n" + "="*60)
        print("GENERATION COMPLETE")
        print("="*60)
        print(f"Status: {result['status'].upper()}")
        if result['status'] == 'success':
            print(f"Output: {result['output_dir']}")
            print(f"Files: {len(result['files'])} generated")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        print("="*60)
        
        # Print logs
        print("\nLogs:")
        print(result['logs'])
        
        return 0 if result['status'] == 'success' else 1
    
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
