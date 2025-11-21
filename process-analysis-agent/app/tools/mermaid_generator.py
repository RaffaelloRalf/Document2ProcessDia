"""
tools/mermaid_generator.py
Tools for Mermaid diagram generation and rendering
"""

import json
import subprocess
import os
from typing import Dict, Any
from app import config

def render_mermaid_to_svg(mermaid_code: str, output_path: str = "auto") -> Dict[str, Any]:
    """
    Renders Mermaid code to SVG using mermaid-cli (mmdc).
    
    Args:
        mermaid_code: The Mermaid code (with or without ```)
        output_path: Path for output SVG (optional, auto-generated if "auto")
        
    Returns:
        Dict with 'success', 'svg_path' and 'message'
    """
    try:
        # Clean code
        cleaned_code = mermaid_code.strip()
        if cleaned_code.startswith("```mermaid"):
            cleaned_code = cleaned_code.replace("```mermaid", "").replace("```", "").strip()
            
        import tempfile
        import uuid
        
        # Ensure OUTPUT_DIR exists (Global config)
        if not os.path.exists(config.OUTPUT_DIR):
            os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        
        temp_id = str(uuid.uuid4())[:8]
        temp_mmd = os.path.join(config.OUTPUT_DIR, f"temp_{temp_id}.mmd")
        
        with open(temp_mmd, "w", encoding="utf-8") as f:
            f.write(cleaned_code)
        
        # Determine output path
        if not output_path or output_path == "auto":
            output_path = os.path.join(config.OUTPUT_DIR, f"process_diagram_{temp_id}.svg")
        
        # --- FIX START: Ensure parent directory of output_path exists ---
        # This catches cases where the agent uses "output/" instead of "outputs/"
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
             os.makedirs(output_dir, exist_ok=True)
        # --- FIX END ----------------------------------------------------
        
        # Run mmdc
        cmd = [
            config.MERMAID_CLI,
            "-i", temp_mmd,
            "-o", output_path,
            "-t", "default",  # Theme
            "-b", "transparent"  # Background
        ]
        
        print(f"[Mermaid Renderer] Rendering SVG...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Cleanup temp file
        if os.path.exists(temp_mmd):
            os.remove(temp_mmd)
        
        if result.returncode == 0:
            print(f"[Mermaid Renderer] ✅ SVG created: {output_path}")
            return {
                "success": True,
                "svg_path": output_path,
                "message": f"SVG successfully created"
            }
        else:
            error_msg = f"mmdc Error: {result.stderr}"
            print(f"[Mermaid Renderer] ❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "svg_path": None
            }
            
    except subprocess.TimeoutExpired:
        error_msg = "mmdc Timeout (>30s)"
        print(f"[Mermaid Renderer] ❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "svg_path": None
        }
    
    except FileNotFoundError:
        error_msg = (
            "mmdc not found! "
            "Please install: npm install -g @mermaid-js/mermaid-cli"
        )
        print(f"[Mermaid Renderer] ❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "svg_path": None
        }
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"[Mermaid Renderer] ❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "svg_path": None
        }


def generate_mermaid_code(process_structure: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts a Process Structure (Nodes + Edges) into Mermaid code.
    
    This function is technically redundant as the BPMN Generation Agent
    creates Mermaid code directly. We keep it as a fallback or utility.
    """
    try:
        nodes = process_structure.get("nodes", [])
        edges = process_structure.get("edges", [])
        
        if not nodes:
            return {
                "success": False,
                "error": "No nodes found in process structure",
                "mermaid_code": ""
            }
        
        # Start Mermaid Flowchart
        mermaid_lines = ["flowchart TD"]
        
        # Generate Node Definitions
        for node in nodes:
            node_id = node.get("id", "")
            node_type = node.get("type", "task")
            label = node.get("label", node_id)
            
            # Select syntax based on node type
            if node_type == "start_event":
                mermaid_lines.append(f"    {node_id}([{label}])")
            elif node_type == "end_event":
                mermaid_lines.append(f"    {node_id}([{label}])")
            elif node_type in ["exclusive_gateway", "decision"]:
                mermaid_lines.append(f"    {node_id}{{{label}?}}")
            else:  # task
                mermaid_lines.append(f"    {node_id}[{label}]")
        
        # Generate Edges
        for edge in edges:
            from_node = edge.get("from", "")
            to_node = edge.get("to", "")
            edge_label = edge.get("label", "")
            
            if edge_label:
                mermaid_lines.append(f"    {from_node} -->|{edge_label}| {to_node}")
            else:
                mermaid_lines.append(f"    {from_node} --> {to_node}")
        
        # Combine
        mermaid_code = "\n".join(mermaid_lines)
        full_code = f"```mermaid\n{mermaid_code}\n```"
        
        print(f"[Mermaid Generator] ✅ Code generated ({len(nodes)} Nodes, {len(edges)} Edges)")
        
        return {
            "success": True,
            "mermaid_code": full_code,
            "message": "Mermaid code successfully generated"
        }
        
    except Exception as e:
        error_msg = f"❌ Error generating Mermaid: {str(e)}"
        print(f"[Mermaid Generator] {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "mermaid_code": ""
        }