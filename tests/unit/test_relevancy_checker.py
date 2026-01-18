"""Unit tests for Relevancy Checker"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from unittest.mock import Mock
from src.agents.relevancy_checker import RelevancyChecker

def test_relevant_plan():
    """Matching plan should score high"""
    mock_llm = Mock()
    # Use lowercase 'reasoning:' to match the split
    mock_llm.invoke.return_value = Mock(content='Relevancy Score: 0.9\nIs Relevant: Yes\nreasoning: Plan covers all query aspects')
    
    checker = RelevancyChecker(mock_llm)
    result = checker.check_relevancy(
        original_query="climate change effects",
        transformed_query="What are the environmental and economic effects of climate change?",
        plan={"research_angles": ["environmental impact", "economic impact"], "search_queries": [], "focus_areas": []}
    )
    
    assert result["is_relevant"] == True
    assert result["relevancy_score"] >= 0.6
    print("PASSED: Relevant plan detected")

def test_irrelevant_plan():
    """Mismatched plan should score low"""
    mock_llm = Mock()
    # Use lowercase and include "not relevant" to trigger is_relevant=False
    mock_llm.invoke.return_value = Mock(content='Relevancy Score: 0.2\nIs Relevant: No\nThe plan is not relevant\nreasoning: Plan does not address query')
    
    checker = RelevancyChecker(mock_llm)
    result = checker.check_relevancy(
        original_query="quantum computing basics",
        transformed_query="What are the fundamentals of quantum computing?",
        plan={"research_angles": ["cooking recipes"], "search_queries": [], "focus_areas": []}
    )
    
    assert result["is_relevant"] == False
    assert result["relevancy_score"] < 0.6
    print("PASSED: Irrelevant plan detected")

if __name__ == "__main__":
    test_relevant_plan()
    test_irrelevant_plan()
    print("\nAll Relevancy Checker tests passed")