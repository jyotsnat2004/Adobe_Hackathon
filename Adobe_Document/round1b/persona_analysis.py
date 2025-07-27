#!/usr/bin/env python3
"""
Round 1B: Persona-Driven Document Intelligence
Main entry point for the Connecting the Dots Challenge
"""

import os
import sys
import glob
import json
from typing import List, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_processor import PDFProcessor
from persona_analyzer import PersonaAnalyzer
from utils import save_json_output, get_timestamp

def load_config(config_file: str = "/app/input/config.json") -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_file}")
        return {}
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return {}

def process_persona_analysis(input_dir: str, output_dir: str) -> None:
    """Process persona-driven analysis on PDF documents."""
    
    # Initialize processors
    pdf_processor = PDFProcessor()
    persona_analyzer = PersonaAnalyzer()
    
    # Load configuration
    config = load_config()
    
    # Extract configuration parameters
    persona = config.get("persona", "Research Analyst")
    job_to_be_done = config.get("job_to_be_done", "Analyze document content")
    
    # Find all PDF files
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    print(f"Persona: {persona}")
    print(f"Job to be done: {job_to_be_done}")
    print()
    
    # Process all PDF files
    documents = []
    for pdf_file in pdf_files:
        try:
            print(f"Processing: {os.path.basename(pdf_file)}")
            
            # Extract PDF data
            pdf_data = pdf_processor.process_pdf_file(pdf_file)
            documents.append(pdf_data)
            
            print(f"✓ Completed: {os.path.basename(pdf_file)}")
            print(f"  - Title: {pdf_data['title']}")
            print(f"  - Pages: {pdf_data['pages']}")
            
        except Exception as e:
            print(f"✗ Error processing {pdf_file}: {str(e)}")
    
    if not documents:
        print("No documents processed successfully")
        return
    
    print(f"\nAnalyzing {len(documents)} document(s) for persona: {persona}")
    
    # Perform persona-driven analysis
    try:
        analysis_result = persona_analyzer.analyze_documents(
            documents, persona, job_to_be_done
        )
        
        # Save result
        output_file = os.path.join(output_dir, "persona_analysis.json")
        save_json_output(analysis_result, output_file)
        
        print(f"✓ Analysis completed: persona_analysis.json")
        print(f"  - Extracted sections: {len(analysis_result['extracted_sections'])}")
        print(f"  - Sub-sections: {len(analysis_result['sub_section_analysis'])}")
        
        # Print top sections
        print("\nTop relevant sections:")
        for i, section in enumerate(analysis_result['extracted_sections'][:5], 1):
            print(f"  {i}. {section['section_title']} (Rank: {section['importance_rank']:.2f})")
        
    except Exception as e:
        print(f"✗ Error during analysis: {str(e)}")
        
        # Create error output
        error_result = {
            "metadata": {
                "input_documents": [doc.get("file_path", "unknown") for doc in documents],
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "processing_timestamp": get_timestamp(),
                "error": str(e)
            },
            "extracted_sections": [],
            "sub_section_analysis": []
        }
        
        output_file = os.path.join(output_dir, "persona_analysis.json")
        save_json_output(error_result, output_file)

def main():
    """Main function."""
    
    # Define input and output directories
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Ensure directories exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== Persona-Driven Document Intelligence (Round 1B) ===")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Process documents
    process_persona_analysis(input_dir, output_dir)
    
    print()
    print("=== Processing Complete ===")
    
    # List output files
    output_files = glob.glob(os.path.join(output_dir, "*.json"))
    if output_files:
        print(f"Generated {len(output_files)} output file(s):")
        for output_file in output_files:
            print(f"  - {os.path.basename(output_file)}")

if __name__ == "__main__":
    main() 