#!/usr/bin/env python3
"""
Test script for the PDF Intelligence System
Tests both Round 1A and Round 1B functionality
"""

import os
import sys
import tempfile
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor
from round1a.outline_extractor import OutlineExtractor
from round1b.persona_analyzer import PersonaAnalyzer
from utils import save_json_output

def create_sample_pdf_content():
    """Create a sample PDF-like text content for testing."""
    return """
    Understanding Artificial Intelligence
    
    Introduction
    Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines.
    
    What is AI?
    AI refers to the simulation of human intelligence in machines.
    
    History of AI
    The field of AI was founded in 1956 at a conference at Dartmouth College.
    
    Machine Learning
    Machine learning is a subset of AI that enables computers to learn without being explicitly programmed.
    
    Deep Learning
    Deep learning uses neural networks with multiple layers to process data.
    
    Applications
    AI has applications in various fields including healthcare, finance, and transportation.
    
    Conclusion
    AI continues to evolve and will play an increasingly important role in our lives.
    """

def test_round_1a():
    """Test Round 1A functionality."""
    print("=== Testing Round 1A: PDF Outline Extraction ===")
    
    # Create sample PDF data
    sample_text = create_sample_pdf_content()
    pdf_data = {
        "text": sample_text,
        "title": "Understanding Artificial Intelligence",
        "metadata": {
            "pages": [
                {
                    "page_number": 1,
                    "text_blocks": [
                        {"text": "Understanding Artificial Intelligence", "font_size": 18, "font_name": "Arial-Bold"},
                        {"text": "Introduction", "font_size": 16, "font_name": "Arial-Bold"},
                        {"text": "What is AI?", "font_size": 14, "font_name": "Arial-Bold"},
                        {"text": "History of AI", "font_size": 14, "font_name": "Arial-Bold"},
                        {"text": "Machine Learning", "font_size": 14, "font_name": "Arial-Bold"},
                        {"text": "Deep Learning", "font_size": 12, "font_name": "Arial-Bold"},
                        {"text": "Applications", "font_size": 14, "font_name": "Arial-Bold"},
                        {"text": "Conclusion", "font_size": 16, "font_name": "Arial-Bold"}
                    ]
                }
            ]
        }
    }
    
    # Test outline extraction
    extractor = OutlineExtractor()
    outline = extractor.extract_outline(pdf_data)
    
    print(f"Title: {outline['title']}")
    print(f"Headings found: {len(outline['outline'])}")
    
    for heading in outline['outline']:
        print(f"  - {heading['level']}: {heading['text']} (Page {heading['page']})")
    
    # Validate output format
    assert "title" in outline
    assert "outline" in outline
    assert isinstance(outline["outline"], list)
    
    print("✓ Round 1A test passed")
    return outline

def test_round_1b():
    """Test Round 1B functionality."""
    print("\n=== Testing Round 1B: Persona-Driven Analysis ===")
    
    # Create sample documents
    documents = [
        {
            "file_path": "research_paper_1.pdf",
            "title": "Graph Neural Networks for Drug Discovery",
            "text": """
            Abstract
            This paper presents a novel approach to drug discovery using graph neural networks.
            
            Introduction
            Drug discovery is a complex process that requires understanding molecular structures.
            
            Methodology
            We use graph neural networks to model molecular interactions and predict drug efficacy.
            
            Results
            Our approach achieves 85% accuracy in predicting drug-target interactions.
            
            Conclusion
            Graph neural networks show promise for accelerating drug discovery processes.
            """
        },
        {
            "file_path": "research_paper_2.pdf",
            "title": "Machine Learning in Computational Biology",
            "text": """
            Abstract
            Machine learning techniques are revolutionizing computational biology.
            
            Background
            Traditional methods in computational biology have limitations in handling large datasets.
            
            Methods
            We apply various machine learning algorithms to biological data analysis.
            
            Results
            Our methods improve prediction accuracy by 20% compared to traditional approaches.
            
            Discussion
            The integration of ML in computational biology opens new research opportunities.
            """
        }
    ]
    
    # Test persona analysis
    analyzer = PersonaAnalyzer()
    persona = "PhD Researcher in Computational Biology"
    job = "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
    
    result = analyzer.analyze_documents(documents, persona, job)
    
    print(f"Persona: {result['metadata']['persona']}")
    print(f"Job: {result['metadata']['job_to_be_done']}")
    print(f"Documents processed: {len(result['metadata']['input_documents'])}")
    print(f"Extracted sections: {len(result['extracted_sections'])}")
    print(f"Sub-sections: {len(result['sub_section_analysis'])}")
    
    # Print top sections
    print("\nTop sections:")
    for i, section in enumerate(result['extracted_sections'][:3], 1):
        print(f"  {i}. {section['section_title']} (Rank: {section['importance_rank']:.2f})")
    
    # Validate output format
    assert "metadata" in result
    assert "extracted_sections" in result
    assert "sub_section_analysis" in result
    
    print("✓ Round 1B test passed")
    return result

def test_utils():
    """Test utility functions."""
    print("\n=== Testing Utility Functions ===")
    
    from utils import clean_text, is_heading_candidate, get_heading_level
    
    # Test text cleaning
    dirty_text = "  This   is   a   test   text  "
    clean = clean_text(dirty_text)
    assert clean == "This is a test text"
    
    # Test heading detection
    assert is_heading_candidate("Introduction") == True
    assert is_heading_candidate("This is a regular paragraph.") == False
    
    # Test heading level determination
    assert get_heading_level(18, "Arial-Bold", "Introduction") == "H1"
    assert get_heading_level(14, "Arial", "random text") == "H2"  # Font size 14 = H2
    
    print("✓ Utility functions test passed")

def test_performance():
    """Test performance characteristics."""
    print("\n=== Testing Performance ===")
    
    import time
    
    # Test processing speed
    start_time = time.time()
    
    # Simulate processing a 50-page document
    large_text = create_sample_pdf_content() * 50  # Simulate 50 pages
    
    pdf_data = {
        "text": large_text,
        "title": "Large Test Document",
        "metadata": {"pages": []}
    }
    
    extractor = OutlineExtractor()
    outline = extractor.extract_outline(pdf_data)
    
    processing_time = time.time() - start_time
    
    print(f"Processing time: {processing_time:.2f} seconds")
    assert processing_time < 10.0, f"Processing took {processing_time} seconds, should be < 10 seconds"
    
    print("✓ Performance test passed")

def main():
    """Run all tests."""
    print("Starting PDF Intelligence System Tests")
    print("=" * 50)
    
    try:
        test_utils()
        test_round_1a()
        test_round_1b()
        test_performance()
        
        print("\n" + "=" * 50)
        print("✓ All tests passed successfully!")
        print("The system is ready for deployment.")
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 