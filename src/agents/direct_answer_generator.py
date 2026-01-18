"""
Direct Answer Generator - Generates LLM-based answers when research plan is not relevant
"""

from typing import Dict
from src.prompts.templates import DIRECT_ANSWER_PROMPT
from datetime import datetime

class DirectAnswerGenerator:
    def __init__(self, llm):
        """Initialize with LLM for direct answer generation"""
        self.llm = llm
    
    def generate_answer(self, original_query: str, transformed_query: str, relevancy_reasoning: str) -> str:
        """
        Generate a direct LLM answer when research plan is not relevant
        
        Returns:
            Formatted markdown report with LLM-generated disclaimer
        """
        prompt = DIRECT_ANSWER_PROMPT.format(
            original_query=original_query,
            transformed_query=transformed_query,
            relevancy_issue=relevancy_reasoning
        )
        
        try:
            response = self.llm.invoke(prompt)
            answer = response.content
            
            # Wrap in report format with disclaimer
            report = self._format_as_report(original_query, answer)
            return report
        except Exception as e:
            print(f"Direct answer generation failed: {e}")
            return self._fallback_answer(original_query)
    
    def _format_as_report(self, query: str, answer: str) -> str:
        """Format LLM answer as a research report with disclaimer"""
        report = f"""---
Research Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Topic: {query}
Sources Analyzed: 0
IMPORTANT: This report is LLM-generated (not based on external research)
---

# Research Report: {query}

## Disclaimer

**This report is generated directly by an AI language model and is not based on external research sources.**

The research plan generated for this query was determined to be insufficiently relevant to the original question. As a result, this response is based solely on the AI model's training data and may not reflect the most current information or external sources.

---

## Answer

{answer}

---

## Note

This response was generated because the automated research planning process could not identify sufficiently relevant search strategies for your query. For more accurate and up-to-date information, please consider:
- Refining your query to be more specific
- Conducting manual research using academic databases
- Consulting domain experts

---

*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return report
    
    def _fallback_answer(self, query: str) -> str:
        """Fallback answer if generation fails"""
        return f"""# Research Report: {query}

## Disclaimer

**This report is LLM-generated (not based on external research)**

## Answer

I apologize, but I was unable to generate a comprehensive answer for your query. The research planning process encountered issues, and direct answer generation also failed.

Please try:
- Rephrasing your query
- Being more specific about what you're looking for
- Breaking down complex questions into smaller parts

*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""