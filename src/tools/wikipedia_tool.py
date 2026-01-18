"""
Wikipedia Tool - Specialized tool for Wikipedia searches
Provides reliable fallback for factual information
"""

import wikipedia
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
import re

@dataclass
class WikipediaResult:
    """Structured Wikipedia result"""
    title: str
    summary: str
    url: str
    categories: List[str]
    references: int
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'snippet': self.summary,
            'url': self.url,
            'source': 'wikipedia',
            'metadata': {
                'categories': self.categories,
                'references': self.references
            }
        }

class WikipediaTool:
    """
    Wikipedia search and content extraction tool
    Provides high-quality, factual information as fallback
    """
    
    def __init__(self):
        # Configure Wikipedia
        wikipedia.set_lang("en")
        self.session = requests.Session()
        
    def search(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search Wikipedia for relevant articles
        """
        results = []
        
        try:
            # Search for pages
            search_results = wikipedia.search(query, results=max_results * 2)
            
            for page_title in search_results[:max_results]:
                try:
                    # Get page content
                    result = self._get_page_info(page_title)
                    if result:
                        results.append(result.to_dict())
                except Exception as e:
                    print(f"Failed to get Wikipedia page '{page_title}': {e}")
                    continue
            
            # If no results, try disambiguation
            if not results and search_results:
                results = self._handle_disambiguation(query, max_results)
                
        except Exception as e:
            print(f"Wikipedia search error: {e}")
        
        return results
    
    def _get_page_info(self, title: str) -> Optional[WikipediaResult]:
        """Get detailed information about a Wikipedia page"""
        try:
            page = wikipedia.page(title)
            
            # Get summary (first paragraph or 500 chars)
            summary = page.summary
            if len(summary) > 500:
                # Try to cut at sentence boundary
                sentences = summary[:500].split('. ')
                if len(sentences) > 1:
                    summary = '. '.join(sentences[:-1]) + '.'
                else:
                    summary = summary[:497] + '...'
            
            # Count references (approximate)
            ref_count = len(page.references) if hasattr(page, 'references') else 0
            
            # Get categories
            categories = page.categories[:5] if hasattr(page, 'categories') else []
            
            return WikipediaResult(
                title=page.title,
                summary=summary,
                url=page.url,
                categories=categories,
                references=ref_count
            )
            
        except wikipedia.exceptions.DisambiguationError as e:
            # Handle disambiguation pages
            if e.options:
                return self._get_page_info(e.options[0])
        except wikipedia.exceptions.PageError:
            return None
        except Exception as e:
            print(f"Error getting page info: {e}")
            return None
    
    def _handle_disambiguation(self, query: str, max_results: int) -> List[Dict]:
        """Handle disambiguation pages"""
        results = []
        
        try:
            # Try to get disambiguation page
            page = wikipedia.page(f"{query} (disambiguation)")
            
            # Extract links from disambiguation page
            links = page.links[:max_results * 2]
            
            for link in links:
                if len(results) >= max_results:
                    break
                    
                try:
                    result = self._get_page_info(link)
                    if result:
                        results.append(result.to_dict())
                except:
                    continue
                    
        except:
            pass
        
        return results
    
    def get_page_sections(self, page_title: str) -> Dict[str, str]:
        """
        Get specific sections from a Wikipedia page
        Useful for detailed research
        """
        sections = {}
        
        try:
            page = wikipedia.page(page_title)
            content = page.content
            
            # Split content by headers (== Header ==)
            section_pattern = r'\n== (.*?) ==\n'
            section_splits = re.split(section_pattern, content)
            
            # First section (before any headers) is the introduction
            if section_splits:
                sections['Introduction'] = section_splits[0].strip()
            
            # Process remaining sections
            for i in range(1, len(section_splits), 2):
                if i + 1 < len(section_splits):
                    section_name = section_splits[i]
                    section_content = section_splits[i + 1].strip()
                    
                    # Limit section length
                    if len(section_content) > 1000:
                        section_content = section_content[:997] + '...'
                    
                    sections[section_name] = section_content
                    
        except Exception as e:
            print(f"Failed to get sections for '{page_title}': {e}")
        
        return sections
    
    def search_related(self, topic: str, max_results: int = 5) -> List[Dict]:
        """
        Search for related Wikipedia articles
        Useful for comprehensive research
        """
        results = []
        
        try:
            # Get main page
            main_page = wikipedia.page(topic)
            
            # Get linked pages (related topics)
            related_titles = main_page.links[:max_results * 2]
            
            for title in related_titles:
                if len(results) >= max_results:
                    break
                    
                # Filter out disambiguation and list pages
                if '(disambiguation)' in title or 'List of' in title:
                    continue
                    
                try:
                    result = self._get_page_info(title)
                    if result:
                        results.append(result.to_dict())
                except:
                    continue
                    
        except Exception as e:
            print(f"Failed to get related articles: {e}")
        
        return results
    
    def fact_check(self, claim: str) -> Optional[Dict]:
        """
        Try to fact-check a claim using Wikipedia
        Returns relevant Wikipedia content for verification
        """
        # Extract key terms from claim
        keywords = self._extract_keywords(claim)
        
        if not keywords:
            return None
        
        # Search for relevant articles
        search_query = ' '.join(keywords)
        results = self.search(search_query, max_results=1)
        
        if results:
            result = results[0]
            result['fact_check_claim'] = claim
            result['confidence'] = self._calculate_relevance(claim, result['snippet'])
            return result
        
        return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from text for searching"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'must', 'can', 'what', 'which', 'who',
            'whom', 'whose', 'where', 'when', 'why', 'how', 'this', 'that', 'these',
            'those', 'it', 'its'
        }
        
        # Simple keyword extraction
        words = text.lower().split()
        keywords = []
        
        for word in words:
            # Clean word
            word = re.sub(r'[^\w\s]', '', word)
            
            # Skip stop words and short words
            if word not in stop_words and len(word) > 2:
                keywords.append(word)
        
        # Return unique keywords (maintain order)
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:5]  # Limit to 5 keywords
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """Calculate relevance score between query and content"""
        query_words = set(self._extract_keywords(query))
        content_words = set(self._extract_keywords(content))
        
        if not query_words:
            return 0.0
        
        # Calculate overlap
        overlap = len(query_words.intersection(content_words))
        relevance = overlap / len(query_words)
        
        return min(1.0, relevance)