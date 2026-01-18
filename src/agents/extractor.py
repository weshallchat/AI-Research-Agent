"""
Evidence Extractor - Extracts relevant evidence from search results
"""

from typing import Dict, List, Optional
from src.prompts.templates import EXTRACTION_PROMPT

class EvidenceExtractor:
    def __init__(self, llm):
        self.llm = llm
    
    def extract(self, content: Dict, context: str, focus_areas: List[str]) -> Optional[Dict]:
        """
        Extract evidence from a search result
        Focus on claims, data, and relevance to research topic
        """
        
        if not content.get('snippet'):
            return None
        
        prompt = EXTRACTION_PROMPT.format(
            content=content['snippet'],
            title=content.get('title', ''),
            context=context,
            focus_areas=', '.join(focus_areas)
        )
        
        try:
            response = self.llm.invoke(prompt)
            
            return {
                'source': content.get('url', 'Unknown'),
                'title': content.get('title', 'Untitled'),
                'evidence': response.content,
                'relevance': self._calculate_relevance(response.content, focus_areas),
                'content': content['snippet']
            }
            
        except Exception as e:
            print(f"Extraction error: {e}")
            # Return raw content as fallback
            return {
                'source': content.get('url', 'Unknown'),
                'title': content.get('title', 'Untitled'),
                'evidence': content['snippet'],
                'relevance': 0.5,
                'content': content['snippet']
            }
    
    def _calculate_relevance(self, evidence: str, focus_areas: List[str]) -> float:
        """
        Simple relevance scoring based on focus area mentions
        """
        if not focus_areas:
            return 0.5
        
        evidence_lower = evidence.lower()
        matches = sum(1 for area in focus_areas if area.lower() in evidence_lower)
        
        return min(1.0, matches / len(focus_areas) + 0.3)