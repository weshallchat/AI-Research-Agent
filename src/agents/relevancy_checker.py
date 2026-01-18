"""
Relevancy Checker - Validates that the research plan aligns with the original query
"""

from typing import Dict
from src.prompts.templates import RELEVANCY_CHECK_PROMPT

class RelevancyChecker:
    def __init__(self, llm):
        """Initialize with LLM for relevancy analysis"""
        self.llm = llm
    
    def check_relevancy(self, original_query: str, transformed_query: str, plan: Dict) -> Dict:
        """
        Check if the research plan is relevant to the original and transformed queries
        
        Returns:
            Dict with 'is_relevant' (bool), 'relevancy_score' (float), 'reasoning' (str)
        """
        prompt = RELEVANCY_CHECK_PROMPT.format(
            original_query=original_query,
            transformed_query=transformed_query,
            research_angles=', '.join(plan.get('research_angles', [])),
            search_queries='\n'.join(plan.get('search_queries', [])),
            focus_areas=', '.join(plan.get('focus_areas', []))
        )
        
        try:
            response = self.llm.invoke(prompt)
            result = self._parse_response(response.content)
            return result
        except Exception as e:
            print(f"Relevancy check failed: {e}")
            # Fallback: assume relevant if we can't check
            return {
                'is_relevant': True,
                'relevancy_score': 0.7,
                'reasoning': 'Relevancy check failed, proceeding with caution'
            }
    
    def _parse_response(self, response: str) -> Dict:
        """Parse LLM response into structured relevancy check result"""
        response_lower = response.lower()
        
        # Extract relevancy score (0.0 to 1.0)
        relevancy_score = 0.5  # Default
        is_relevant = True  # Default
        
        # Look for score indicators
        if 'score:' in response_lower:
            try:
                score_line = [line for line in response.split('\n') if 'score:' in line.lower()][0]
                score_str = score_line.split(':')[1].strip().split()[0]
                relevancy_score = float(score_str)
            except:
                pass
        
        # Look for relevancy decision
        if any(word in response_lower for word in ['not relevant', 'irrelevant', 'unrelated', 'off-topic']):
            is_relevant = False
        
        if any(word in response_lower for word in ['relevant', 'aligned', 'appropriate', 'matches']):
            is_relevant = True
        
        # Extract reasoning
        reasoning = response
        if 'reasoning:' in response_lower:
            reasoning = response.split('reasoning:')[1].strip()
        elif 'reason:' in response_lower:
            reasoning = response.split('reason:')[1].strip()
        
        # Set threshold (score < 0.6 means not relevant)
        if relevancy_score < 0.6:
            is_relevant = False
        
        return {
            'is_relevant': is_relevant,
            'relevancy_score': relevancy_score,
            'reasoning': reasoning[:500]  # Limit reasoning length
        }