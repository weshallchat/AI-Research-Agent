"""
Helper utilities for the research agent
"""

import os
from langchain_openai import ChatOpenAI
from langchain.llms.base import LLM

def setup_llm(model: str = "gpt-4o", temperature: float = 0.3) -> LLM:
    """
    Main LLM for research tasks such as planning, extracting evidence, and synthesizing report
    More capable for complex reasoning and synthesis of information
    Setup LLM with fallback options for more basic tasks
    """
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    try:
        # Try to initialize with specified model
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            max_tokens=2000  # Control costs
        )
        return llm
    except Exception as e:
        print(f"Failed to initialize {model}, falling back to gpt-4o-mini: {e}")
        # Fallback to most basic model
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=temperature,
            api_key=api_key,
            max_tokens=1000
        )

def estimate_cost(tokens_used: int, model: str = "gpt-4o-mini") -> float:
    """Estimate API cost based on tokens used"""
    # Approximate costs per 1K tokens
    costs = {
        "gpt-3.5-turbo": 0.002,
        "gpt-4": 0.03,
        "gpt-4-turbo": 0.01
    }
    
    cost_per_1k = costs.get(model, 0.002)
    return (tokens_used / 1000) * cost_per_1k

def clean_text(text: str, max_length: int = 1000) -> str:
    """Clean and truncate text for processing"""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Truncate if needed
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

def setup_lightweight_llm(model: str = "gpt-4o-mini", temperature: float = 0.2):
    """
    Setup a lightweight LLM for simple tasks like query transformation
    Uses lower max_tokens and temperature for faster, cheaper responses
    """
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=api_key,
        max_tokens=500  # Query transformation needs fewer tokens
    )