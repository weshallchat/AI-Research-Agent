"""
Web Search Tool - Implements multiple search backends with fallback
Fallback strategies for reliability
"""

import os
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
import requests
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import urllib.parse

@dataclass
class SearchResult:
    """Structured search result"""
    title: str
    snippet: str
    url: str
    source: str
    timestamp: str = None
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'snippet': self.snippet,
            'url': self.url,
            'source': self.source,
            'timestamp': self.timestamp or time.strftime('%Y-%m-%d %H:%M:%S')
        }

class WebSearchTool:
    """
    Multi-backend web search tool with fallback chain:
    1. Serper API (if available)
    2. DuckDuckGo 
    3. Bing Search (if API key available)
    4. Google Custom Search (if configured)
    """
    
    def __init__(self):
        # API Keys from environment
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.bing_api_key = os.getenv('BING_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cx = os.getenv('GOOGLE_CX')  # Custom search engine ID
        
        # Initialize DuckDuckGo (no API key needed)
        self.ddgs = DDGS()
        
        # Track usage for rate limiting
        self.request_times = []
        self.rate_limit_per_minute = 20
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Main search method with automatic fallback
        """
        # Rate limiting
        self._enforce_rate_limit()
        
        # Try search backends in order
        search_methods = [
            ('serper', self._search_serper),
            ('duckduckgo', self._search_duckduckgo),
            ('bing', self._search_bing),
            ('google', self._search_google_custom),
        ]
        
        for backend_name, search_method in search_methods:
            try:
                results = search_method(query, max_results)
                if results:
                    print(f"  ✓ Search successful with {backend_name}")
                    return results
            except Exception as e:
                print(f"{backend_name} search failed: {str(e)[:50]}")
                continue
        
        # If all fail, return empty list
        print(f"All search backends failed for query: {query}")
        return []
    
    def _enforce_rate_limit(self):
        """Simple rate limiting to avoid API bans"""
        now = time.time()
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= self.rate_limit_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                print(f"  ⏳ Rate limit reached, waiting {sleep_time:.1f}s...")
                time.sleep(sleep_time)
        
        self.request_times.append(now)
    
    def _search_serper(self, query: str, max_results: int) -> List[Dict]:
        """Search using Serper API (Google results)"""
        if not self.serper_api_key:
            raise ValueError("Serper API key not configured")
        
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': max_results,
            'gl': 'us',
            'hl': 'en'
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        # Extract organic results
        for item in data.get('organic', [])[:max_results]:
            result = SearchResult(
                title=item.get('title', ''),
                snippet=item.get('snippet', ''),
                url=item.get('link', ''),
                source='serper/google'
            )
            results.append(result.to_dict())
        
        # Also get featured snippets if available
        if 'answerBox' in data:
            answer = data['answerBox']
            result = SearchResult(
                title=answer.get('title', 'Featured Answer'),
                snippet=answer.get('snippet', answer.get('answer', '')),
                url=answer.get('link', ''),
                source='serper/featured'
            )
            results.insert(0, result.to_dict())
        
        return results
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """Search using DuckDuckGo (no API key required)"""
        results = []
        
        try:
            # Text search
            search_results = self.ddgs.text(
                query, 
                max_results=max_results,
                safesearch='off',
                backend='api'
            )
            
            for item in search_results:
                result = SearchResult(
                    title=item.get('title', ''),
                    snippet=item.get('body', ''),
                    url=item.get('href', ''),
                    source='duckduckgo'
                )
                results.append(result.to_dict())
            
            # Try to get instant answer if available
            instant = self.ddgs.answers(query)
            if instant:
                for answer in instant[:1]:  # Just first answer
                    result = SearchResult(
                        title="Quick Answer",
                        snippet=answer.get('text', ''),
                        url=answer.get('url', ''),
                        source='duckduckgo/instant'
                    )
                    results.insert(0, result.to_dict())
                    
        except Exception as e:
            print(f"DuckDuckGo error: {e}")
            raise
        
        return results
    
    def _search_bing(self, query: str, max_results: int) -> List[Dict]:
        """Search using Bing Search API"""
        if not self.bing_api_key:
            raise ValueError("Bing API key not configured")
        
        endpoint = "https://api.bing.microsoft.com/v7.0/search"
        headers = {'Ocp-Apim-Subscription-Key': self.bing_api_key}
        params = {
            'q': query,
            'count': max_results,
            'textDecorations': False,
            'textFormat': 'HTML'
        }
        
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('webPages', {}).get('value', [])[:max_results]:
            # Clean HTML from snippet
            soup = BeautifulSoup(item.get('snippet', ''), 'html.parser')
            clean_snippet = soup.get_text()
            
            result = SearchResult(
                title=item.get('name', ''),
                snippet=clean_snippet,
                url=item.get('url', ''),
                source='bing'
            )
            results.append(result.to_dict())
        
        return results
    
    def _search_google_custom(self, query: str, max_results: int) -> List[Dict]:
        """Search using Google Custom Search API"""
        if not self.google_api_key or not self.google_cx:
            raise ValueError("Google Custom Search not configured")
        
        endpoint = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.google_api_key,
            'cx': self.google_cx,
            'q': query,
            'num': min(max_results, 10)  # Google limits to 10 per request
        }
        
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('items', [])[:max_results]:
            result = SearchResult(
                title=item.get('title', ''),
                snippet=item.get('snippet', ''),
                url=item.get('link', ''),
                source='google_custom'
            )
            results.append(result.to_dict())
        
        return results
    
    def search_academic(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Specialized academic search
        Uses Google Scholar via SerperDev or fallback to ArXiv
        """
        results = []
        
        # Try Google Scholar via Serper
        if self.serper_api_key:
            try:
                results = self._search_google_scholar(query, max_results)
                if results:
                    return results
            except:
                pass
        
        # Fallback to ArXiv
        try:
            results = self._search_arxiv(query, max_results)
        except:
            pass
        
        return results
    
    def _search_google_scholar(self, query: str, max_results: int) -> List[Dict]:
        """Search Google Scholar via Serper API"""
        if not self.serper_api_key:
            raise ValueError("Serper API key not configured")
        
        url = "https://google.serper.dev/scholar"
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': max_results
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('organic', [])[:max_results]:
            result = SearchResult(
                title=item.get('title', ''),
                snippet=item.get('snippet', ''),
                url=item.get('link', ''),
                source='google_scholar'
            )
            results.append(result.to_dict())
        
        return results
    
    def _search_arxiv(self, query: str, max_results: int) -> List[Dict]:
        """Search ArXiv for academic papers"""
        import urllib
        import feedparser
        
        # Construct ArXiv API URL
        base_url = 'http://export.arxiv.org/api/query?'
        query_params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        url = base_url + urllib.parse.urlencode(query_params)
        
        # Parse the feed
        feed = feedparser.parse(url)
        results = []
        
        for entry in feed.entries[:max_results]:
            # Extract abstract
            abstract = entry.get('summary', '')
            if len(abstract) > 300:
                abstract = abstract[:297] + '...'
            
            result = SearchResult(
                title=entry.get('title', ''),
                snippet=abstract,
                url=entry.get('link', ''),
                source='arxiv'
            )
            results.append(result.to_dict())
        
        return results
    
    def fetch_content(self, url: str) -> Optional[str]:
        """
        Fetch full content from a URL
        Used when snippet isn't enough
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit length
            max_length = 5000
            if len(text) > max_length:
                text = text[:max_length] + '...'
            
            return text
            
        except Exception as e:
            print(f"Failed to fetch content from {url}: {e}")
            return None