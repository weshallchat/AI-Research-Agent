"""Run all tests"""
import subprocess
import sys

test_files = [
    "tests/unit/test_query_transformer.py",
    "tests/unit/test_relevancy_checker.py",
    "tests/unit/test_visual_generator.py",
    "tests/integration/test_search_extract_pipeline.py",
    # Uncomment for full E2E (uses real API calls):
    # "tests/e2e/test_full_research.py",
    # "tests/edge_cases/test_edge_cases.py",
]

def main():
    print("=" * 60)
    print("AI Research Agent - Test Suite")
    print("=" * 60)
    
    failed = []
    
    for test_file in test_files:
        print(f"\n▶ Running {test_file}...")
        result = subprocess.run([sys.executable, test_file])
        if result.returncode != 0:
            failed.append(test_file)
    
    print("\n" + "=" * 60)
    if failed:
        print(f"FAILED: {len(failed)} test file(s)")
        for f in failed:
            print(f"   - {f}")
    else:
        print("ALL TESTS PASSED")
    print("=" * 60)

if __name__ == "__main__":
    main()