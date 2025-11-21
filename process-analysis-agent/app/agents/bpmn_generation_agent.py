"""
agents/bpmn_generation_agent.py
Agent 4: BPMN Generation Agent
Generates Mermaid Flowchart code from process structure.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import types
from app import config
from app.tools import render_mermaid_to_svg

def create_bpmn_generation_agent() -> LlmAgent:
    """
    Creates the BPMN Generation Agent (Mermaid).
    
    Uses Code Execution Tool for SVG rendering.
    
    Returns:
        LlmAgent configured for Mermaid generation
    """
    
    # Custom Tool: SVG Rendering
    render_tool = FunctionTool(
        func=render_mermaid_to_svg
    )
    
    agent = LlmAgent(
        name="BPMNGenerationAgent",
        model=config.MODEL_FLASH_THINKING,
        instruction=(
            "You are an expert Mermaid.js developer specializing in business process diagrams. "
            "Your task is to generate valid Mermaid 'flowchart TD' code based on the provided process structure.\n\n"
            "STRICT RULES FOR ROBUST SYNTAX:\n"
            "1. Always wrap node labels in double quotes. Example: node1[\"Start Process\"]\n"
            "2. Do NOT use parentheses () inside node labels unless they are within quotes. Even better: Avoid them.\n"
            "3. Use distinct IDs (e.g., Start, Decision1, End_Approved).\n"
            "4. For End Events, use the syntax: id([\"Label\"])\n"
            "5. For Decisions, use the syntax: id{{\"Question?\"}}\n"
            "6. Return ONLY the raw Mermaid code. No markdown blocks (```mermaid), no explanations."
        ),
        description=(
            "Generates clean Mermaid flowchart syntax from process structures. "
            "Specializes in business process diagram notation."
        ),
        tools=[
            render_tool
        ],
        output_key="current_mermaid_code",
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,  # Very low for precise syntax
        )
    )
    
    print(f"✅ {agent.name} created (with render tool)")
    return agent