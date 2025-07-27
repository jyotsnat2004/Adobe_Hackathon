import re
from typing import List, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import is_heading_candidate, get_heading_level, clean_text

class OutlineExtractor:
    """Extract hierarchical outline from PDF documents."""
    
    def __init__(self):
        self.heading_patterns = [
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS
            r'^\d+\.\s+[A-Z]',   # Numbered headings
            r'^\d+\.\d+\s+[A-Z]', # Sub-numbered headings
            r'^\d+\.\d+\.\d+\s+[A-Z]', # Sub-sub-numbered headings
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$',  # Title Case
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s*$',  # Title Case with trailing space
        ]
        
        self.heading_keywords = [
            'introduction', 'conclusion', 'abstract', 'summary', 'background',
            'method', 'methodology', 'results', 'discussion', 'analysis',
            'overview', 'review', 'related work', 'literature review',
            'chapter', 'section', 'part', 'appendix', 'references',
            'executive summary', 'table of contents', 'acknowledgments'
        ]
    
    def extract_outline(self, pdf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract outline from PDF data."""
        text = pdf_data.get("text", "")
        metadata = pdf_data.get("metadata", {})
        
        if not text:
            return {
                "title": pdf_data.get("title", "Untitled Document"),
                "outline": []
            }
        
        # Extract headings using multiple methods
        headings = []
        
        # Method 1: Font-based extraction
        font_headings = self._extract_headings_by_font(metadata)
        headings.extend(font_headings)
        
        # Method 2: Pattern-based extraction
        pattern_headings = self._extract_headings_by_pattern(text)
        headings.extend(pattern_headings)
        
        # Method 3: Content-based extraction
        content_headings = self._extract_headings_by_content(text)
        headings.extend(content_headings)
        
        # Remove duplicates and sort
        unique_headings = self._deduplicate_headings(headings)
        sorted_headings = self._sort_headings(unique_headings)
        
        # Convert to required format
        outline = []
        for heading in sorted_headings:
            outline.append({
                "level": heading["level"],
                "text": heading["text"],
                "page": heading["page"]
            })
        
        return {
            "title": pdf_data.get("title", "Untitled Document"),
            "outline": outline
        }
    
    def _extract_headings_by_font(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract headings based on font properties."""
        headings = []
        
        for page_data in metadata.get("pages", []):
            page_num = page_data.get("page_number", 1)
            text_blocks = page_data.get("text_blocks", [])
            
            for block in text_blocks:
                text = block.get("text", "").strip()
                if not text or len(text) < 2:
                    continue
                
                font_size = block.get("font_size", 0)
                font_name = block.get("font_name", "")
                
                # Determine if this looks like a heading
                if self._is_font_heading(font_size, font_name, text):
                    level = get_heading_level(font_size, font_name, text)
                    if level != "BODY":
                        headings.append({
                            "text": text,
                            "level": level,
                            "page": page_num,
                            "font_size": font_size,
                            "font_name": font_name
                        })
        
        return headings
    
    def _extract_headings_by_pattern(self, text: str) -> List[Dict[str, Any]]:
        """Extract headings based on text patterns."""
        headings = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or len(line) < 2:
                continue
            
            # Check against heading patterns
            if self._matches_heading_pattern(line):
                # Determine level based on pattern
                level = self._determine_level_by_pattern(line)
                headings.append({
                    "text": line,
                    "level": level,
                    "page": 1,  # Default page, will be refined later
                    "line_number": line_num
                })
        
        return headings
    
    def _extract_headings_by_content(self, text: str) -> List[Dict[str, Any]]:
        """Extract headings based on content analysis."""
        headings = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or len(line) < 2:
                continue
            
            # Check if line contains heading keywords
            if self._contains_heading_keywords(line):
                # Determine level based on content
                level = self._determine_level_by_content(line)
                headings.append({
                    "text": line,
                    "level": level,
                    "page": 1,  # Default page, will be refined later
                    "line_number": line_num
                })
        
        return headings
    
    def _is_font_heading(self, font_size: float, font_name: str, text: str) -> bool:
        """Determine if text block is a heading based on font properties."""
        # Large font size
        if font_size >= 14:
            return True
        
        # Bold font
        if 'bold' in font_name.lower() or 'black' in font_name.lower():
            return True
        
        # Check text content
        if is_heading_candidate(text):
            return True
        
        return False
    
    def _matches_heading_pattern(self, text: str) -> bool:
        """Check if text matches heading patterns."""
        for pattern in self.heading_patterns:
            if re.match(pattern, text):
                return True
        return False
    
    def _contains_heading_keywords(self, text: str) -> bool:
        """Check if text contains heading keywords."""
        text_lower = text.lower()
        for keyword in self.heading_keywords:
            if keyword in text_lower:
                return True
        return False
    
    def _determine_level_by_pattern(self, text: str) -> str:
        """Determine heading level based on pattern."""
        # Numbered headings
        if re.match(r'^\d+\.\s+', text):
            return "H1"
        elif re.match(r'^\d+\.\d+\s+', text):
            return "H2"
        elif re.match(r'^\d+\.\d+\.\d+\s+', text):
            return "H3"
        
        # ALL CAPS
        if re.match(r'^[A-Z][A-Z\s]+$', text):
            return "H1"
        
        # Title Case
        if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$', text):
            return "H2"
        
        return "H3"
    
    def _determine_level_by_content(self, text: str) -> str:
        """Determine heading level based on content."""
        text_lower = text.lower()
        
        # H1 level keywords
        h1_keywords = ['introduction', 'conclusion', 'abstract', 'summary', 'chapter']
        for keyword in h1_keywords:
            if keyword in text_lower:
                return "H1"
        
        # H2 level keywords
        h2_keywords = ['method', 'methodology', 'results', 'discussion', 'analysis', 'background']
        for keyword in h2_keywords:
            if keyword in text_lower:
                return "H2"
        
        # H3 level keywords
        h3_keywords = ['overview', 'review', 'related work', 'literature review']
        for keyword in h3_keywords:
            if keyword in text_lower:
                return "H3"
        
        return "H3"
    
    def _deduplicate_headings(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate headings based on text similarity."""
        unique_headings = []
        seen_texts = set()
        
        for heading in headings:
            text = heading["text"].lower().strip()
            if text not in seen_texts:
                seen_texts.add(text)
                unique_headings.append(heading)
        
        return unique_headings
    
    def _sort_headings(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort headings by page number and position."""
        # Sort by page number first
        headings.sort(key=lambda x: x.get("page", 1))
        
        # Within each page, sort by line number if available
        for i in range(len(headings) - 1):
            if (headings[i].get("page", 1) == headings[i + 1].get("page", 1) and
                "line_number" in headings[i] and "line_number" in headings[i + 1]):
                if headings[i]["line_number"] > headings[i + 1]["line_number"]:
                    headings[i], headings[i + 1] = headings[i + 1], headings[i]
        
        return headings 