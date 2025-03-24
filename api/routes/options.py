# api/routes/options.py
from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
from models.options import OptionsContractsResponse, OptionsDataResponse
from models.enums import Timespan, SortOrder
from dependencies import get_api_key
from services.polygon import PolygonService

router = APIRouter(prefix="/options", tags=["options"])

@router.get(
    "/contracts",
    response_model=OptionsContractsResponse,
    summary="List options contracts",
    description="Retrieve a comprehensive index of options contracts, including both active and expired listings"
)
async def list_options_contracts(
    underlying_ticker: Optional[str] = Query(None, description="Query for contracts relating to an underlying stock ticker"),
    contract_type: Optional[str] = Query(None, description="Query by the type of contract (put, call)"),
    expiration_date: Optional[str] = Query(None, description="Query by contract expiration with date format YYYY-MM-DD"),
    as_of: Optional[str] = Query(None, description="Specify a point in time for contracts as of this date (YYYY-MM-DD)"),
    strike_price: Optional[float] = Query(None, description="Query by strike price of a contract"),
    expired: bool = Query(False, description="Query for expired contracts"),
    order: SortOrder = Query(SortOrder.asc, description="Order results based on the sort field"),
    limit: int = Query(10, description="Limit the number of results returned", ge=1, le=1000),
    sort: str = Query("ticker", description="Sort field used for ordering"),
    api_key: str = Depends(get_api_key),
):
    """
    List options contracts with various filters.
    
    Parameters:
    - underlying_ticker: Query contracts for a specific underlying stock 
    - contract_type: Filter by contract type (put, call)
    - expiration_date: Filter by expiration date
    - as_of: Specify contracts as of a specific date
    - strike_price: Filter by strike price
    - expired: Include expired contracts
    - order: Sort order (asc or desc)
    - limit: Limit the number of results
    - sort: Sort field to use
    """
    return await PolygonService.get_options_contracts(
        underlying_ticker=underlying_ticker,
        contract_type=contract_type,
        expiration_date=expiration_date,
        as_of=as_of,
        strike_price=strike_price,
        expired=expired,
        order=order.value,
        limit=limit,
        sort=sort
    )

@router.get(
    "/{options_ticker}/ohlc/{multiplier}/{timespan}/{from_date}/{to_date}",
    response_model=OptionsDataResponse,
    summary="Get OHLC data for an options contract",
    description="Retrieve aggregated historical OHLC data for a specified options contract over a custom date range and time interval"
)
async def get_options_ohlc(
    options_ticker: str = Path(..., description="The ticker symbol of the options contract"),
    multiplier: int = Path(..., description="The size of the timespan multiplier"),
    timespan: str = Path(..., description="Time window size (minute, hour, day, week, month, quarter, year)"),
    from_date: str = Path(..., description="Start date in YYYY-MM-DD format"),
    to_date: str = Path(..., description="End date in YYYY-MM-DD format"),
    adjusted: bool = Query(True, description="Whether or not the results are adjusted for splits"),
    sort: SortOrder = Query(SortOrder.asc, description="Sort the results by timestamp"),
    limit: int = Query(120, description="Limits the number of base aggregates queried", le=50000),
    api_key: str = Depends(get_api_key),
):
    """
    Get OHLC (Open, High, Low, Close) data for an options contract.
    
    Parameters:
    - options_ticker: Options contract ticker symbol (e.g., O:SPY251219C00650000)
    - multiplier: The size of the timespan multiplier
    - timespan: The size of the time window (minute, hour, day, etc.)
    - from_date: Start date in YYYY-MM-DD format
    - to_date: End date in YYYY-MM-DD format
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
    
    return await PolygonService.get_options_aggregates(
        options_ticker=options_ticker,
        multiplier=multiplier,
        timespan=timespan_enum,
        from_date=from_date,
        to_date=to_date,
        adjusted=adjusted,
        sort=sort,
        limit=limit
    )