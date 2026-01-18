"""Integration test: Searcher -> Extractor pipeline"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from unittest.mock import Mock
from src.agents.extractor import EvidenceExtractor  # <-- Fixed class name

def test_search_to_extract():
    """Searcher output should feed into Extractor"""
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content='Key finding: AI is transforming healthcare through improved diagnostics.')
    
    # Simulated search results
    search_results = [
        {"title": "AI Overview", "url": "https://example.com/ai", "snippet": "AI is transforming industries..."},
        {"title": "ML Basics", "url": "https://example.com/ml", "snippet": "Machine learning enables..."}
    ]
    
    extractor = EvidenceExtractor(mock_llm)
    
    for result in search_results:
        extracted = extractor.extract(result, "AI applications", ["healthcare", "diagnostics"])
        assert "evidence" in extracted
        assert "source" in extracted
    
    print("PASSED: Search -> Extract pipeline works")

if __name__ == "__main__":
    test_search_to_extract()
    print("\n All Integration tests passed")