# api/services/perplexity.py
import os
import uuid
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from api.core.exceptions import ConfigurationException

load_dotenv()

class PerplexityService:
    """Service for interacting with the Perplexity API."""
    
    BASE_URL = "https://api.perplexity.ai/chat/completions"
    
    @classmethod
    def _get_api_key(cls):
        """Get the Perplexity API key from environment variables."""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ConfigurationException(detail="Perplexity API key not configured")
        return api_key
    
    @classmethod
    async def search(
        cls,
        query: str,
        model: str = "sonar",
        temperature: float = 0.2,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Perform a web search using Perplexity API.
        
        Args:
            query: The search query
            model: The model to use (e.g., "sonar", "mistral")
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            The API response
        """
        api_key = cls._get_api_key()
        
        # Prepare the API request payload
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "Be precise and concise. Provide comprehensive and accurate information based on web search results."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "search_domain_filter": ["<any>"],
            "return_images": False,
            "return_related_questions": False,
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1,
            "web_search_options": {"search_context_size": "high"}
        }
        
        # Headers with API key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Make the API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    cls.BASE_URL,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                # Check if the request was successful
                response.raise_for_status()
                
                # Parse the response
                response_data = response.json()
                
                # Format the response with some additional metadata
                return {
                    "request_id": str(uuid.uuid4()),
                    "success": True,
                    "model": model,
                    "content": response_data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "raw_response": response_data
                }
                
        except httpx.HTTPStatusError as e:
            return {
                "request_id": str(uuid.uuid4()),
                "success": False,
                "error": f"HTTP error: {e.response.status_code}",
                "details": e.response.text if e.response else None
            }
        except httpx.RequestError as e:
            return {
                "request_id": str(uuid.uuid4()),
                "success": False,
                "error": f"Request error: {str(e)}"
            }
        except Exception as e:
            return {
                "request_id": str(uuid.uuid4()),
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    @classmethod
    async def search_market_info(
        cls,
        query: str,
        model: str = "sonar",
        temperature: float = 0.2,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Search for market information related to a query.
        
        Args:
            query: The search query about market information
            model: Perplexity model to use
            temperature: Temperature parameter
            max_tokens: Maximum tokens in the response
            
        Returns:
            Search results from Perplexity
        """
        enhanced_query = f"""Provide detailed market research information about:
        {query}
        
        Focus on:
        - Public companies that might be affected (ALWAYS include stock tickers)
        - List several specific stock tickers directly related to this topic
        - Industry trends and recent market developments
        - Analyst opinions and market forecasts
        - Current market conditions related to this topic
        
        IMPORTANT: For every company you mention, include its stock ticker symbol in parentheses.
        Be specific about why each company/ticker is relevant to the query.
        """
        
        return await cls.search(
            query=enhanced_query,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )