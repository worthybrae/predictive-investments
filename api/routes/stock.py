# api/routes/stocks.py
from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
from api.models.stocks import StockDataResponse, StockDetailsResponse, NewsResponse
from api.models.enums import Timespan, SortOrder
from api.dependencies import get_api_key
from api.services.polygon import PolygonService

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get(
    "/{ticker}/ohlc/{multiplier}/{timespan}/{from_date}/{to_date}",
    response_model=StockDataResponse,
    summary="Get OHLC data for a stock",
    description="Retrieve aggregated historical OHLC data for a specified stock ticker over a custom date range and time interval",
)
async def get_stock_ohlc(
    ticker: str,
    multiplier: int,
    timespan: str = Path(..., description="Time window size (minute, hour, day, week, month, quarter, year)"),
    from_date: str = Path(..., description="Start date in YYYY-MM-DD format"),
    to_date: str = Path(..., description="End date in YYYY-MM-DD format"),
    adjusted: bool = Query(True, description="Whether or not the results are adjusted for splits"),
    sort: SortOrder = Query(SortOrder.asc, description="Sort the results by timestamp"),
    limit: int = Query(5000, description="Limits the number of base aggregates queried", le=50000),
    api_key: str = Depends(get_api_key),
):
    """
    Get OHLC (Open, High, Low, Close) data for a stock ticker.
    
    Parameters:
    - ticker: Stock ticker symbol (e.g., AAPL for Apple)
    - multiplier: The size of the timespan multiplier
    - timespan: The size of the time window (minute, hour, day, etc.)
    - from_date: Start date in YYYY-MM-DD format or millisecond timestamp
    - to_date: End date in YYYY-MM-DD format or millisecond timestamp
    - adjusted: Whether results are adjusted for splits
    - sort: Sort order (asc or desc)
    - limit: Limit the number of results
    """
    # Validate the timespan
    if timespan not in [t.value for t in Timespan]:
        valid_timespans = ", ".join([t.value for t in Timespan])
        raise ValueError(f"Invalid timespan: {timespan}. Valid options are: {valid_timespans}")
    
    # Convert to Enum
    timespan_enum = Timespan(timespan)
    
    return await PolygonService.get_stock_aggregates(
        ticker=ticker,
        multiplier=multiplier,
        timespan=timespan_enum,
        from_date=from_date,
        to_date=to_date,
        adjusted=adjusted,
        sort=sort,
        limit=limit
    )

@router.get(
    "/{ticker}/details",
    response_model=StockDetailsResponse,
    summary="Get stock ticker details",
    description="Retrieve comprehensive details for a single stock ticker including company information, branding, and market data",
)
async def get_stock_details(
    ticker: str,
    date: Optional[str] = Query(None, description="Date to get historical info (YYYY-MM-DD)"),
    api_key: str = Depends(get_api_key),
):
    """
    Get comprehensive details for a single stock ticker.
    
    Parameters:
    - ticker: Stock ticker symbol (e.g., AAPL for Apple)
    - date: Optional date to get historical information (YYYY-MM-DD)
    """
    return await PolygonService.get_ticker_details(
        ticker=ticker,
        date=date
    )

@router.get(
    "/news",
    response_model=NewsResponse,
    summary="Get stock news articles",
    description="Retrieve recent news articles related to stocks with filtering options"
)
async def get_stock_news(
    ticker: Optional[str] = Query(None, description="Stock ticker symbol (e.g., AAPL)"),
    published_utc: Optional[str] = Query(None, description="Published date (YYYY-MM-DD format or RFC3339)"),
    order: str = Query("desc", description="Sort order (asc or desc)"),
    limit: int = Query(10, description="Limit the number of results", ge=1, le=1000),
    sort: str = Query("published_utc", description="Field to sort results by"),
    api_key: str = Depends(get_api_key),
):
    """
    Get news articles related to stocks.
    
    Parameters:
    - ticker: Optional stock ticker symbol to filter news
    - published_utc: Return results published on, before, or after this date
    - order: Sort order (asc or desc)
    - limit: Limit the number of results (max 1000)
    - sort: Field to sort results by
    """
    # Validate sort field (current API only supports sorting by published_utc)
    if sort != "published_utc":
        raise ValueError(f"Invalid sort field: {sort}. Only 'published_utc' is supported.")
    
    # Validate order
    if order not in ["asc", "desc"]:
        raise ValueError(f"Invalid order: {order}. Must be 'asc' or 'desc'.")
    
    return await PolygonService.get_ticker_news(
        ticker=ticker,
        published_utc=published_utc,
        order=order,
        limit=limit,
        sort=sort
    )