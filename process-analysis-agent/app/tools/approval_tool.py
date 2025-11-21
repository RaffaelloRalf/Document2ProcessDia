"""
tools/approval_tool.py
Human-in-the-Loop Tool using ADK's native confirmation mechanism.
"""

import os
from typing import Dict, Any
from google.adk.tools import ToolContext

def request_publication_approval(
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Pauses the workflow and requests user approval to proceed.
    """
    print("\n[Approval Tool] ⏸️  Requesting user confirmation...")

    # 1. CHECK STATE FIRST (Double Safety)
    current_status = tool_context.session.state.get("approval_status")
    if current_status == "APPROVED":
        print("[Approval Tool] ⏩ Already APPROVED in state. Skipping.")
        return {"status": "approved", "approved": True, "message": "Already approved"}

    # 2. RESUME PHASE (User has clicked/responded in Web UI)
    if tool_context.tool_confirmation:
        if tool_context.tool_confirmation.confirmed:
            print("[Approval Tool] ✅ User APPROVED.")
            # STATE SETZEN!
            tool_context.session.state["approval_status"] = "APPROVED"
            return {"status": "approved", "approved": True}
        else:
            print("[Approval Tool] ❌ User REJECTED.")
            tool_context.session.state["approval_status"] = "REJECTED"
            reason = tool_context.tool_confirmation.payload.get("reason", "No reason given")
            return {"status": "rejected", "approved": False, "reason": reason}

    # 3. INITIAL PHASE (Trigger)
    
    # CLI Auto-Approve
    if os.getenv("CLI_MODE") == "true":
        print("[Approval Tool] 🤖 CLI Mode detected: Auto-approving.")
        tool_context.session.state["approval_status"] = "APPROVED"
        return {"status": "approved", "approved": True}

    # Web Mode: Trigger the pause
    print("[Approval Tool] ⏳ Triggering Web UI interruption...")
    
    mermaid_code = tool_context.session.state.get("current_mermaid_code", "No code found")
    
    tool_context.request_confirmation(
        hint="Please review the generated diagram code and approve publication.",
        payload={
            "preview_data": mermaid_code[:500] + "..." 
        }
    )
    
    # WICHTIG: Status auf PENDING setzen, damit wir wissen, dass wir warten
    tool_context.session.state["approval_status"] = "PENDING"
    
    return {"status": "waiting_for_user", "approved": False}