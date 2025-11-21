"""
agents/quality_agent.py
Agent 3: Output Quality Agent
Evaluate the quality of the generated Process Structure (in the LoopAgent)
"""
from typing import List
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import types
from pydantic import BaseModel, Field, conint, confloat
from app import config

def exit_loop() -> dict:
    """
    Tool function to terminate the LoopAgent. Called by the Quality Agent when approved=True.
    
    Returns:
        Dict with exit signal
    """
    print("\n🔄 Quality Agent: Loop is terminated (Approval granted)")
    return {"exit_loop": True, "reason": "Quality standards met"}

# Pydantic Model for structured output
class QualityOutput(BaseModel):
    reasoning: str = Field(..., description="Detailed step-by-step reasoning for the evaluation.")
    completeness_score: confloat(ge=0.0, le=1.0) = Field(..., description="Score for completeness of the process.")
    clarity_score: confloat(ge=0.0, le=1.0) = Field(..., description="Score for clarity and unambiguity.")
    reduction_score: confloat(ge=0.0, le=1.0) = Field(..., description="Score for filtering out unnecessary details.")
    consistency_score: confloat(ge=0.0, le=1.0) = Field(..., description="Score for logical consistency of the flow.")
    feedback: str = Field(..., description="Specific, actionable feedback for improvement.")
    approved: bool = Field(..., description="True if all scores are >= 0.85, else False.")


    
def create_quality_agent() -> LlmAgent:
    class QualityOutput(BaseModel):
        reasoning: str = Field(...)
        completeness_score: confloat(ge=0.0, le=1.0) = Field(...)
        clarity_score: confloat(ge=0.0, le=1.0) = Field(...)
        reduction_score: confloat(ge=0.0, le=1.0) = Field(...)
        consistency_score: confloat(ge=0.0, le=1.0) = Field(...)
        feedback: str = Field(...)
        approved: bool = Field(...)
        exit_loop: bool = Field(..., description="True if loop should exit")
    
    agent = LlmAgent(
        name="QualityAgent",
        model=config.MODEL_FLASH_THINKING,
        instruction=config.SYSTEM_PROMPT_QUALITY + "\n\nSet 'exit_loop: true' when approved=true.",
        # tools=[] entfernt!
        output_schema=QualityOutput,
        generate_content_config=types.GenerateContentConfig(
            temperature=0.4,
            response_mime_type="application/json"
        )
    )
    return agent

