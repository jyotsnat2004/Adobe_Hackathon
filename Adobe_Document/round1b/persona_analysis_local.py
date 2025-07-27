#!/usr/bin/env python3
"""
Round 1B: Persona-Driven Document Intelligence (Local Version)
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
from utils import save_json_output

def load_config(config_file: str) -> Dict[str, str]:
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return {
            "persona": "Default Persona",
            "job_to_be_done": "Default job description"
        }

def process_documents(input_dir: str, output_dir: str, config: Dict[str, str]) -> None:
    """Process all PDF files and perform persona-driven analysis."""
    
    # Initialize processors
    pdf_processor = PDFProcessor()
    persona_analyzer = PersonaAnalyzer()
    
    # Find all PDF files
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    
    # Process all documents
    all_documents = []
    for pdf_file in pdf_files:
        try:
            print(f"Processing: {os.path.basename(pdf_file)}")
            
            # Extract PDF data
            pdf_data = pdf_processor.process_pdf_file(pdf_file)
            all_documents.append({
                'filename': os.path.basename(pdf_file),
                'data': pdf_data
            })
            
        except Exception as e:
            print(f"✗ Error processing {pdf_file}: {str(e)}")
    
    if not all_documents:
        print("No documents could be processed")
        return
    
    # Perform persona-driven analysis
    try:
        print(f"\nPerforming persona-driven analysis...")
        print(f"Persona: {config['persona']}")
        print(f"Job-to-be-done: {config['job_to_be_done']}")
        
        analysis_result = persona_analyzer.analyze_documents(
            all_documents, 
            config['persona'], 
            config['job_to_be_done']
        )
        
        # Add metadata
        analysis_result['metadata'] = {
            'input_documents': [doc['filename'] for doc in all_documents],
            'persona': config['persona'],
            'job_to_be_done': config['job_to_be_done'],
            'processing_timestamp': persona_analyzer._get_timestamp()
        }
        
        # Save result
        output_file = os.path.join(output_dir, "persona_analysis_result.json")
        save_json_output(analysis_result, output_file)
        
        print(f"✓ Completed: persona_analysis_result.json")
        print(f"  - Documents analyzed: {len(all_documents)}")
        print(f"  - Relevant sections found: {len(analysis_result.get('extracted_sections', []))}")
        print(f"  - Sub-sections analyzed: {len(analysis_result.get('sub_section_analysis', []))}")
        
    except Exception as e:
        print(f"✗ Error in persona analysis: {str(e)}")

def main():
    """Main function."""
    
    # Define input and output directories (local paths)
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(current_dir, "input")
    output_dir = os.path.join(current_dir, "output")
    
    # Ensure directories exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== Persona-Driven Document Intelligence (Round 1B) ===")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Load configuration
    config_file = os.path.join(input_dir, "config.json")
    if not os.path.exists(config_file):
        print(f"Config file not found: {config_file}")
        print("Please create config.json in the input directory with persona and job_to_be_done")
        return
    
    config = load_config(config_file)
    
    # Process documents
    process_documents(input_dir, output_dir, config)
    
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