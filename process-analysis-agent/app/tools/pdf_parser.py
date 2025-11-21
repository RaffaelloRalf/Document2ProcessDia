"""
tools/pdf_parser.py
Custom Tool for PDF Parsing using PyPDF2
Now with Session State integration!
"""

import json
from typing import Dict, Any
from PyPDF2 import PdfReader
from google.adk.tools import ToolContext  
from app import config

def parse_pdf(pdf_path: str, tool_context: ToolContext = None) -> Dict[str, Any]:
    """
    Extracts text from a PDF and saves the path to session state.
    
    Args:
        pdf_path: Path to the PDF file
        tool_context: ADK Tool Context (injected automatically)
        
    Returns:
        Dict containing extracted_text and metadata
    """
    try:
        # --- AGENTIC MAGIC: Save path to state automatically ---
        if tool_context:
            print(f"[PDF Parser] 💾 Saving pdf_path to session state: {pdf_path}")
            tool_context.session.state["pdf_path"] = pdf_path
        # -------------------------------------------------------

        # Open PDF
        reader = PdfReader(pdf_path)
        
        # Check page count
        num_pages = len(reader.pages)
        if num_pages > config.PDF_MAX_PAGES:
            raise ValueError(
                f"PDF has {num_pages} pages, "
                f"maximum allowed is {config.PDF_MAX_PAGES}"
            )
        
        # Extract text from all pages
        extracted_text = ""
        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                extracted_text += f"\n--- Page {page_num} ---\n{page_text}"
        
        # Metadata
        metadata = {
            "num_pages": num_pages,
            "title": reader.metadata.title if reader.metadata else None,
            "author": reader.metadata.author if reader.metadata else None
        }
        
        result = {
            "success": True,
            "extracted_text": extracted_text.strip(),
            "metadata": metadata,
            "message": f"✅ Successfully extracted {num_pages} pages"
        }
        
        print(f"[PDF Parser] {result['message']}")
        return result
        
    except FileNotFoundError:
        error_msg = f"❌ PDF not found: {pdf_path}"
        print(f"[PDF Parser] {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "extracted_text": "",
            "metadata": {}
        }
    
    except Exception as e:
        error_msg = f"❌ Error parsing PDF: {str(e)}"
        print(f"[PDF Parser] {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "extracted_text": "",
            "metadata": {}
        }