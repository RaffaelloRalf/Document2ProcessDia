"""
agents/conversion_agent.py
Agent 2: Conversion Agent
Transforms extracted process elements into a POWL-like structure (Nodes + Edges).
"""
from typing import List, Optional
from google.adk.agents import LlmAgent
from google.genai import types
from pydantic import BaseModel, Field
from app import config

# Pydantic Models for structured output
class Node(BaseModel):
    id: str = Field(..., description="Unique identifier for the node.")
    type: str = Field(..., description="Type of the node (e.g., 'task', 'exclusive_gateway').")
    label: str = Field(..., description="Short, descriptive label for the node.")
    actor: Optional[str] = Field(None, description="The actor associated with the node.")

class Edge(BaseModel):
    from_: str = Field(..., alias="from", description="The ID of the source node.")
    to: str = Field(..., description="The ID of the target node.")
    label: Optional[str] = Field(None, description="Label for the edge, representing a condition.")

class ConversionOutput(BaseModel):
    nodes: List[Node] = Field(..., description="List of all nodes in the process graph.")
    edges: List[Edge] = Field(..., description="List of all edges connecting the nodes.")


def create_conversion_agent() -> LlmAgent:
    """
    Creates the Conversion Agent.
    
    This agent operates within the LoopAgent and is evaluated by the QualityAgent.
    
    Returns:
        LlmAgent configured for process conversion
    """
    
    agent = LlmAgent(
        name="ConversionAgent",
        model=config.MODEL_FLASH_THINKING,
        instruction=config.SYSTEM_PROMPT_CONVERSION,
        description=(
            "Converts extracted process elements into a POWL-like "
            "graph structure with nodes and edges. Filters out "
            "unnecessary details."
        ),
        tools=[],
        output_schema=ConversionOutput,
        generate_content_config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json"
        )
    )
    
    print(f"✅ {agent.name} created")
    return agent