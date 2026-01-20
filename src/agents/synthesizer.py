
## 2. Update `src/agents/synthesizer.py` (COMPLETE FILE)

"""
Synthesis Agent - Creates final research report with visuals
"""

from typing import Dict, List
from datetime import datetime
from src.prompts.templates import SYNTHESIS_PROMPT
from src.agents.visual_generator import VisualGenerator

class SynthesisAgent:
    def __init__(self, llm):
        self.llm = llm
        self.visual_generator = VisualGenerator()
    
    def create_report(self, prompt: str, plan: Dict, evidence: List[Dict]) -> str:
        """
        Synthesize evidence into coherent research report with visuals
        """
        
        # Sort evidence by relevance
        sorted_evidence = sorted(
            evidence, 
            key=lambda x: x.get('relevance', 0), 
            reverse=True
        )
        
        # Prepare evidence summary for LLM
        evidence_text = self._format_evidence(sorted_evidence[:10])
        
        synthesis_prompt = SYNTHESIS_PROMPT.format(
            research_topic=prompt,
            research_angles=plan.get('research_angles', []),
            evidence=evidence_text,
            focus_areas=plan.get('focus_areas', [])
        )
        
        try:
            response = self.llm.invoke(synthesis_prompt)
            report = response.content
            
            # Insert visuals after executive summary
            report = self._insert_visuals(report, plan, sorted_evidence)
            
            # Add metadata and sources
            report = self._add_metadata(report, prompt, len(evidence))
            report = self._add_sources(report, sorted_evidence)
            
            return report
            
        except Exception as e:
            print(f"Synthesis error: {e}")
            return self._create_basic_report(prompt, plan, sorted_evidence)
    
    def _insert_visuals(self, report: str, plan: Dict, evidence: List[Dict]) -> str:
        """Insert visualizations into the report after Executive Summary"""
        visuals = self.visual_generator.generate_visual_summary(plan, evidence)
        
        if not visuals:
            return report
        
        # Try to insert after "## Executive Summary" section
        if "## Executive Summary" in report:
            parts = report.split("## Executive Summary", 1)
            if len(parts) == 2:
                exec_section = parts[1]
                next_header_pos = exec_section.find("\n##")
                
                if next_header_pos > 0:
                    exec_content = exec_section[:next_header_pos]
                    rest_content = exec_section[next_header_pos:]
                    return (parts[0] + "## Executive Summary" + exec_content + 
                           "\n\n" + visuals + "\n" + rest_content)
                else:
                    return parts[0] + "## Executive Summary" + exec_section + "\n\n" + visuals
        
        # Fallback: insert after first major section
        if "\n## " in report:
            first_header = report.find("\n## ")
            second_header = report.find("\n## ", first_header + 1)
            if second_header > 0:
                return report[:second_header] + "\n\n" + visuals + report[second_header:]
        
        # Last resort: add at beginning
        return visuals + "\n\n" + report
    
    def _format_evidence(self, evidence: List[Dict]) -> str:
        """Format evidence for LLM consumption"""
        formatted = []
        
        for i, item in enumerate(evidence, 1):
            formatted.append(f"""
Evidence {i}:
- Source: {item['title']}
- Key Points: {item['evidence'][:500]}
- Relevance Score: {item['relevance']:.2f}
""")
        
        return '\n'.join(formatted)
    
    def _add_metadata(self, report: str, prompt: str, evidence_count: int) -> str:
        """Add metadata header to report"""
        metadata = f"""**Research Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Topic:** {prompt}

**Sources Analyzed:** {evidence_count}

---

"""
        return metadata + report
    
    def _add_sources(self, report: str, evidence: List[Dict]) -> str:
        """Add sources section to report"""
        sources_section = "\n\n## Evidence Sources\n\n"
        
        for i, item in enumerate(evidence[:10], 1):
            sources_section += f"{i}. [{item['title']}]({item['source']})\n"
        
        return report + sources_section
    
    def _create_basic_report(self, prompt: str, plan: Dict, evidence: List[Dict]) -> str:
        """Create basic report if LLM fails"""
        report = f"""# Research Report: {prompt}

## Executive Summary

This research examined {prompt}. Analysis was conducted across {len(evidence)} sources 
covering {', '.join(plan.get('research_angles', ['multiple perspectives']))}.

## Key Findings

"""
        
        for i, item in enumerate(evidence[:5], 1):
            report += f"""
### Finding {i}: {item['title']}

{item['evidence'][:300]}...

*Source: {item['source']}*
"""
        
        report += """

## Conclusion

Further research is recommended to fully understand all implications.
"""
        
        return report
