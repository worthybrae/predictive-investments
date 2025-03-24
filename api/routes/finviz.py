# api/routes/finviz.py
from typing import List
from fastapi import APIRouter, Depends
from api.models.finviz import ScreenerRequest, ScreenerResponse, FiltersResponse, OptionResponse, OptionRequest
from api.services.finviz import FinvizService
from api.dependencies import get_api_key

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.post(
    "/screener",
    response_model=ScreenerResponse,
    summary="Get stock tickers from screener",
    description="Retrieve tickers from screener based on specified filters"
)
async def get_screener_results(
    request: ScreenerRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Get stock tickers from screener based on applied filters.
    
    Parameters:
    - request: ScreenerRequest object with optional filters
    """
    return await FinvizService.scrape_screener_results(request.filters)

@router.get(
    "/filters",
    response_model=FiltersResponse,
    summary="Get available filters",
    description="Retrieve all available filters that can be used with the screener"
)
async def get_available_filters(
    api_key: str = Depends(get_api_key)
):
    """
    Get all available filters for the screener.
    """
    return await FinvizService.get_available_filters()

@router.post(
    "/options",
    response_model=OptionResponse,
    summary="Get available filter options",
    description="Retrieve all available options for specified filters that can be used with the screener"
)
async def get_filter_options(
    selected_filters: OptionRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Get all available options for the specified filters.
    
    Parameters:
    - selected_filters: List of filter names to get options for
    """
    return await FinvizService.get_filter_options(selected_filters.filters)