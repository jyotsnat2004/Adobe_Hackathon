#!/usr/bin/env python3
"""
Round 1A: PDF Outline Extraction
Main entry point for the Connecting the Dots Challenge
"""

import os
import sys
import glob
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_processor import PDFProcessor
from outline_extractor import OutlineExtractor
from utils import save_json_output

def process_pdf_files(input_dir: str, output_dir: str) -> None:
    """Process all PDF files in input directory and save results to output directory."""
    
    # Initialize processors
    pdf_processor = PDFProcessor()
    outline_extractor = OutlineExtractor()
    
    # Find all PDF files
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    
    # Process each PDF file
    for pdf_file in pdf_files:
        try:
            print(f"Processing: {os.path.basename(pdf_file)}")
            
            # Extract PDF data
            pdf_data = pdf_processor.process_pdf_file(pdf_file)
            
            # Extract outline
            outline_data = outline_extractor.extract_outline(pdf_data)
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}.json")
            
            # Save result
            save_json_output(outline_data, output_file)
            
            print(f"✓ Completed: {base_name}.json")
            print(f"  - Title: {outline_data['title']}")
            print(f"  - Headings found: {len(outline_data['outline'])}")
            
        except Exception as e:
            print(f"✗ Error processing {pdf_file}: {str(e)}")
            # Create error output
            error_data = {
                "title": f"Error Processing {os.path.basename(pdf_file)}",
                "outline": []
            }
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}.json")
            save_json_output(error_data, output_file)

def main():
    """Main function."""
    
    # Define input and output directories
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Ensure directories exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== PDF Outline Extraction (Round 1A) ===")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Process PDF files
    process_pdf_files(input_dir, output_dir)
    
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