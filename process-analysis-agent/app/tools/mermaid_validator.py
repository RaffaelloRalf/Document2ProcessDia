"""
tools/mermaid_validator.py
Validates Mermaid Diagram Syntax and Logic
"""

import re
from typing import Dict, Any, List

def validate_mermaid_syntax(mermaid_code: str) -> Dict[str, Any]:
    """
    Validates Mermaid code for syntax and logical errors.
    
    Args:
        mermaid_code: The mermaid code string to validate
        
    Returns:
        Dict containing validation results (valid/invalid, errors, warnings)
    """
    errors = []
    warnings = []
    
    # Remove Code Block Wrapper
    code = mermaid_code.strip()
    if code.startswith("```mermaid"):
        code = code.replace("``````", "").strip()
    
    # Split into lines
    lines = [line.strip() for line in code.split("\n") if line.strip()]
    
    # === Syntax Checks ===
    
    # 1. Must start with "flowchart"
    if not lines or not lines[0].startswith("flowchart"):
        errors.append("Mermaid code must start with 'flowchart TD'")
    
    # 2. Extract all defined Node IDs
    defined_nodes = set()
    referenced_nodes = set()
    
    node_pattern = r"^(\w+)[\[\(\{]"  # Matches: NodeID[...], NodeID(...), NodeID{...}
    edge_pattern = r"(\w+)\s*-->.*?(\w+)"  # Matches: Node1 --> Node2 or Node1 -->|label| Node2
    
    for line in lines[1:]:  # Skip first line (flowchart TD)
        # Check for Node Definition
        node_match = re.match(node_pattern, line)
        if node_match:
            defined_nodes.add(node_match.group(1))
        
        # Check for Edges (referencing nodes)
        edge_matches = re.findall(edge_pattern, line)
        for from_node, to_node in edge_matches:
            referenced_nodes.add(from_node)
            referenced_nodes.add(to_node)
    
    # 3. Check: Are all referenced nodes defined?
    undefined_nodes = referenced_nodes - defined_nodes
    if undefined_nodes:
        errors.append(f"Undefined nodes referenced: {', '.join(undefined_nodes)}")
    
    # 4. Check: Orphan Nodes (defined but never referenced)?
    orphan_nodes = defined_nodes - referenced_nodes
    if orphan_nodes:
        warnings.append(f"Unconnected nodes (Orphans): {', '.join(orphan_nodes)}")
    
    # 5. Check: At least one Start/End?
    has_start = any("([" in line for line in lines)
    if not has_start:
        warnings.append("No Start/End event found (Node with '([...])')")
    
    # === Logic Checks ===
    
    # 6. Check: Do Decision Gateways have multiple outputs?
    gateway_pattern = r"(\w+)\{.*?\}"  # Matches: GW1{...}
    gateways = []
    for line in lines:
        gw_match = re.search(gateway_pattern, line)
        if gw_match:
            gateways.append(gw_match.group(1))
    
    for gw in gateways:
        # Count edges originating from this gateway
        outgoing_edges = sum(1 for line in lines if re.search(rf"\b{gw}\s*-->", line))
        if outgoing_edges < 2:
            warnings.append(
                f"Gateway '{gw}' has only {outgoing_edges} outgoing edge(s). "
                f"Expected: at least 2."
            )
    
    # 7. Check: Potentially problematic special characters
    problematic_chars = ["\"", "'", ";", "|"]  # | is OK in labels but risky elsewhere
    for line in lines:
        # Ignore Labels in -->|...|
        cleaned_line = re.sub(r"-->\|.*?\|", "", line)
        for char in problematic_chars:
            if char in cleaned_line:
                warnings.append(
                    f"Potentially problematic character '{char}' in line: {line[:50]}"
                )
                break
    
    # === Summary ===
    
    syntax_valid = len(errors) == 0
    logic_valid = syntax_valid and len([w for w in warnings if "Gateway" in w or "Orphans" in w]) == 0
    
    if syntax_valid and not warnings:
        overall_status = "valid"
    elif syntax_valid:
        overall_status = "needs_improvement"
    else:
        overall_status = "invalid"
    
    result = {
        "syntax_valid": syntax_valid,
        "logic_valid": logic_valid,
        "errors": errors,
        "warnings": warnings,
        "overall_status": overall_status,
        "stats": {
            "defined_nodes": len(defined_nodes),
            "referenced_nodes": len(referenced_nodes),
            "gateways": len(gateways)
        }
    }
    
    # Logging
    if overall_status == "valid":
        print(f"[Mermaid Validator] ✅ Validation successful ({len(defined_nodes)} Nodes)")
    elif overall_status == "needs_improvement":
        print(f"[Mermaid Validator] ⚠️ {len(warnings)} Warnings")
    else:
        print(f"[Mermaid Validator] ❌ {len(errors)} Errors")
    
    return result