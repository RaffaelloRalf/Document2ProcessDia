"""
agents/validation_agent.py
Agent 5: Validation Agent
Validates Mermaid diagrams for syntax and logic errors.
"""
from typing import List
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import types
from pydantic import BaseModel, Field
from app import config
from app.tools import validate_mermaid_syntax

# Pydantic Model for structured output
class ValidationOutput(BaseModel):
    syntax_valid: bool = Field(..., description="Whether the Mermaid syntax is valid.")
    logic_valid: bool = Field(..., description="Whether the process logic is valid (e.g., single start, no orphans).")
    errors: List[str] = Field(..., description="A list of errors found in the diagram.")
    warnings: List[str] = Field(..., description="A list of warnings or suggestions for improvement.")
    overall_status: str = Field(..., description="Overall status: 'valid', 'invalid', or 'needs_improvement'.")


def create_validation_agent() -> LlmAgent:
    """
    Creates the Validation Agent.
    """
    
    # Custom Tool: Mermaid Validator
    validator_tool = FunctionTool(
        func=validate_mermaid_syntax
    )
    
    agent = LlmAgent(
        name="ValidationAgent",
        model=config.MODEL_FLASH_THINKING,
        # --- UPDATE: Explicit Handoff Instruction ---
        instruction=(
            config.SYSTEM_PROMPT_VALIDATION + 
            "\n\nIMPORTANT FINAL STEP:\n"
            "After validating the diagram, output the JSON result.\n"
            "Then, explicitly state: 'Validation complete. Proceeding to publication.'"
        ),
        # --------------------------------------------
        description=(
            "Validates Mermaid flowcharts. Passes control to PublicationAgent upon completion."
        ),
        tools=[validator_tool],
        output_schema=ValidationOutput,
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,
        )
    )
    
    print(f"✅ {agent.name} created (with validator tool)")
    return agent