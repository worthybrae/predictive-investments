# api/routes/ai/screening.py
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List
import logging
from pydantic import BaseModel

from dependencies import get_api_key
from services.ai import AIService

logger = logging.getLogger(__name__)

router = APIRouter()

class FilterGenerationRequest(BaseModel):
    """Request model for generating Finviz screener filters."""
    prediction_text: str
    prediction_analysis: Dict[str, Any]
    model: str = "gpt-4o-mini-mini"

@router.post(
    "/generate-filters",
    response_model=Dict[str, Any],
    summary="Generate Finviz filters",
    description="Generate Finviz screener filters based on a prediction"
)
async def generate_finviz_filters(
    request: FilterGenerationRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Generate Finviz screener filters based on a prediction.
    
    Parameters:
    - prediction_text: The prediction text
    - prediction_analysis: Structured analysis of the prediction
    - model: OpenAI model to use
    """
    return await AIService.generate_finviz_filters(
        prediction_text=request.prediction_text,
        prediction_analysis=request.prediction_analysis,
        model=request.model
    )

@router.post(
    "/run-screener",
    response_model=List[str],
    summary="Run Finviz screener",
    description="Run the Finviz screener with the given filters"
)
async def run_finviz_screener(
    filters: Dict[str, str],
    api_key: str = Depends(get_api_key),
):
    """
    Run the Finviz screener with the given filters.
    
    Parameters:
    - filters: Dictionary of filter name-value pairs
    """
    return await AIService.run_finviz_screener(filters)