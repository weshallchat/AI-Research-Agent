"""
Query Transformer - Transforms raw user queries into research-optimized queries
Uses a lightweight LLM for fast, cost-effective transformation
"""

from typing import Dict
from src.prompts.templates import QUERY_TRANSFORM_PROMPT

class QueryTransformer:
    def __init__(self, llm):
        """
        Initialize with a lightweight LLM
        Can use a different (cheaper) model than the main agents
        """
        self.llm = llm
    
    def transform(self, raw_query: str) -> Dict[str, str]:
        """
        Transform a raw user query into a research-optimized query
        
        Returns:
            Dict with 'original', 'transformed', and 'research_focus'
        """
        # Skip transformation for already well-formed queries
        if self._is_well_formed(raw_query):
            return {
                'original': raw_query,
                'transformed': raw_query,
                'research_focus': self._extract_focus(raw_query),
                'was_transformed': False
            }
        
        prompt = QUERY_TRANSFORM_PROMPT.format(user_query=raw_query)
        
        try:
            response = self.llm.invoke(prompt)
            result = self._parse_response(response.content, raw_query)
            result['was_transformed'] = True
            return result
        except Exception as e:
            print(f"Query transformation failed: {e}")
            # Fallback: return cleaned original
            return {
                'original': raw_query,
                'transformed': self._basic_cleanup(raw_query),
                'research_focus': 'general analysis',
                'was_transformed': False
            }
    
    def _is_well_formed(self, query: str) -> bool:
        """Check if query is already research-oriented"""
        research_indicators = [
            'analyze', 'evaluate', 'compare', 'examine',
            'investigate', 'research', 'study', 'assess',
            'implications', 'impact', 'effects', 'benefits',
            'risks', 'challenges', 'advantages', 'disadvantages'
        ]
        query_lower = query.lower()
        
        # Check for research-oriented words and reasonable length
        has_research_words = any(word in query_lower for word in research_indicators)
        has_good_length = 100 < len(query) < 500
        has_specificity = len(query.split()) >= 5
        
        return has_research_words and has_good_length and has_specificity
    
    def _parse_response(self, response: str, original: str) -> Dict:
        """Parse LLM response into structured output"""
        lines = response.strip().split('\n')
        
        transformed = original
        focus = "general analysis"
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith('transformed:') or line.lower().startswith('query:'):
                transformed = line.split(':', 1)[1].strip().strip('"\'')
            elif line.lower().startswith('focus:') or line.lower().startswith('research focus:'):
                focus = line.split(':', 1)[1].strip()
            # If response is just a single improved query
            elif len(lines) == 1 and len(line) > 20:
                transformed = line.strip('"\'')
        
        return {
            'original': original,
            'transformed': transformed if transformed else original,
            'research_focus': focus
        }
    
    def _basic_cleanup(self, query: str) -> str:
        """Basic cleanup for fallback"""
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        # Ensure it ends properly
        if not query.endswith(('?', '.', '!')):
            query += '?'
        
        # Add research framing if too short
        if len(query.split()) < 5:
            query = f"What are the key aspects and implications of {query}"
        
        return query
    
    def _extract_focus(self, query: str) -> str:
        """Extract research focus from well-formed query"""
        focus_keywords = {
            'risk': 'risk analysis',
            'benefit': 'benefits assessment', 
            'impact': 'impact analysis',
            'compare': 'comparative analysis',
            'future': 'future implications',
            'ethical': 'ethical considerations',
            'technical': 'technical analysis',
            'economic': 'economic impact'
        }
        
        query_lower = query.lower()
        for keyword, focus in focus_keywords.items():
            if keyword in query_lower:
                return focus
        
        return 'comprehensive analysis'