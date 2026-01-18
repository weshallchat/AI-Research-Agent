"""Unit tests for Visual Generator"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.visual_generator import VisualGenerator

def test_generates_png_files():
    """Should create PNG files"""
    generator = VisualGenerator(output_dir="outputs/test")
    
    plan = {"research_angles": ["angle 1", "angle 2", "angle 3"]}
    evidence = [
        {"relevance": 0.9, "source": "https://example.com/a"},
        {"relevance": 0.6, "source": "https://test.org/b"},
        {"relevance": 0.3, "source": "https://example.com/c"},
    ]
    
    result = generator.generate_visual_summary(plan, evidence)
    
    assert ".png" in result
    print("PASSED: PNG references generated")

def test_handles_empty_evidence():
    """Should handle empty evidence gracefully"""
    generator = VisualGenerator(output_dir="outputs/test")
    
    result = generator.generate_visual_summary({}, [])
    
    assert result is not None  # Should not crash
    print("PASSED: Empty evidence handled")

if __name__ == "__main__":
    test_generates_png_files()
    test_handles_empty_evidence()
    print("\nAll Visual Generator tests passed")