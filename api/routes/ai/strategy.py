# api/routes/ai/strategy.py
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional
import logging
from pydantic import BaseModel

from api.dependencies import get_api_key
from api.services.ai import AIService

logger = logging.getLogger(__name__)

router = APIRouter()

class StrategyRequest(BaseModel):
    """Request model for creating an investment strategy."""
    prediction_text: str
    prediction_analysis: Optional[Dict[str, Any]] = None
    relevant_tickers: Optional[Dict[str, Any]] = None
    market_research: Optional[str] = None
    include_stock_data: bool = False
    include_year_data: bool = False
    include_week_data: bool = False
    model: str = "gpt-4o-mini"

@router.post(
    "/create-strategy",
    response_model=Dict[str, Any],
    summary="Create investment strategy",
    description="Generate an investment strategy based on a prediction and analysis"
)
async def create_investment_strategy(
    request: StrategyRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Create an investment strategy based on a prediction.
    
    Parameters:
    - prediction_text: The prediction statement
    - prediction_analysis: Optional pre-computed analysis
    - relevant_tickers: Optional pre-computed tickers
    - market_research: Optional pre-computed research
    - include_stock_data: Whether to include stock data
    - include_year_data: Whether to include 1-year data
    - include_week_data: Whether to include 1-week data
    - model: OpenAI model to use
    """
    return await AIService.create_investment_strategy(
        prediction_text=request.prediction_text,
        prediction_analysis=request.prediction_analysis,
        relevant_tickers=request.relevant_tickers,
        market_research=request.market_research,
        include_stock_data=request.include_stock_data,
        include_year_data=request.include_year_data,
        include_week_data=request.include_week_data,
        model=request.model
    )