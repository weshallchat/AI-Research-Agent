"""
Research Orchestrator:
- One orchestrator that creates action plan
- Sequential execution of actions
- Fallback strategies for failures
- Relevancy checking before proceeding
"""

from typing import Dict, List, Optional
import json
from src.agents.planner import PlanningAgent
from src.agents.searcher import SearchAgent
from src.agents.extractor import EvidenceExtractor
from src.agents.synthesizer import SynthesisAgent
from src.agents.relevancy_checker import RelevancyChecker
from src.agents.direct_answer_generator import DirectAnswerGenerator
from src.utils.helpers import setup_llm, setup_lightweight_llm
from src.agents.query_transformer import QueryTransformer
from datetime import datetime


class ResearchOrchestrator:
    def __init__(self):
        """Initialize orchestrator with all agents"""
        self.llm = setup_llm()
        self.lightweight_llm = setup_lightweight_llm()
        
        # Query transformer (uses lightweight LLM)
        self.transformer = QueryTransformer(self.lightweight_llm)
        self.relevancy_checker = RelevancyChecker(self.lightweight_llm)
        
        # Other agents (use main LLM)
        self.planner = PlanningAgent(self.llm)
        self.direct_answer_generator = DirectAnswerGenerator(self.llm)
        self.searcher = SearchAgent()
        self.extractor = EvidenceExtractor(self.llm)
        self.synthesizer = SynthesisAgent(self.llm)
        
        # Track state
        self.state = {
            'original_query': None,
            'transformed_query': None,
            'plan': None,
            'relevancy_check': None,
            'is_llm_generated': False,
            'search_results': [],
            'evidence': [],
            'report': None
        }
    
    def conduct_research(self, prompt: str) -> str:
        """
        Main orchestration flow:
        0. Transform query
        1. Create action plan
        2. Check relevancy of plan
        3a. If relevant: Execute searches, extract, synthesize
        3b. If not relevant: Generate direct LLM answer
        """
        
        if not prompt or not prompt.strip():
            print("=" * 60)
            print("ERROR: Empty query provided")
            print("=" * 60)
            return self._empty_query_response()

        print("=" * 60)
        print("Step 0: Transforming query...")
        print("=" * 60)
        self.state['original_query'] = prompt
        transform_result = self.transformer.transform(prompt)
        self.state['transformed_query'] = transform_result
        
        research_query = transform_result['transformed']
        
        if transform_result['was_transformed']:
            print(f"Query transformed: {research_query[:80]}...")
        else:
            print(f"Query already well-formed")
        
        print("\n" + "=" * 60)
        print("Step 1: Creating research plan...")
        print("=" * 60)
        self.state['plan'] = self._create_plan(research_query)
        print(f"Plan created with {len(self.state['plan'].get('research_angles', []))} angles")
        
        print("\n" + "=" * 60)
        print("Step 2: Checking plan relevancy...")
        print("=" * 60)
        self.state['relevancy_check'] = self._check_relevancy(prompt, research_query)
        
        relevancy_score = self.state['relevancy_check']['relevancy_score']
        is_relevant = self.state['relevancy_check']['is_relevant']
        
        print(f"Relevancy Score: {relevancy_score:.2f}/1.0")
        print(f"Reasoning: {self.state['relevancy_check']['reasoning'][:200]}...")
        
        if not is_relevant:
            print("\n")
            print("!" * 60)
            print("!!! WARNING: GENERATING LLM-ONLY RESPONSE !!!")
            print("!" * 60)
            print("Research plan is NOT sufficiently relevant to the query")
            print("The response will be LLM-generated (no external sources)")
            print("!" * 60)
            print("\n")
            
            self.state['is_llm_generated'] = True
            self.state['report'] = self._generate_direct_answer(
                prompt, 
                research_query,
                self.state['relevancy_check']['reasoning']
            )
            return self.state['report']
        
        print(f"Plan is relevant (score: {relevancy_score:.2f})")
        print("Proceeding with research pipeline...")
        
        print("\n" + "=" * 60)
        print("Step 3: Executing searches...")
        print("=" * 60)
        self.state['search_results'] = self._execute_searches()
        
        print("\n" + "=" * 60)
        print("Step 4: Extracting evidence...")
        print("=" * 60)
        self.state['evidence'] = self._extract_evidence(research_query)
        
        print("\n" + "=" * 60)
        print("Step 5: Synthesizing report...")
        print("=" * 60)
        self.state['report'] = self._synthesize_report(research_query)
        
        return self.state['report']
    
    def _empty_query_response(self) -> str:
        """Return error response for empty queries"""
        return f"""---
Research Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Topic: (Empty Query)
Sources Analyzed: 0
---

# Error: No Query Provided

Please provide a research query to proceed.

**Examples of good queries:**
- "What are the benefits and risks of synthetic data in AI?"
- "How has machine learning evolved in healthcare?"
- "Compare renewable energy sources for industrial use"

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _check_relevancy(self, original_query: str, transformed_query: str) -> Dict:
        """Check if research plan is relevant to queries"""
        return self.relevancy_checker.check_relevancy(
            original_query=original_query,
            transformed_query=transformed_query,
            plan=self.state['plan']
        )
    
    def _generate_direct_answer(self, original_query: str, transformed_query: str, reasoning: str) -> str:
        """Generate direct LLM answer when plan is not relevant"""
        return self.direct_answer_generator.generate_answer(
            original_query=original_query,
            transformed_query=transformed_query,
            relevancy_reasoning=reasoning
        )
    
    def _create_plan(self, research_query: str) -> Dict:
        """Create research plan with fallback"""
        try:
            return self.planner.create_plan(research_query)
        except Exception as e:
            print(f"Planning failed, using fallback: {e}")
            return {
                'research_angles': ['general overview', 'risks', 'benefits'],
                'search_queries': [
                    research_query,
                    f"{research_query} academic research",
                    f"{research_query} industry applications"
                ],
                'focus_areas': ['data quality', 'bias', 'evaluation']
            }
    
    def _execute_searches(self) -> List[Dict]:
        """Execute searches with fallback strategies"""
        all_results = []
        queries = self.state['plan'].get('search_queries', [])
        
        for query in queries:
            try:
                results = self.searcher.search(query)
                all_results.extend(results)
                print(f"✓ Found {len(results)} results for: {query[:50]}...")
            except Exception as e:
                print(f"Search failed, trying fallback: {e}")
                try:
                    fallback_results = self.searcher.fallback_search(query)
                    all_results.extend(fallback_results)
                except:
                    print(f"Fallback also failed for: {query[:50]}...")
                    continue
        
        return all_results
    
    def _extract_evidence(self, research_query: str) -> List[Dict]:
        """Extract evidence from search results"""
        evidence_list = []
        
        for result in self.state['search_results']:
            try:
                evidence = self.extractor.extract(
                    content=result,
                    context=research_query,
                    focus_areas=self.state['plan'].get('focus_areas', [])
                )
                if evidence:
                    evidence_list.append(evidence)
            except Exception as e:
                print(f"Evidence extraction failed for one source: {e}")
                continue
        
        return evidence_list
    
    def _synthesize_report(self, research_query: str) -> str:
        """Synthesize final report from evidence"""
        try:
            return self.synthesizer.create_report(
                prompt=research_query,
                plan=self.state['plan'],
                evidence=self.state['evidence']
            )
        except Exception as e:
            print(f"Synthesis failed, using fallback: {e}")
            return self._fallback_report(research_query)
    
    def _fallback_report(self, research_query: str) -> str:
        """Simple fallback report if synthesis fails"""
        report = f"# Research Report\n\n"
        report += f"## Topic\n{research_query}\n\n"
        report += f"## Summary\nResearch conducted on {len(self.state['search_results'])} sources.\n\n"
        report += f"## Key Findings\n"
        
        for i, evidence in enumerate(self.state['evidence'][:5], 1):
            report += f"\n### Finding {i}\n"
            report += f"- Source: {evidence.get('source', 'Unknown')}\n"
            report += f"- Content: {evidence.get('content', 'No content')[:200]}...\n"
        
        return report