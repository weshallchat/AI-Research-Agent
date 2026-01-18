"""End-to-end tests for full research pipeline"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from src.orchestrator import ResearchOrchestrator

def test_simple_research_query():
    """Simple factual query should produce valid report"""
    orchestrator = ResearchOrchestrator()
    report = orchestrator.conduct_research("What is machine learning?")
    
    assert len(report) > 500
    assert "machine learning" in report.lower() or "ml" in report.lower()
    assert "##" in report  # Has headers
    print("PASSED: Simple query produces report")

def test_complex_research_query():
    """Complex analytical query should produce detailed report"""
    orchestrator = ResearchOrchestrator()
    report = orchestrator.conduct_research(
        "What are the ethical implications of using AI in criminal justice systems?"
    )
    
    assert len(report) > 1000
    assert "ethical" in report.lower() or "ethics" in report.lower()
    assert "References" in report or "Sources" in report
    print("PASSED: Complex query produces detailed report")

def test_report_has_visuals():
    """Report should include visual references"""
    orchestrator = ResearchOrchestrator()
    report = orchestrator.conduct_research("Benefits of renewable energy")
    
    assert ".png" in report or "Evidence" in report
    print("PASSED: Report includes visuals or evidence section")

if __name__ == "__main__":
    print("Running E2E tests (these make real API calls)...\n")
    test_simple_research_query()
    test_complex_research_query()
    test_report_has_visuals()
    print("\nAll E2E tests passed")