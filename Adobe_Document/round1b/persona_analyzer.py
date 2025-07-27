import re
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import clean_text, segment_text_by_sections, rank_sections_by_relevance

class PersonaAnalyzer:
    """Analyze documents based on persona and job requirements."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        # Persona-specific keyword mappings
        self.persona_keywords = {
            'researcher': [
                'methodology', 'analysis', 'results', 'conclusion', 'hypothesis',
                'experiment', 'data', 'statistical', 'correlation', 'significance',
                'literature review', 'related work', 'background', 'framework'
            ],
            'student': [
                'introduction', 'overview', 'concept', 'definition', 'example',
                'explanation', 'summary', 'key points', 'important', 'fundamental',
                'basic', 'principles', 'theory', 'practice'
            ],
            'analyst': [
                'trend', 'analysis', 'performance', 'metrics', 'data', 'statistics',
                'comparison', 'benchmark', 'evaluation', 'assessment', 'insights',
                'findings', 'recommendations', 'strategy'
            ],
            'manager': [
                'executive summary', 'overview', 'strategy', 'planning', 'goals',
                'objectives', 'implementation', 'timeline', 'budget', 'resources',
                'team', 'leadership', 'decision', 'action'
            ],
            'journalist': [
                'news', 'story', 'event', 'interview', 'quote', 'source',
                'background', 'context', 'timeline', 'impact', 'reaction',
                'statement', 'announcement', 'development'
            ]
        }
        
        # Job-specific keyword mappings
        self.job_keywords = {
            'literature review': [
                'previous work', 'related research', 'background', 'methodology',
                'findings', 'conclusion', 'limitations', 'future work'
            ],
            'exam preparation': [
                'key concepts', 'important', 'definition', 'example', 'practice',
                'review', 'summary', 'main points', 'fundamental'
            ],
            'market analysis': [
                'market', 'trend', 'competition', 'revenue', 'growth', 'strategy',
                'performance', 'analysis', 'forecast', 'opportunity'
            ],
            'financial analysis': [
                'financial', 'revenue', 'profit', 'loss', 'investment', 'budget',
                'expense', 'income', 'balance', 'cash flow'
            ],
            'technical review': [
                'technology', 'system', 'architecture', 'implementation', 'design',
                'performance', 'efficiency', 'optimization', 'scalability'
            ]
        }
    
    def analyze_documents(self, documents: List[Dict[str, Any]], 
                         persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """Analyze documents based on persona and job requirements."""
        
        # Extract persona and job keywords
        persona_keywords = self._extract_persona_keywords(persona)
        job_keywords = self._extract_job_keywords(job_to_be_done)
        
        # Process all documents
        all_sections = []
        document_info = []
        
        for doc in documents:
            doc_name = doc.get("file_path", "unknown")
            doc_text = doc.get("text", "")
            
            if not doc_text:
                continue
            
            # Segment document into sections
            sections = segment_text_by_sections(doc_text)
            
            # Add document info to sections
            for section in sections:
                section["document"] = doc_name
                section["page_number"] = 1  # Default, will be refined
            
            all_sections.extend(sections)
            document_info.append({
                "document": doc_name,
                "title": doc.get("title", "Untitled"),
                "sections_count": len(sections)
            })
        
        # Rank sections by relevance
        ranked_sections = rank_sections_by_relevance(
            all_sections, persona_keywords, job_keywords
        )
        
        # Extract top relevant sections
        top_sections = ranked_sections[:10]  # Top 10 sections
        
        # Generate sub-section analysis
        sub_sections = self._generate_sub_section_analysis(
            top_sections, persona_keywords, job_keywords
        )
        
        # Prepare output
        output = {
            "metadata": {
                "input_documents": [doc.get("file_path", "unknown") for doc in documents],
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "processing_timestamp": self._get_timestamp()
            },
            "extracted_sections": [
                {
                    "document": section["document"],
                    "page_number": section["page_number"],
                    "section_title": section["title"],
                    "importance_rank": section["importance_rank"]
                }
                for section in top_sections
            ],
            "sub_section_analysis": sub_sections
        }
        
        return output
    
    def _extract_persona_keywords(self, persona: str) -> List[str]:
        """Extract keywords based on persona."""
        persona_lower = persona.lower()
        
        # Check for exact matches
        for key, keywords in self.persona_keywords.items():
            if key in persona_lower:
                return keywords
        
        # Check for partial matches
        for key, keywords in self.persona_keywords.items():
            if any(word in persona_lower for word in key.split()):
                return keywords
        
        # Default keywords for unknown persona
        return [
            'important', 'key', 'main', 'primary', 'essential', 'critical',
            'analysis', 'review', 'summary', 'overview', 'background'
        ]
    
    def _extract_job_keywords(self, job_description: str) -> List[str]:
        """Extract keywords based on job description."""
        job_lower = job_description.lower()
        
        # Check for exact matches
        for key, keywords in self.job_keywords.items():
            if key in job_lower:
                return keywords
        
        # Check for partial matches
        for key, keywords in self.job_keywords.items():
            if any(word in job_lower for word in key.split()):
                return keywords
        
        # Extract keywords from job description
        words = re.findall(r'\b\w+\b', job_lower)
        return [word for word in words if len(word) > 3][:10]
    
    def _generate_sub_section_analysis(self, sections: List[Dict[str, Any]], 
                                     persona_keywords: List[str], 
                                     job_keywords: List[str]) -> List[Dict[str, Any]]:
        """Generate detailed sub-section analysis."""
        sub_sections = []
        
        for section in sections:
            content = " ".join(section["content"])
            
            # Split content into paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            for i, paragraph in enumerate(paragraphs[:3]):  # Top 3 paragraphs
                # Calculate relevance score for this paragraph
                paragraph_lower = paragraph.lower()
                
                persona_score = sum(1 for keyword in persona_keywords 
                                  if keyword.lower() in paragraph_lower)
                job_score = sum(1 for keyword in job_keywords 
                              if keyword.lower() in paragraph_lower)
                
                total_score = persona_score + job_score
                max_possible = len(persona_keywords) + len(job_keywords)
                relevance_score = total_score / max_possible if max_possible > 0 else 0
                
                # Only include relevant paragraphs
                if relevance_score > 0.1:  # Threshold for relevance
                    sub_sections.append({
                        "document": section["document"],
                        "page_number": section["page_number"],
                        "refined_text": paragraph[:500],  # Limit length
                        "importance_rank": relevance_score
                    })
        
        # Sort by importance rank
        sub_sections.sort(key=lambda x: x["importance_rank"], reverse=True)
        
        return sub_sections[:20]  # Top 20 sub-sections
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def calculate_document_similarity(self, doc1_text: str, doc2_text: str) -> float:
        """Calculate similarity between two documents using TF-IDF."""
        if not doc1_text or not doc2_text:
            return 0.0
        
        try:
            # Create TF-IDF vectors
            texts = [doc1_text, doc2_text]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except Exception:
            # Fallback to simple word overlap
            words1 = set(doc1_text.lower().split())
            words2 = set(doc2_text.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
    
    def find_related_sections(self, target_section: str, 
                            all_sections: List[Dict[str, Any]], 
                            threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Find sections related to a target section."""
        related = []
        
        for section in all_sections:
            section_text = " ".join(section["content"])
            similarity = self.calculate_document_similarity(target_section, section_text)
            
            if similarity >= threshold:
                related.append({
                    **section,
                    "similarity_score": similarity
                })
        
        # Sort by similarity score
        related.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return related 