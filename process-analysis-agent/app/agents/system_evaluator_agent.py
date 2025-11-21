"""
agents/system_evaluator_agent.py
Agent 6: System Quality Evaluator (Agent-as-a-Judge)
Evaluates the entire multi-agent system after workflow completion.
"""
from typing import List
from google.adk.agents import LlmAgent
from google.genai import types
from pydantic import BaseModel, Field, confloat
from app import config

# Pydantic Model for structured output
class SystemEvaluationOutput(BaseModel):
    planning_quality_score: confloat(ge=0.0, le=1.0) = Field(..., description="Score for the overall agent orchestration strategy.")
    tool_use_score: confloat(ge=0.0, le=1.0) = Field(..., description="Score for the correctness and efficiency of tool usage.")
    context_handling_score: confloat(ge=0.0, le=1.0) = Field(..., description="Score for proper context preservation and information flow.")
    collaboration_score: confloat(ge=0.0, le=1.0) = Field(..., description="Score for efficient agent handoff and feedback incorporation.")
    output_quality_score: confloat(ge=0.0, le=1.0) = Field(..., description="Score for the accuracy, usability, and structure of the final output.")
    overall_score: confloat(ge=0.0, le=1.0) = Field(..., description="Average of all individual scores.")
    feedback: str = Field(..., description="Detailed analysis of system performance.")
    recommendations: List[str] = Field(..., description="Specific suggestions for improving the system.")
    strengths: List[str] = Field(..., description="What the system did well.")
    weaknesses: List[str] = Field(..., description="What needs improvement.")


def create_system_evaluator_agent() -> LlmAgent:
    """
    Creates the System Quality Evaluator (Agent-as-a-Judge).
    
    This agent runs AT THE VERY END and evaluates:
    - Planning Quality
    - Tool Use
    - Context Handling
    - Agent Collaboration
    - Output Quality
    
    Uses Gemini 2.0 Pro for complex system analysis.
    
    Returns:
        LlmAgent configured for System Evaluation
    """
    
    agent = LlmAgent(
        name="SystemEvaluatorAgent",
        model=config.MODEL_PRO,
        instruction=(
            config.SYSTEM_PROMPT_SYSTEM_EVALUATOR + 
            "\n\nCRITICAL OUTPUT RULES:\n"
            "1. Return raw JSON only.\n"
            "2. Do NOT use Markdown code blocks (no ```json ... ```).\n"
            "3. Do NOT include any introductory text or explanations outside the JSON object.\n"
            "4. Ensure all boolean values are lowercase (true/false) and nulls are null."
        ),
        description=(
            "Evaluates the entire multi-agent system performance. "
            "Analyzes planning, tool use, context handling, collaboration, "
            "and output quality. Provides actionable recommendations."
        ),
        tools=[], # No tools - pure analysis
        output_schema=SystemEvaluationOutput,
        generate_content_config=types.GenerateContentConfig(
            temperature=0.0, # Zero temperature for maximum structural stability
            response_mime_type="application/json"
        )
    )
    
    print(f"✅ {agent.name} created (Pro Model for System Evaluation)")
    return agent