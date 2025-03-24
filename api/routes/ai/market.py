# api/routes/ai/market.py
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List, Optional
import logging

from api.dependencies import get_api_key
from api.services.ai import AIService
from api.services.industry_mapper import IndustryMapperService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/market-research",
    response_model=Dict[str, Any],
    summary="Get market research",
    description="Use Perplexity to gather market research related to a prediction"
)
async def get_market_research(
    prediction_text: str = Query(..., description="The prediction to research"),
    industries: Optional[List[str]] = Query(None, description="Industries to focus on"),
    timeframe: Optional[str] = Query(None, description="Timeframe of the prediction"),
    search_model: str = Query("sonar", description="Perplexity model to use"),
    api_key: str = Depends(get_api_key),
):
    """
    Get market research for a prediction using Perplexity.
    
    Parameters:
    - prediction_text: The prediction statement
    - industries: Specific industries to focus on
    - timeframe: Timeframe of the prediction
    - search_model: Perplexity model to use
    """
    return await AIService.get_market_research(
        prediction_text=prediction_text,
        industries=industries,
        timeframe=timeframe,
        search_model=search_model
    )

@router.post(
    "/find-tickers",
    response_model=Dict[str, Any],
    summary="Find relevant tickers",
    description="Identify stock tickers relevant to a prediction"
)
async def find_relevant_tickers(
    prediction_text: str = Query(..., description="The prediction text"),
    prediction_analysis: Optional[Dict[str, Any]] = None,
    use_web_search: bool = Query(False, description="Whether to use web search"),
    search_model: str = Query("sonar", description="Perplexity model to use"),
    model: str = Query("gpt-4o-mini", description="OpenAI model to use"),
    api_key: str = Depends(get_api_key),
):
    """
    Find tickers relevant to a prediction.
    
    Parameters:
    - prediction_text: The prediction text
    - prediction_analysis: Optional pre-computed analysis
    - use_web_search: Whether to use web search
    - search_model: Perplexity model to use
    - model: OpenAI model to use
    """
    return await AIService.find_relevant_tickers(
        prediction_text=prediction_text,
        prediction_analysis=prediction_analysis,
        use_web_search=use_web_search,
        search_model=search_model,
        model=model
    )

@router.get(
    "/industries",
    response_model=Dict[str, Any],
    summary="Get available industries",
    description="List all available industries for prediction analysis"
)
async def get_industries(
    api_key: str = Depends(get_api_key),
):
    """
    Get a list of all available industries that can be used in predictions.
    
    Returns:
        Dictionary of industry codes and names
    """
    try:
        industry_data = IndustryMapperService.get_industries_for_prompt()
        return {
            "success": True,
            "count": len(industry_data["industries"]),
            "filter_name": industry_data["industry_filter_name"],
            "description": industry_data["industry_filter_description"],
            "industries": industry_data["industries"]
        }
    except Exception as e:
        logger.exception("Error getting industries")
        return {
            "success": False,
            "error": f"Error retrieving industries: {str(e)}",
            "industries": {}
        }