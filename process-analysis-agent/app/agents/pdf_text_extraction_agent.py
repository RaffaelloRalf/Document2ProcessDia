"""
agents/pdf_text_extraction_agent.py
Agent 1.1: PDF Text Extraction Agent
Extracts text from PDF documents using the 'parse_pdf' tool.
"""

from google.adk.agents import LlmAgent
from google.genai import types
from app import config

# Import custom tools
from app.tools.pdf_parser import parse_pdf

def create_pdf_text_extraction_agent() -> LlmAgent:
    """
    Creates the PDF Text Extraction Agent.
    
    This agent uses the 'parse_pdf' tool to extract text from a PDF document.
    The extracted text is stored under 'extracted_pdf_text' in the session state.
    
    Returns:
        LlmAgent configured for PDF text extraction
    """
    
    agent = LlmAgent(
        name="PDFTextExtractionAgent",
        model=config.MODEL_FLASH_THINKING,
        instruction=(
            "You are a helpful assistant specialized in extracting text from PDF documents. "
            "Your task is to use the 'parse_pdf' tool. "
            "The user will provide the file path in their message (e.g. 'The source PDF is located at...'). "
            "\n\n"
            "STEPS:\n"
            "1. Identify the file path.\n"
            "2. Call the 'parse_pdf' tool with this path.\n"
            "3. The tool will return the text. **Simply return this text as your final response.**\n"
            "4. Do NOT try to save the text to the session state yourself (no 'set_state' calls needed).\n"
            "   The system automatically saves your output."
        ),
        description=(
            "Extracts text content from a PDF document using the 'parse_pdf' tool. "
            "Stores the extracted text in the session state for further processing."
        ),
        tools=[parse_pdf],
        output_key="extracted_pdf_text",
        generate_content_config=types.GenerateContentConfig(
            temperature=0.0,  # Deterministic output
        )
    )
    
    print(f"✅ {agent.name} created (Model: {config.MODEL_FLASH_THINKING}, Tool: parse_pdf)")
    return agent