"""
agents/approval_agent.py
Agent 6.5: Approval Agent
Interacts with the human user to get valid sign-off before publication.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import types
from app import config
from app.tools.approval_tool import request_publication_approval

def create_approval_agent() -> LlmAgent:
    """
    Creates the Approval Agent.
    """
    
    approval_tool = FunctionTool(func=request_publication_approval)
    
    agent = LlmAgent(
        name="ApprovalAgent",
        model=config.MODEL_FLASH_THINKING,
        # HIER IST DER FIX: Kontext-Variable {approval_status?} nutzen!
        instruction=(
            "You are the Quality Gatekeeper.\n\n"
            "CURRENT STATUS: {approval_status?}\n\n"
            "LOGIC:\n"
            "1. IF status is 'APPROVED':\n"
            "   - Do NOT call the tool.\n"
            "   - Just output: 'Approval already granted. Proceeding.'\n"
            "2. IF status is 'REJECTED':\n"
            "   - Do NOT call the tool.\n"
            "   - Just output: 'Approval denied previously.'\n"
            "3. IF status is unknown or 'PENDING':\n"
            "   - Call 'request_publication_approval' tool.\n"
            "   - If tool returns 'waiting_for_user': Output 'Waiting for user approval...'\n"
            "   - If tool returns 'approved': Output 'Approval confirmed.'\n"
            "   - If tool returns 'rejected': Output 'Approval denied.'"
        ),
        description="Triggers approval workflow only if not already approved.",
        tools=[approval_tool],
        generate_content_config=types.GenerateContentConfig(
            temperature=0.0
        )
    )
    
    print(f"✅ {agent.name} created")
    return agent