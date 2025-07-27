import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might interfere with processing
    text = re.sub(r'[^\w\s\-\.\,\;\:\!\?\(\)\[\]]', '', text)
    
    return text

def is_heading_candidate(text: str) -> bool:
    """Check if text looks like a heading."""
    if not text or len(text.strip()) < 2:
        return False
    
    text = text.strip()
    
    # Common heading patterns
    heading_patterns = [
        r'^[A-Z][A-Z\s]+$',  # ALL CAPS
        r'^\d+\.\s+[A-Z]',   # Numbered headings
        r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$',  # Title Case
        r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s*$',  # Title Case with trailing space
    ]
    
    for pattern in heading_patterns:
        if re.match(pattern, text):
            return True
    
    # Check for common heading words
    heading_words = [
        'introduction', 'conclusion', 'abstract', 'summary', 'background',
        'method', 'methodology', 'results', 'discussion', 'analysis',
        'overview', 'review', 'related work', 'literature review',
        'chapter', 'section', 'part', 'appendix', 'references'
    ]
    
    text_lower = text.lower()
    for word in heading_words:
        if word in text_lower:
            return True
    
    return False

def normalize_font_size(font_size: float) -> int:
    """Normalize font sizes into discrete categories."""
    if font_size >= 16:
        return 3  # H1
    elif font_size >= 14:
        return 2  # H2
    elif font_size >= 12:
        return 1  # H3
    else:
        return 0  # Body text

def get_heading_level(font_size: float, font_weight: str = None, text: str = None) -> str:
    """Determine heading level based on font properties and text content."""
    normalized_size = normalize_font_size(font_size)
    
    # Adjust based on font weight
    if font_weight and 'bold' in font_weight.lower():
        normalized_size += 1
    
    # Adjust based on text content
    if text and is_heading_candidate(text):
        normalized_size += 1
    
    # Map to heading levels
    if normalized_size >= 3:
        return "H1"
    elif normalized_size >= 2:
        return "H2"
    elif normalized_size >= 1:
        return "H3"
    else:
        return "BODY"

def save_json_output(data: Dict[str, Any], output_path: str) -> None:
    """Save data to JSON file with proper formatting."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()

def extract_title_from_text(text: str) -> str:
    """Extract document title from text."""
    if not text:
        return "Untitled Document"
    
    # Look for title in first few lines
    lines = text.split('\n')[:10]
    
    for line in lines:
        line = line.strip()
        if line and len(line) > 3 and len(line) < 200:
            # Check if it looks like a title
            if re.match(r'^[A-Z][A-Za-z\s\-\.,:;]+$', line):
                return line
    
    # Fallback: use first non-empty line
    for line in lines:
        line = line.strip()
        if line and len(line) > 3:
            return line[:100]  # Limit length
    
    return "Untitled Document"

def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings."""
    if not text1 or not text2:
        return 0.0
    
    # Simple word overlap similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

def segment_text_by_sections(text: str) -> List[Dict[str, Any]]:
    """Segment text into sections based on headings."""
    sections = []
    lines = text.split('\n')
    current_section = {"title": "", "content": [], "page": 1}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line looks like a heading
        if is_heading_candidate(line):
            # Save previous section if it has content
            if current_section["content"]:
                sections.append(current_section)
            
            # Start new section
            current_section = {
                "title": line,
                "content": [],
                "page": 1  # Default page, will be updated by caller
            }
        else:
            # Add to current section content
            current_section["content"].append(line)
    
    # Add final section
    if current_section["content"]:
        sections.append(current_section)
    
    return sections

def rank_sections_by_relevance(sections: List[Dict[str, Any]], 
                              persona_keywords: List[str], 
                              job_keywords: List[str]) -> List[Dict[str, Any]]:
    """Rank sections by relevance to persona and job requirements."""
    ranked_sections = []
    
    for section in sections:
        section_text = " ".join(section["content"])
        section_text_lower = section_text.lower()
        
        # Calculate relevance scores
        persona_score = sum(1 for keyword in persona_keywords 
                          if keyword.lower() in section_text_lower)
        job_score = sum(1 for keyword in job_keywords 
                       if keyword.lower() in section_text_lower)
        
        # Combined score
        total_score = persona_score + job_score
        
        # Normalize score (0-1 range)
        max_possible_score = len(persona_keywords) + len(job_keywords)
        normalized_score = total_score / max_possible_score if max_possible_score > 0 else 0
        
        ranked_sections.append({
            **section,
            "importance_rank": normalized_score
        })
    
    # Sort by importance rank (descending)
    ranked_sections.sort(key=lambda x: x["importance_rank"], reverse=True)
    
    return ranked_sections 