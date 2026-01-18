"""Unit tests for Query Transformer"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from unittest.mock import Mock
from src.agents.query_transformer import QueryTransformer

def test_transform_vague_query():
    """Vague query should be expanded"""
    mock_llm = Mock()
    # Return format that _parse_response expects
    mock_llm.invoke.return_value = Mock(content='Transformed: What are the applications, benefits, and limitations of AI in healthcare?\nFocus: healthcare AI analysis')
    
    transformer = QueryTransformer(mock_llm)
    result = transformer.transform("AI in healthcare")
    
    assert "transformed" in result  # <-- Fixed key name
    assert "original" in result
    print("PASSED: Vague query expanded")

def test_transform_good_query():
    """Good query should remain similar"""
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content='Transformed: What are the ethical implications of facial recognition?\nFocus: ethics')
    
    transformer = QueryTransformer(mock_llm)
    # Long query with research indicators triggers _is_well_formed = True
    result = transformer.transform("What are the ethical implications of facial recognition in law enforcement and its impact on civil liberties?")
    
    assert "transformed" in result
    assert result["was_transformed"] == False  # Well-formed = no transformation
    print("PASSED: Good query handled")

def test_transform_empty_query():
    """Empty query should return fallback"""
    mock_llm = Mock()
    mock_llm.invoke.side_effect = Exception("Empty")
    
    transformer = QueryTransformer(mock_llm)
    result = transformer.transform("")
    
    assert result is not None
    assert "transformed" in result
    print("PASSED: Empty query handled")

if __name__ == "__main__":
    test_transform_vague_query()
    test_transform_good_query()
    test_transform_empty_query()
    print("\nAll Query Transformer tests passed")