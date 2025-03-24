# api/routes/ai/prediction.py
from fastapi import APIRouter, Depends, Path, Query, HTTPException
from typing import Dict, Any, List
import logging
from pydantic import BaseModel

from services.ai import AIService

from models.predictions import PredictionStatusResponse
from dependencies import get_api_key
from services.prediction_queue import PredictionQueueManager

logger = logging.getLogger(__name__)

router = APIRouter()

class PredictionRequest(BaseModel):
    """Request model for full prediction analysis."""
    prediction_text: str
    model: str = "gpt-4o-mini"
    use_web_search: bool = False
    search_model: str = "sonar"
    use_finviz_screener: bool = True
    include_stock_data: bool = False
    include_year_data: bool = False
    include_week_data: bool = False

@router.post(
    "/predict",
    summary="Full prediction analysis pipeline",
    description="Run a complete prediction analysis pipeline including analysis, market research, ticker selection, and strategy creation"
)
async def full_prediction_analysis(
    request: PredictionRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Run a complete prediction analysis pipeline.
    
    Parameters:
    - prediction_text: The prediction to analyze
    - model: OpenAI model to use
    - use_web_search: Whether to use web search
    - search_model: Perplexity model to use
    - use_finviz_screener: Whether to use Finviz screener
    - include_stock_data: Whether to include stock data
    - include_year_data: Whether to include 1-year data
    - include_week_data: Whether to include 1-week data
    """
    return await AIService.full_prediction_analysis(
        prediction_text=request.prediction_text,
        model=request.model,
        use_web_search=request.use_web_search,
        search_model=request.search_model,
        use_finviz_screener=request.use_finviz_screener,
        include_stock_data=request.include_stock_data,
        include_year_data=request.include_year_data,
        include_week_data=request.include_week_data
    )

@router.post(
    "/analyze-prediction",
    response_model=Dict[str, Any],
    summary="Analyze a prediction",
    description="Extract structured information from a prediction statement"
)
async def analyze_prediction(
    prediction_text: str = Query(..., description="The prediction to analyze"),
    model: str = Query("gpt-4o-mini", description="OpenAI model to use"),
    api_key: str = Depends(get_api_key),
):
    """
    Analyze a prediction to extract key details.
    
    Parameters:
    - prediction_text: The prediction to analyze
    - model: OpenAI model to use
    """
    return await AIService.analyze_prediction(
        prediction_text=prediction_text,
        model=model
    )

@router.post(
    "/predict/async",
    response_model=dict,
    summary="Create asynchronous prediction analysis",
    description="Start an asynchronous prediction analysis and return a prediction ID"
)
async def create_async_prediction(
    request: dict,
    api_key: str = Depends(get_api_key)
):
    """
    Create a new asynchronous prediction analysis.
    
    Parameters:
    - prediction_text: The prediction to analyze
    - options: Optional processing options
    """
    prediction_text = request.get("prediction_text")
    if not prediction_text:
        raise HTTPException(status_code=400, detail="Prediction text is required")
    
    options = request.get("options", {})
    
    # Create prediction
    prediction_id = PredictionQueueManager.create_prediction(
        prediction_text=prediction_text,
        options=options
    )
    
    return {
        "prediction_id": prediction_id,
        "message": "Prediction queued for processing. Use the /predict/async/{prediction_id} endpoint to check status."
    }

@router.get(
    "/predict/async/{prediction_id}",
    response_model=PredictionStatusResponse,
    summary="Get prediction status",
    description="Get the current status of an asynchronous prediction"
)
async def get_prediction_status(
    prediction_id: str = Path(..., description="The prediction ID"),
    api_key: str = Depends(get_api_key)
):
    """
    Get the current status of a prediction.
    
    Parameters:
    - prediction_id: The prediction ID
    """
    status = PredictionQueueManager.get_prediction_status(prediction_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Prediction not found with ID: {prediction_id}")
    
    return status

@router.get(
    "/predict/async",
    response_model=List[PredictionStatusResponse],
    summary="List predictions",
    description="List recent predictions"
)
async def list_predictions(
    limit: int = Query(10, description="Maximum number of predictions to return", ge=1, le=100),
    api_key: str = Depends(get_api_key)
):
    """
    List recent predictions.
    
    Parameters:
    - limit: Maximum number of predictions to return
    """
    return PredictionQueueManager.list_predictions(limit=limit)