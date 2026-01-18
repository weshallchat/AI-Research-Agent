"""
Search Agent - Updated to use the new tool implementations
"""

from typing import List, Dict
from src.tools.web_search import WebSearchTool
from src.tools.wikipedia_tool import WikipediaTool

class SearchAgent:
    def __init__(self):
        """Initialize search tools"""
        self.web_tool = WebSearchTool()
        self.wiki_tool = WikipediaTool()
        
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Primary search function using web search tool
        """
        return self.web_tool.search(query, max_results)
    
    def fallback_search(self, query: str) -> List[Dict]:
        """
        Fallback search using Wikipedia
        As Saikat Da suggested - info na pele ki korbi
        """
        return self.wiki_tool.search(query, max_results=3)
    
    def academic_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Specialized academic search for research papers
        """
        return self.web_tool.search_academic(query, max_results)
    
    def comprehensive_search(self, query: str) -> List[Dict]:
        """
        Comprehensive search across all available sources
        Used for important research topics
        """
        results = []
        
        # Web search
        web_results = self.web_tool.search(query, max_results=3)
        results.extend(web_results)
        
        # Wikipedia search
        wiki_results = self.wiki_tool.search(query, max_results=2)
        results.extend(wiki_results)
        
        # Academic search if query seems academic
        academic_keywords = ['research', 'study', 'analysis', 'theory', 'model', 
                           'algorithm', 'method', 'evaluation', 'experiment']
        if any(keyword in query.lower() for keyword in academic_keywords):
            academic_results = self.web_tool.search_academic(query, max_results=2)
            results.extend(academic_results)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    def fetch_full_content(self, url: str) -> str:
        """
        Fetch full content from a URL when snippet isn't enough
        """
        content = self.web_tool.fetch_content(url)
        return content if content else "Failed to fetch content"
    
    def fact_check(self, claim: str) -> Dict:
        """
        Attempt to fact-check a claim using Wikipedia
        """
        result = self.wiki_tool.fact_check(claim)
        if result:
            return result
        
        # Fallback to web search for fact checking
        query = f"fact check {claim}"
        web_results = self.web_tool.search(query, max_results=1)
        if web_results:
            return web_results[0]
        
        return {
            'title': 'Fact check unavailable',
            'snippet': 'Could not find reliable sources to verify this claim',
            'source': 'none'
        }