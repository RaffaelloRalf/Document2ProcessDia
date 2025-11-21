"""
agents/pdf_analysis_agent.py
Agent 1: PDF Analysis Agent
Analyzes extracted text to identify the process structure.
"""

from typing import List, Optional
from google.adk.agents import LlmAgent
from google.genai import types
from pydantic import BaseModel, Field, conint
from app import config

# Pydantic Models for structured output
class Step(BaseModel):
    id: conint(ge=0) = Field(..., description="Unique identifier for the step.")
    type: str = Field(..., description="Type of the step (e.g., 'task', 'decision', 'start_event', 'end_event').")
    action: str = Field(..., description="Description of the action performed in the step.")
    actor: Optional[str] = Field(None, description="The actor performing the step.")
    condition: Optional[str] = Field(None, description="Condition for a decision step.")

class Dependency(BaseModel):
    from_: conint(ge=0) = Field(..., alias="from", description="The ID of the source step.")
    to: conint(ge=0) = Field(..., description="The ID of the target step.")
    label: Optional[str] = Field(None, description="Label for the dependency/arrow.")

class PdfAnalysisOutput(BaseModel):
    actors: List[str] = Field(..., description="List of all actors involved in the process.")
    steps: List[Step] = Field(..., description="List of all process steps.")
    dependencies: List[Dependency] = Field(..., description="List of dependencies between steps.")


def create_pdf_analysis_agent() -> LlmAgent:
    """
    Creates the PDF Analysis Agent.
    
    This agent analyzes the pre-extracted text from a PDF document
    to identify the process structure.
    
    Returns:
        LlmAgent configured for PDF analysis
    """
    
    agent = LlmAgent(
        name="PDFAnalysisAgent",
        model=config.MODEL_FLASH_THINKING,
        instruction=(
            "You are an expert in business process analysis. Your task is to extract "
            "the core process flow from the provided text, which is available in "
            "'session.state[\"extracted_pdf_text\"]'. Identify all actors, process steps, "
            "decisions, and their dependencies. Your output must strictly adhere to "
            "the PdfAnalysisOutput JSON schema."
        ),
        description=(
            "Analyzes business process descriptions from pre-extracted PDF text. "
            "Identifies actors, steps, decisions, and dependencies to structure the process."
        ),
        tools=[],  # No tools needed, text is already in state
        output_schema=PdfAnalysisOutput
    )
    
    print(f"✅ {agent.name} created (Expects 'extracted_pdf_text' in state)")
    return agent