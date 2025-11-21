# Makefile for Process Analysis Agent

.PHONY: run web install

# Configuration
FILE ?= app/test_data/sample_process.pdf

# --- COMMANDS ---

# 1. Web Interface (Interactive HITL)
# Starts the ADK server. In the browser chat, simply type:
# "Analyze: app/test_data/sample_process.pdf"
# (Wait for the Approval Buttons to appear!)
web:
	CLI_MODE=false
	uv run adk web .

# 2. CLI Mode (Auto-Approve via Env Var)
# Usage: make run (or make run FILE=...)
# Sets CLI_MODE=true so the approval tool doesn't hang.
run:
	CLI_MODE=true uv run python -m app.agent $(FILE)

# 3. Install
install:
	uv pip install -r requirements.txt