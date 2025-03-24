# api/routes/indices.py
from fastapi import APIRouter, Depends, Query, Path
from typing import Optional, List
from models.stocks import StockDataResponse
from models.tickers import TickersResponse
from models.enums import Timespan, SortOrder
from dependencies import get_api_key
from services.polygon import PolygonService

router = APIRouter(prefix="/indices", tags=["indices"])

@router.get(
    "",
    response_model=TickersResponse,
    summary="List all indices",
    description="Retrieve a list of all available indices tickers"
)
async def list_indices(
    search: Optional[str] = Query(None, description="Search for terms within the ticker and/or index name"),
    active: bool = Query(True, description="Filter to only active indices"),
    order: SortOrder = Query(SortOrder.asc, description="Order results based on the sort field"),
    limit: int = Query(100, description="Limit the number of results returned", ge=1, le=1000),
    sort: str = Query("ticker", description="Sort field used for ordering"),
    api_key: str = Depends(get_api_key),
):
    """
    List all available indices tickers.
    
    Parameters:
    - search: Optional search term to filter indices
    - active: Filter to only active indices
    - order: Sort order (asc or desc)
    - limit: Limit the number of results (max 1000)
    - sort: Field to sort results by
    """
    return await PolygonService.list_tickers(
        market="indices",
        search=search,
        active=active,
        order=order.value,
        limit=limit,
        sort=sort
    )

@router.get(
    "/{indices_ticker}/ohlc/{multiplier}/{timespan}/{from_date}/{to_date}",
    response_model=StockDataResponse,
    summary="Get OHLC data for an index",
    description="Retrieve aggregated historical OHLC data for a specified index over a custom date range and time interval",
)
async def get_index_ohlc(
    indices_ticker: str = Path(..., description="The ticker symbol of the index (e.g., I:SPX, I:NDX)"),
    multiplier: int = Path(..., description="The size of the timespan multiplier"),
    timespan: str = Path(..., description="Time window size (minute, hour, day, week, month, quarter, year)"),
    from_date: str = Path(..., description="Start date in YYYY-MM-DD format"),
    to_date: str = Path(..., description="End date in YYYY-MM-DD format"),
    sort: SortOrder = Query(SortOrder.asc, description="Sort the results by timestamp"),
    limit: int = Query(5000, description="Limits the number of base aggregates queried", le=50000),
    api_key: str = Depends(get_api_key),
):
    """
    Get OHLC (Open, High, Low, Close) data for an index.
    
    Parameters:
    - indices_ticker: Index ticker symbol (e.g., I:SPX for S&P 500, I:NDX for Nasdaq-100)
    - multiplier: The size of the timespan multiplier
    - timespan: The size of the time window (minute, hour, day, etc.)
    - from_date: Start date in YYYY-MM-DD format
    - to_date: End date in YYYY-MM-DD format
    - sort: Sort order (asc or desc)
    - limit: Limit the number of results
    """
    # Validate the timespan
    if timespan not in [t.value for t in Timespan]:
        valid_timespans = ", ".join([t.value for t in Timespan])
        raise ValueError(f"Invalid timespan: {timespan}. Valid options are: {valid_timespans}")
    
    # Convert to Enum
    timespan_enum = Timespan(timespan)
    
    return await PolygonService.get_index_aggregates(
        indices_ticker=indices_ticker,
        multiplier=multiplier,
        timespan=timespan_enum,
        from_date=from_date,
        to_date=to_date,
        sort=sort,
        limit=limit
    )