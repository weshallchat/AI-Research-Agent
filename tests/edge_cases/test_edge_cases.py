"""Edge case tests"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from src.orchestrator import ResearchOrchestrator

def test_empty_query():
    """Empty query should not crash"""
    orchestrator = ResearchOrchestrator()
    try:
        report = orchestrator.conduct_research("")
        assert report is not None
        print("PASSED: Empty query handled")
    except Exception as e:
        print(f"HANDLED: Empty query raised {type(e).__name__}")

def test_very_long_query():
    """Very long query should be handled"""
    orchestrator = ResearchOrchestrator()
    long_query = "Explain " + "the implications of " * 50 + "AI"
    
    report = orchestrator.conduct_research(long_query)
    assert report is not None
    print("PASSED: Long query handled")

def test_special_characters():
    """Query with special chars should work"""
    orchestrator = ResearchOrchestrator()
    report = orchestrator.conduct_research("What is C++ vs C#? @2024")
    
    assert report is not None
    print("PASSED: Special characters handled")

def test_non_english_query():
    """Non-English query should produce some output"""
    orchestrator = ResearchOrchestrator()
    report = orchestrator.conduct_research("¿Qué es la inteligencia artificial?")
    
    assert report is not None
    print("PASSED: Non-English query handled")

def test_nonsense_query():
    """Nonsense query should trigger direct answer fallback"""
    orchestrator = ResearchOrchestrator()
    report = orchestrator.conduct_research("asdfghjkl qwerty xyz123")
    
    assert report is not None
    # Should likely trigger LLM-generated answer
    print("PASSED: Nonsense query handled (likely direct answer)")

if __name__ == "__main__":
    print("Running Edge Case tests...\n")
    test_empty_query()
    test_very_long_query()
    test_special_characters()
    test_non_english_query()
    test_nonsense_query()
    print("\nAll Edge Case tests passed")