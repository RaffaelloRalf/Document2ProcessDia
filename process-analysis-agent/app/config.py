"""
config.py
Central configuration for the Process Diagram Agent System
"""

import os
import sys

# =============================================================================
# Import Prompts (Robust for CLI & Web)
# =============================================================================
try:
    # Attempt 1: Import as package (Standard for 'make run' / 'adk web')
    from app.prompts import (
        SYSTEM_PROMPT_PDF_ANALYSIS,
        SYSTEM_PROMPT_CONVERSION,
        SYSTEM_PROMPT_QUALITY,
        SYSTEM_PROMPT_BPMN_GENERATION,
        SYSTEM_PROMPT_VALIDATION,
        SYSTEM_PROMPT_SYSTEM_EVALUATOR
    )
except ImportError:
    # Fallback: Local import (if config.py is tested directly)
    from prompts import (
        SYSTEM_PROMPT_PDF_ANALYSIS,
        SYSTEM_PROMPT_CONVERSION,
        SYSTEM_PROMPT_QUALITY,
        SYSTEM_PROMPT_BPMN_GENERATION,
        SYSTEM_PROMPT_VALIDATION,
        SYSTEM_PROMPT_SYSTEM_EVALUATOR
    )

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# API & Model Configuration
# =============================================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

# Model Names (Gemini 2.0 - free for testing!)
MODEL_FLASH_THINKING = "gemini-2.5-flash"  # Fast and cost-effective
MODEL_PRO = "gemini-2.5-pro"             # High reasoning capability

# =============================================================================
# Agent Configuration
# =============================================================================

MAX_QUALITY_ITERATIONS = 2
MIN_QUALITY_SCORE = 0.85

# =============================================================================
# File Paths
# =============================================================================

OUTPUT_DIR = "outputs"
LOGS_DIR = "logs"
TEST_DATA_DIR = "test_data"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(TEST_DATA_DIR, exist_ok=True)

# =============================================================================
# Logging
# =============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# =============================================================================
# Tool Configuration
# =============================================================================

MERMAID_CLI = "mmdc" # Assumes 'mmdc' is in the system PATH (via Nix)

# =============================================================================
# PDF Configuration
# =============================================================================

PDF_MAX_PAGES = 50

# =============================================================================
# Validation
# =============================================================================

def validate_config():
    """Validates the configuration at startup."""
    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY not found! "
            "Please create a .env file with your API Key."
        )
    
    print("✅ Configuration loaded successfully")
    print(f"   Model: {MODEL_FLASH_THINKING}")
    print(f"   Max Quality Iterations: {MAX_QUALITY_ITERATIONS}")

if __name__ != "__main__":
    validate_config()