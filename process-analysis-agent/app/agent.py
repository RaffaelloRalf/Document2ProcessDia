"""
agent.py
ENTRY POINT for the Process Diagram Multi-Agent System
"""

import os
import sys
import asyncio
import json
import re

# --- SMART IMPORTS ---
from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import google.generativeai as genai

# Import from app package
from app import config
from app.agents import (
    create_pdf_analysis_agent,
    create_pdf_text_extraction_agent,
    create_conversion_agent,
    create_quality_agent,
    create_bpmn_generation_agent,
    create_validation_agent,
    create_system_evaluator_agent,
    create_approval_agent,
    create_publication_agent
)
from app.tools import (
    render_mermaid_to_svg,
    save_diagram,
    save_report
)

# =============================================================================
# Helper: Robust JSON Parser
# =============================================================================
def repair_and_parse_json(json_str):
    """Attempts to repair and parse broken JSON from LLMs."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
            json_str = json_str.replace("None", "null")
            json_str = json_str.replace("True", "true").replace("False", "false")
            return json.loads(json_str)
        except:
            return None

# =============================================================================

print("\n" + "="*70)
print("🚀 Process Diagram Multi-Agent System")
print("="*70 + "\n")

genai.configure(api_key=config.GOOGLE_API_KEY)

# =============================================================================
# Create Sub-Agents
# =============================================================================

print("📦 Creating Sub-Agents...")

pdf_text_extraction_agent = create_pdf_text_extraction_agent()
pdf_analysis_agent = create_pdf_analysis_agent()
conversion_agent = create_conversion_agent()
quality_agent = create_quality_agent()
bpmn_generation_agent = create_bpmn_generation_agent()
validation_agent = create_validation_agent()
system_evaluator_agent = create_system_evaluator_agent()
approval_agent = create_approval_agent()
publication_agent = create_publication_agent()

# =============================================================================
# Create Quality Loop Agent
# =============================================================================

print("\n🔄 Creating LoopAgent (Quality Loop)...")

quality_loop_agent = LoopAgent(
    name="QualityLoopAgent",
    description="Iteratively refines the process structure.",
    sub_agents=[conversion_agent, quality_agent],
    max_iterations=config.MAX_QUALITY_ITERATIONS
)

print(f"✅ {quality_loop_agent.name} created")

# =============================================================================
# Create Root Agent
# =============================================================================

print("\n🎯 Creating Root Agent...")

agent = SequentialAgent(
    name="ProcessDiagramRootAgent",
    description="Root orchestrator for process diagram generation.",
    sub_agents=[
        pdf_text_extraction_agent,
        pdf_analysis_agent,
        quality_loop_agent,
        bpmn_generation_agent,
        validation_agent,
        approval_agent,     # HITL Gatekeeper
        publication_agent   # Final Action
    ]
)

# IMPORTANT: For ADK Web
root_agent = agent

print(f"✅ {agent.name} created\n")

# =============================================================================
# Session Service
# =============================================================================

session_service = InMemorySessionService()

# =============================================================================
# Workflow Logic
# =============================================================================

async def run_process_diagram_workflow(pdf_path: str, user_query: str = None):
    print("="*70)
    print("🔥 STARTING WORKFLOW")
    print("="*70)
    
    try:
        if not user_query:
            user_query = "Analyze this process description."
        
        user_query += f"\n\nThe source PDF is located at path: {pdf_path}"
        
        user_id = "test_user"
        session_id = "test_session"
        app_name = "ProcessDiagramApp"
        
        session = await session_service.create_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        
        runner = Runner(agent=agent, app_name=app_name, session_service=session_service)
        
        final_response = ""
        
        # --- MAIN EVENT LOOP (Clean & Simple) ---
        # Wir entfernen hier jegliche manuelle Confirmation-Logik!
        # Das macht jetzt das Tool selbst.
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, 
            new_message=types.Content(parts=[types.Part(text=user_query)])
        ):
            if event.is_final_response():
                if hasattr(event, 'text') and event.text:
                    final_response = event.text
                else:
                    final_response = "Workflow completed."
        
        print(f"\n✅ Workflow completed!")

        # --- SYSTEM EVALUATION (Agent-as-a-Judge) ---
        print(f"\n🏅 System Evaluation (Agent-as-a-Judge)...")
        
        eval_score = "N/A"
        
        try:
            session = await session_service.get_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )
            mermaid_code = session.state.get("current_mermaid_code", "")
            
            eval_runner = Runner(
                agent=system_evaluator_agent,
                app_name=app_name,
                session_service=session_service
            )
            
            execution_trace = {
                "agents_invoked": [a.name for a in agent.sub_agents],
                "final_output_len": len(mermaid_code)
            }
            
            eval_prompt = f"Evaluate execution. Trace: {execution_trace}. Code: {mermaid_code[:1000]}..."
            
            eval_result = None
            async for event in eval_runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=types.Content(parts=[types.Part(text=eval_prompt)])
            ):
                if event.is_final_response():
                    eval_result = event
            
            # Robust Parsing
            if eval_result:
                raw_text = ""
                if hasattr(eval_result, 'text') and eval_result.text:
                    raw_text = eval_result.text
                elif hasattr(eval_result, 'content') and hasattr(eval_result.content, 'parts'):
                    for part in eval_result.content.parts:
                        if hasattr(part, 'text'):
                            raw_text += part.text
                
                if not raw_text:
                    raw_text = str(eval_result)

                json_match = re.search(r'(\{[\s\S]*\})', raw_text)
                if json_match:
                    clean_json = json_match.group(1)
                    eval_data = repair_and_parse_json(clean_json)
                    if eval_data:
                        eval_score = eval_data.get('overall_score', 'N/A')
                        feedback = eval_data.get('feedback', 'No feedback')
                        print(f"💡 Feedback: {feedback[:300]}...")
                    else:
                        print(f"⚠️ Warning: JSON parsing failed.")
                else:
                    print(f"⚠️ Warning: No JSON block found.")
            else:
                 print(f"⚠️ Warning: Evaluator returned None.")

        except Exception as e:
            print(f"⚠️ Warning during evaluation: {e}")

        print(f"📈 Overall Score: {eval_score}")
        
        return final_response

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.agent <path/to/pdf>")
        sys.exit(1)
    
    result_msg = asyncio.run(run_process_diagram_workflow(sys.argv[1]))
    print(f"\n🤖 AGENT RESPONSE:\n{result_msg}")