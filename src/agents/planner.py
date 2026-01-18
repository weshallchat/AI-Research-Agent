"""
Planning Agent - Creates research plan from prompt
"""

import json
from typing import Dict, List
from src.prompts.templates import PLANNING_PROMPT

class PlanningAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_plan(self, prompt: str) -> Dict:
        """
        Create structured research plan
        Returns angles, queries, and focus areas
        """
        
        # Use the planning prompt template
        formatted_prompt = PLANNING_PROMPT.format(research_topic=prompt)
        
        try:
            response = self.llm.invoke(formatted_prompt)
            plan = self._parse_plan(response.content)
            
            # Ensure we have the required structure
            if not all(k in plan for k in ['research_angles', 'search_queries', 'focus_areas']):
                raise ValueError("Incomplete plan generated")
            
            return plan
            
        except Exception as e:
            print(f"Planning error: {e}")
            # Return a sensible default plan
            return self._default_plan(prompt)
    
    def _parse_plan(self, response: str) -> Dict:
        """Parse LLM response into structured plan"""
        try:
            # Try to extract JSON if present
            if '{' in response and '}' in response:
                start = response.index('{')
                end = response.rindex('}') + 1
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: Create plan from text
        lines = response.split('\n')
        plan = {
            'research_angles': [],
            'search_queries': [],
            'focus_areas': []
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if 'angle' in line.lower() or 'perspective' in line.lower():
                current_section = 'research_angles'
            elif 'search' in line.lower() or 'quer' in line.lower():
                current_section = 'search_queries'
            elif 'focus' in line.lower() or 'area' in line.lower():
                current_section = 'focus_areas'
            elif line.startswith('-') or line.startswith('•'):
                content = line.lstrip('-•').strip()
                if current_section and content:
                    plan[current_section].append(content)
        
        return plan
    
    def _default_plan(self, prompt: str) -> Dict:
        """Generate default plan if LLM fails"""
        keywords = prompt.lower().split()
        
        return {
            'research_angles': [
                'Academic perspective',
                'Industry applications',
                'Technical challenges',
                'Future implications'
            ],
            'search_queries': [
                prompt,
                f"{prompt} research papers",
                f"{prompt} case studies",
                f"{prompt} best practices",
                f"{prompt} challenges risks"
            ],
            'focus_areas': [
                word for word in keywords 
                if len(word) > 4 and word not in ['what', 'where', 'when', 'which']
            ][:5]
        }