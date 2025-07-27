import os
import pdfplumber
import PyPDF2
from typing import List, Dict, Any, Tuple
from utils import clean_text, extract_title_from_text

class PDFProcessor:
    """Core PDF processing class for text extraction and analysis."""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def extract_text_with_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text and metadata from PDF using multiple methods."""
        try:
            # Method 1: Using pdfplumber for detailed text extraction
            plumber_text, plumber_metadata = self._extract_with_pdfplumber(pdf_path)
            
            # Method 2: Using PyPDF2 as backup
            pypdf_text = self._extract_with_pypdf2(pdf_path)
            
            # Combine results
            combined_text = plumber_text if plumber_text else pypdf_text
            combined_text = clean_text(combined_text)
            
            # Extract title
            title = extract_title_from_text(combined_text)
            
            return {
                "text": combined_text,
                "title": title,
                "metadata": plumber_metadata,
                "pages": len(plumber_metadata.get("pages", [])),
                "file_path": pdf_path
            }
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return {
                "text": "",
                "title": "Error Processing Document",
                "metadata": {},
                "pages": 0,
                "file_path": pdf_path,
                "error": str(e)
            }
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text using pdfplumber with detailed metadata."""
        text_parts = []
        metadata = {"pages": []}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                    
                    # Collect page metadata
                    page_metadata = {
                        "page_number": page_num,
                        "width": page.width,
                        "height": page.height,
                        "text_blocks": []
                    }
                    
                    # Extract text blocks with positioning
                    if page.chars:
                        text_blocks = self._extract_text_blocks(page)
                        page_metadata["text_blocks"] = text_blocks
                    
                    metadata["pages"].append(page_metadata)
                
                # Combine all text
                full_text = "\n".join(text_parts)
                return full_text, metadata
                
        except Exception as e:
            print(f"pdfplumber extraction failed: {str(e)}")
            return "", {"pages": []}
    
    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2 as backup method."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_parts = []
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                return "\n".join(text_parts)
                
        except Exception as e:
            print(f"PyPDF2 extraction failed: {str(e)}")
            return ""
    
    def _extract_text_blocks(self, page) -> List[Dict[str, Any]]:
        """Extract text blocks with positioning and font information."""
        text_blocks = []
        
        if not page.chars:
            return text_blocks
        
        # Group characters by font properties
        font_groups = {}
        
        for char in page.chars:
            font_name = char.get('fontname', 'unknown')
            font_size = char.get('size', 0)
            font_key = f"{font_name}_{font_size}"
            
            if font_key not in font_groups:
                font_groups[font_key] = {
                    'text': '',
                    'font_name': font_name,
                    'font_size': font_size,
                    'x0': char.get('x0', 0),
                    'y0': char.get('y0', 0),
                    'x1': char.get('x1', 0),
                    'y1': char.get('y1', 0),
                    'chars': []
                }
            
            font_groups[font_key]['text'] += char.get('text', '')
            font_groups[font_key]['chars'].append(char)
        
        # Convert to text blocks
        for font_key, group in font_groups.items():
            if group['text'].strip():
                text_blocks.append({
                    'text': group['text'].strip(),
                    'font_name': group['font_name'],
                    'font_size': group['font_size'],
                    'x0': group['x0'],
                    'y0': group['y0'],
                    'x1': group['x1'],
                    'y1': group['y1'],
                    'bbox': (group['x0'], group['y0'], group['x1'], group['y1'])
                })
        
        # Sort by position (top to bottom, left to right)
        text_blocks.sort(key=lambda x: (-x['y0'], x['x0']))
        
        return text_blocks
    
    def process_pdf_file(self, pdf_path: str) -> Dict[str, Any]:
        """Process a single PDF file and return structured data."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError(f"File is not a PDF: {pdf_path}")
        
        return self.extract_text_with_metadata(pdf_path)
    
    def process_multiple_pdfs(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """Process multiple PDF files."""
        results = []
        
        for pdf_path in pdf_paths:
            try:
                result = self.process_pdf_file(pdf_path)
                results.append(result)
            except Exception as e:
                print(f"Failed to process {pdf_path}: {str(e)}")
                results.append({
                    "text": "",
                    "title": f"Error: {os.path.basename(pdf_path)}",
                    "metadata": {},
                    "pages": 0,
                    "file_path": pdf_path,
                    "error": str(e)
                })
        
        return results 