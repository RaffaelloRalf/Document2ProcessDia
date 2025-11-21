# Process Analysis Agent: Automated Process Diagram Generation

## 🚀 Overview: Enterprise Agent Track Submission

This project, the **Process Analysis Agent**, is a highly automated multi-agent system designed to streamline core business documentation. It instantly converts unstructured text—such as process descriptions from standard operating procedures (SOPs) or internal memos—into formal, visual Mermaid flowcharts.

This agent is submitted in the **Enterprise Agents** track, focusing on automating complex business workflows and improving data analysis.

---

## I. The Pitch (Category 1: Problem, Solution, Value)

### 1. Problem Statement
In large organizations, complex process documentation (SOPs, compliance manuals, internal guides) is often stored as lengthy, unstructured text. This leads to:
1.  **High Interpretation Risk:** Non-visualized processes are prone to misinterpretation and errors.
2.  **Time Sink:** Manually creating or updating BPMN/Flowcharts is a slow, tedious task for business analysts (BAs).
3.  **Low Compliance:** Documentation quickly falls out of sync with actual process execution.

### 2. Solution Pitch: Agentic Automation
The **Process Analysis Agent** solves this by implementing a structured, multi-agent workflow powered by Google's Agent Development Kit (ADK) and Gemini models. The agent transforms the raw text into a machine-readable graph structure, validates it, and generates a final, shareable diagram.

### 3. Value Proposition (The "Why Agents?")
This agent drastically reduces the time required for process visualization from **hours to seconds**.
* **Unique Agent Advantage:** Only a multi-agent system can handle this task reliably, requiring cognitive delegation: (1) **Extraction** (LLM), (2) **Refinement** (Loop), (3) **Validation** (Tool), and (4) **Publication** (Tool).
* **Result:** Faster documentation, improved process clarity, and reduced compliance risk.

---

## II. Technical Implementation (Category 2: Architecture & Code)

### 1. Agent Architecture (Sequential and Collaborative)

The system uses a highly modular design with a **SequentialAgent** as the root orchestrator. Data is passed between agents using the shared **Session State**.

#### A. Architecture Diagram
The architecture follows a strict, deterministic sequence:

```mermaid
graph TD
    classDef orchestrator fill:#3f51b5,stroke:#fff,stroke-width:2px,color:#fff;
    classDef agent fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef loop fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,stroke-dasharray: 5 5,color:#000;
    classDef tool fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,rx:5,ry:5,color:#000;
    classDef state fill:#f3e5f5,stroke:#8e24aa,stroke-width:1px,shape:cyl,color:#000;
    classDef eval fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

    Start([User Input / PDF Path]) --> Root[ProcessDiagramRootAgent]:::orchestrator
    
    subgraph Workflow [Execution Chain]
        direction TB
        
        Root --> Ag1
        Ag1[1. PDFTextExtractionAgent]:::agent --> Ag2
        Ag2[2. PDFAnalysisAgent]:::agent --> Ag3
        
        subgraph Loop [3. QualityLoopAgent]
            Ag3a[ConversionAgent]:::agent --> Ag3b
            Ag3b[QualityAgent]:::agent --> Dec{Approved?}
            Dec -- No --> Ag3a
            Dec -- Yes --> LoopEnd((Exit))
            class Loop loop
        end
        
        LoopEnd --> Ag4
        Ag4[4. BPMNGenerationAgent]:::agent --> Ag5
        Ag5[5. ValidationAgent]:::agent --> Ag6
        Ag6[6. ApprovalAgent (HITL)]:::agent --> Ag7
        Ag7[7. PublicationAgent]:::agent --> EndChain([End Workflow])
    end

    EndChain -.-> Eval[SystemEvaluatorAgent (Judge)]:::eval
    
    %% State and Tool Interactions
    Ag1 -.->|writes path & text| State((Session State)):::state
    Ag2 -.->|reads text| State
    Ag4 -.->|writes code| State
    Ag6 -.->|reads code| State
    Ag7 -.->|reads code & path| State
    
    Ag1 -->|Tool| T1[parse_pdf]:::tool
    Ag7 -->|Tools| T2[render_mermaid]:::tool
    Ag7 -->|Tools| T3[save_report]:::tool

````

### 2\. Key Concepts Applied (Criteria Check)

| Feature | Concept Applied | Evidence in Code |
| :--- | :--- | :--- |
| **Multi-agent system** | Sequential Agent & Loop Agent | `ProcessDiagramRootAgent` (Sequential) and `QualityLoopAgent` (Loop) |
| **Tools** | custom tools | `parse_pdf`, `save_diagram`, `save_report`, `render_mermaid_to_svg` (all custom functions) |
| **Long-running operations** | Pause/Resume Agents (HITL) | `ApprovalAgent` uses `request_publication_approval` and `ToolContext` to pause execution until user clicks "Approve". |
| **Sessions & State** | Sessions & state management | Uses `InMemorySessionService` to pass data (`current_mermaid_code`, `pdf_path`) across all 7 agents. |
| **Agent Evaluation** | Agent evaluation | `SystemEvaluatorAgent` runs post-process to calculate a numerical `overall_score` (0-1.0) and provides structured feedback. |
| **Bonus: Effective Use of Gemini** | Model Specialization | Uses `Gemini-2.5-Flash` for fast processing agents (Extraction/Conversion) and `Gemini-2.5-Pro` for high-reasoning tasks (Evaluation). |

### 3\. Setup Instructions (for Judging)

The project is designed to run locally using the Python ADK and `uv`.

#### Prerequisites

1.  Python 3.11+
2.  `uv` (Installed automatically via Makefile)
3.  `GEMINI_API_KEY` (Set in a `.env` file in the project root)
4.  `npm` (for `mermaid-cli` dependencies)

#### Setup

Navigate to the `process-analysis-agent` directory.

```bash
# 1. Install System Dependencies (for rendering)
npm install -g @mermaid-js/mermaid-cli

# 2. Install Python dependencies and create virtual environment
make install

# 3. Create a test PDF (or place your own PDF in app/test_data/)
# Example: Create the file app/test_data/sample_process.pdf

# 4. Final step for judge safety
# Ensure .env file contains: GEMINI_API_KEY=AIza...
```

#### Run Modes

| Mode | Command | Purpose |
| :--- | :--- | :--- |
| **1. Local CLI Test (Auto-Approve)** | `make run` | Runs a complete workflow, auto-approving the HITL step for quick testing. Files saved to `outputs/`. |
| **2. Interactive Web Demo (HITL)** | `make web` | Starts the server (http://localhost:8000). Agent will **pause** at the Approval step, waiting for the user to click "Confirm" in the UI. |

```
```