"""
agents/publication_agent.py
Agent 7: Publication Agent
Checks for 'approval_status' before saving anything.
"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import types
from app import config
from app.tools import render_mermaid_to_svg, save_diagram, save_report

def create_publication_agent() -> LlmAgent:
    """
    Creates the Publication Agent with State Check.
    """
    
    render_tool = FunctionTool(func=render_mermaid_to_svg)
    save_diagram_tool = FunctionTool(func=save_diagram)
    save_report_tool = FunctionTool(func=save_report)
    
    agent = LlmAgent(
        name="PublicationAgent",
        model=config.MODEL_FLASH_THINKING,
        instruction=(
            "You are the Publication Manager. You perform the final save.\n\n"
            "SECURITY CHECK (CRITICAL):\n"
            "1. Check 'session.state[\"approval_status\"]'.\n"
            "2. IF status is 'PENDING', 'REJECTED', or missing: STOP IMMEDIATELY.\n"
            "   - Do NOT call any save tools.\n"
            "   - Return: 'Publication halted: Approval pending or rejected.'\n"
            "3. ONLY IF status is 'APPROVED': Proceed with saving.\n\n"
            "SAVING STEPS (Only if APPROVED):\n"
            "- Extract filename from 'session.state[\"pdf_path\"]'.\n"
            "- Call 'render_mermaid_to_svg'.\n"
            "- Call 'save_diagram'.\n"
            "- Call 'save_report'.\n"
            "- Return: 'Analysis complete. Report saved at [path].'"
        ),
        description="Saves files ONLY if approval_status is APPROVED.",
        tools=[render_tool, save_diagram_tool, save_report_tool],
        generate_content_config=types.GenerateContentConfig(
            temperature=0.0, # Zero temp for strict logic
        )
    )
    
    print(f"✅ {agent.name} created (handles saving & reporting)")
    return agent