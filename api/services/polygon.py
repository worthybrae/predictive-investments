# api/services/polygon.py
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from polygon import RESTClient
from api.models.enums import Timespan, SortOrder
from api.core.exceptions import PolygonAPIException

load_dotenv()

class PolygonService:
    """Service for interacting with the Polygon.io API using the official SDK."""
    
    @classmethod
    async def get_stock_aggregates(
        cls,
        ticker: str,
        multiplier: int,
        timespan: Timespan,
        from_date: str,
        to_date: str,
        adjusted: bool = True,
        sort: SortOrder = SortOrder.asc,
        limit: int = 5000
    ) -> Dict[str, Any]:
        """
        Get aggregated OHLC data for a stock using the Polygon SDK.
        
        Args:
            ticker: Stock ticker symbol
            multiplier: Timespan multiplier
            timespan: The size of the time window
            from_date: Start date (YYYY-MM-DD or millisecond timestamp)
            to_date: End date (YYYY-MM-DD or millisecond timestamp)
            adjusted: Whether results are adjusted for splits
            sort: Sort order (asc or desc)
            limit: Maximum number of results
            
        Returns:
            API response with OHLC data
        """
        try:
            # Create a client with the API key
            client = RESTClient(os.getenv('POLYGON_API_KEY'))
            
            # Use the SDK to fetch aggregates
            aggs = []
            for a in client.list_aggs(
                ticker=ticker,
                multiplier=multiplier,
                timespan=timespan.value,
                from_=from_date,
                to=to_date,
                adjusted=str(adjusted).lower(),
                sort=sort.value,
                limit=limit
            ):
                aggs.append({
                    "c": a.close,
                    "h": a.high,
                    "l": a.low,
                    "o": a.open,
                    "t": a.timestamp,
                    "v": a.volume,
                    "vw": getattr(a, "vw", None),
                    "n": getattr(a, "transactions", None)
                })
            
            # Format the response to match your model
            response = {
                "ticker": ticker,
                "adjusted": adjusted,
                "queryCount": len(aggs),
                "resultsCount": len(aggs),
                "status": "OK",
                "request_id": "sdk_request",
                "results": aggs,
                "next_url": None
            }
            
            return response
            
        except Exception as e:
            raise PolygonAPIException(detail=f"Polygon API error: {str(e)}")
    
    @classmethod
    async def get_ticker_details(
        cls,
        ticker: str,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive details for a single ticker.
        
        Args:
            ticker: Stock ticker symbol
            date: Optional date to get historical info (YYYY-MM-DD)
            
        Returns:
            API response with ticker details
        """
        try:
            # Create a client with the API key
            client = RESTClient(os.getenv('POLYGON_API_KEY'))
            
            # Use the SDK to fetch ticker details
            details = client.get_ticker_details(
                ticker=ticker,
                date=date
            )
            
            # Convert the TickerDetails object to a dictionary
            details_dict = {}
            if hasattr(details, "__dict__"):
                # Convert attributes
                for key, value in details.__dict__.items():
                    # For nested objects like address and branding
                    if hasattr(value, "__dict__"):
                        details_dict[key] = value.__dict__
                    else:
                        details_dict[key] = value
            else:
                # If it's already a dict-like structure
                details_dict = details
            
            # Format the response to match our StockDetailsResponse model structure
            response = {
                "request_id": "sdk_request",
                "status": "OK",
                "results": details_dict
            }
            
            return response
            
        except Exception as e:
            raise PolygonAPIException(detail=f"Polygon API error: {str(e)}")
        
    @classmethod
    async def get_ticker_news(
        cls,
        ticker: Optional[str] = None,
        published_utc: Optional[str] = None,
        order: str = "desc",
        limit: int = 10,
        sort: str = "published_utc"
    ) -> Dict[str, Any]:
        """
        Get news articles for a specified ticker using the Polygon SDK.
        
        Args:
            ticker: Optional stock ticker symbol
            published_utc: Optional publish date for filtering
            order: Sort order (asc or desc)
            limit: Maximum number of results (max 1000)
            sort: Field to sort results by
            
        Returns:
            API response with news articles
        """
        import time
        import random
        
        # Maximum number of retries for rate limit errors
        max_retries = 3
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                # Create a client with the API key
                client = RESTClient(os.getenv('POLYGON_API_KEY'))
                
                # Collect all parameters
                # The SDK expects string values, not integers
                params = {}
                if ticker:
                    params["ticker"] = ticker
                if published_utc:
                    params["published_utc"] = published_utc
                params["order"] = order
                params["limit"] = str(limit)  # Convert limit to string as the SDK expects
                params["sort"] = sort
                
                # First attempt: Try to get the raw REST API response
                # Some SDK versions have a method for this
                try:
                    # Using _get to access the raw response data
                    # This makes a single request rather than using the iterator
                    url_path = "/v2/reference/news"
                    raw_response = client._get(url_path, params)
                    return raw_response
                except (AttributeError, TypeError) as e:
                    # Fall back to using the iterator but limit to one request
                    print(f"Direct API call failed, using iterator: {str(e)}")
                    pass
                
                # If we can't get the raw response, use the iterator but collect only once
                news_items = []
                iterator = client.list_ticker_news(**params)
                
                # Instead of iterating through the generator which could make multiple requests,
                # store the results from the initial request
                for i, news in enumerate(iterator):
                    # Convert news item to a dictionary
                    news_dict = {}
                    for key, value in vars(news).items():
                        if key.startswith('_'):
                            continue
                        
                        # Handle nested objects
                        if key == "publisher" and hasattr(value, "__dict__"):
                            news_dict[key] = {}
                            for k, v in vars(value).items():
                                if not k.startswith('_'):
                                    news_dict[key][k] = v
                        elif key == "insights" and isinstance(value, list):
                            insights = []
                            for insight in value:
                                if hasattr(insight, "__dict__"):
                                    insight_dict = {}
                                    for k, v in vars(insight).items():
                                        if not k.startswith('_'):
                                            insight_dict[k] = v
                                    insights.append(insight_dict)
                            news_dict[key] = insights
                        else:
                            news_dict[key] = value
                    
                    news_items.append(news_dict)
                    
                    # Break after first batch to prevent multiple API calls
                    # We should get up to 'limit' items in the first request
                    if i + 1 >= limit:
                        break
                
                # Stop after the first request regardless of how many items were returned
                # This prevents multiple API calls
                
                # Construct response format matching the API
                response = {
                    "count": len(news_items),
                    "next_url": None,  # We don't have this info from the iterator
                    "request_id": "sdk_request",
                    "results": news_items,
                    "status": "OK"
                }
                
                return response
                
            except Exception as e:
                # Check if this is a rate limit error (429)
                error_str = str(e)
                if "429" in error_str and retry_count < max_retries:
                    retry_count += 1
                    
                    # Exponential backoff with jitter
                    backoff_time = (2 ** retry_count) + random.uniform(0, 1)
                    print(f"Rate limit hit. Retrying in {backoff_time:.2f} seconds...")
                    time.sleep(backoff_time)
                    continue
                else:
                    # Other error or max retries exceeded
                    raise PolygonAPIException(detail=f"Polygon API news error: {str(e)}")
                
    @classmethod
    async def get_options_contracts(
        cls,
        underlying_ticker: Optional[str] = None,
        contract_type: Optional[str] = None,
        expiration_date: Optional[str] = None,
        as_of: Optional[str] = None,
        strike_price: Optional[float] = None,
        expired: bool = False,
        order: str = "asc",
        limit: int = 10,
        sort: str = "ticker"
    ) -> Dict[str, Any]:
        """
        Get options contracts data using the Polygon SDK.
        
        Args:
            underlying_ticker: Query for contracts relating to an underlying stock ticker
            contract_type: Query by the type of contract
            expiration_date: Query by contract expiration date (YYYY-MM-DD)
            as_of: Specify a point in time for contracts as of this date
            strike_price: Query by strike price
            expired: Query for expired contracts
            order: Sort order (asc or desc)
            limit: Maximum number of results
            sort: Field to sort results by
            
        Returns:
            API response with options contracts data
        """
        try:
            # Create a client with the API key
            client = RESTClient(os.getenv('POLYGON_API_KEY'))
            
            # Build parameters dictionary
            params = {}
            if underlying_ticker:
                params["underlying_ticker"] = underlying_ticker
            if contract_type:
                params["contract_type"] = contract_type
            if expiration_date:
                params["expiration_date"] = expiration_date
            if as_of:
                params["as_of"] = as_of
            if strike_price:
                params["strike_price"] = strike_price
            if expired:
                params["expired"] = str(expired).lower()
            
            params["order"] = order
            params["limit"] = limit
            params["sort"] = sort
            
            # Try to get the raw response from the API
            try:
                url_path = "/v3/reference/options/contracts"
                raw_response = client._get(url_path, params)
                return raw_response
            except (AttributeError, TypeError):
                # Fall back to using the iterator method
                pass
            
            # Use the SDK to list options contracts
            contracts = []
            for contract in client.list_options_contracts(**params):
                # Convert contract object to dictionary
                contract_dict = {}
                for key, value in vars(contract).items():
                    if key.startswith('_'):
                        continue
                        
                    # Handle nested objects like additional_underlyings
                    if key == "additional_underlyings" and isinstance(value, list):
                        underlyings = []
                        for underlying in value:
                            if hasattr(underlying, "__dict__"):
                                underlying_dict = {}
                                for k, v in vars(underlying).items():
                                    if not k.startswith('_'):
                                        underlying_dict[k] = v
                                underlyings.append(underlying_dict)
                        contract_dict[key] = underlyings
                    else:
                        contract_dict[key] = value
                        
                contracts.append(contract_dict)
                
                # Limit to requested number of contracts
                if len(contracts) >= limit:
                    break
            
            # Format the response to match our model
            response = {
                "request_id": "sdk_request",
                "results": contracts,
                "status": "OK",
                "next_url": None
            }
            
            return response
            
        except Exception as e:
            raise PolygonAPIException(detail=f"Polygon API error: {str(e)}")

    @classmethod
    async def get_options_aggregates(
        cls,
        options_ticker: str,
        multiplier: int,
        timespan: Timespan,
        from_date: str,
        to_date: str,
        adjusted: bool = True,
        sort: SortOrder = SortOrder.asc,
        limit: int = 120
    ) -> Dict[str, Any]:
        try:
            # Create a client with the API key
            client = RESTClient(os.getenv('POLYGON_API_KEY'))
            
            # Skip the direct API call attempt and only use the SDK
            aggs = []
            for a in client.list_aggs(
                ticker=options_ticker,
                multiplier=multiplier,
                timespan=timespan.value,
                from_=from_date,
                to=to_date,
                adjusted=str(adjusted).lower(),
                sort=sort.value,
                limit=limit
            ):
                aggs.append({
                    "c": a.close,
                    "h": a.high,
                    "l": a.low,
                    "o": a.open,
                    "t": a.timestamp,
                    "v": a.volume,
                    "vw": getattr(a, "vw", None),
                    "n": getattr(a, "transactions", None)
                })
            
            # Format the response to match Polygon's API structure
            response = {
                "ticker": options_ticker,
                "adjusted": adjusted,
                "queryCount": limit,  # Use the requested limit for consistency with Polygon
                "resultsCount": len(aggs),  # Use the actual count of results
                "status": "DELAYED" if len(aggs) > 0 else "OK",  # Match Polygon status pattern
                "request_id": "sdk_request",
                "results": aggs if len(aggs) > 0 else None,  # Use None instead of empty list
                "next_url": None
            }
            
            return response
            
        except Exception as e:
            # Log the full exception for debugging
            import traceback
            print(f"Error in get_options_aggregates: {str(e)}")
            print(traceback.format_exc())
            raise PolygonAPIException(detail=f"Polygon API error: {str(e)}")

    @classmethod
    async def list_tickers(
        cls,
        market: Optional[str] = None,
        search: Optional[str] = None,
        active: bool = True,
        order: str = "asc",
        limit: int = 100,
        sort: str = "ticker"
    ) -> Dict[str, Any]:
        """
        Get a list of tickers using the Polygon SDK.
        
        Args:
            market: Filter by market type (stocks, indices, crypto, fx, otc)
            search: Search term to filter tickers by name or symbol
            active: Filter to only active tickers
            order: Sort order (asc or desc)
            limit: Maximum number of results
            sort: Field to sort results by
            
        Returns:
            API response with ticker data
        """
        try:
            # Create a client with the API key
            client = RESTClient(os.getenv('POLYGON_API_KEY'))
            
            # Build parameters dictionary
            params = {}
            if market:
                params["market"] = market
            if search:
                params["search"] = search
            
            params["active"] = str(active).lower()
            params["order"] = order
            params["limit"] = str(limit)  # SDK expects string
            params["sort"] = sort
            
            # Try to get the raw response from the API
            try:
                url_path = "/v3/reference/tickers"
                raw_response = client._get(url_path, params)
                return raw_response
            except (AttributeError, TypeError):
                # Fall back to using the iterator method
                pass
            
            # Use the SDK's list_tickers method as fallback
            tickers = []
            for ticker in client.list_tickers(**params):
                # Convert ticker object to dictionary
                ticker_dict = {}
                for key, value in vars(ticker).items():
                    if key.startswith('_'):
                        continue
                    ticker_dict[key] = value
                
                tickers.append(ticker_dict)
                
                # Limit to requested number of tickers
                if len(tickers) >= limit:
                    break
            
            # Format the response to match our model
            response = {
                "count": len(tickers),
                "request_id": "sdk_request",
                "results": tickers,
                "status": "OK",
                "next_url": None
            }
            
            return response
            
        except Exception as e:
            raise PolygonAPIException(detail=f"Polygon API error: {str(e)}")
            
    @classmethod
    async def get_index_aggregates(
        cls,
        indices_ticker: str,
        multiplier: int,
        timespan: Timespan,
        from_date: str,
        to_date: str,
        sort: SortOrder = SortOrder.asc,
        limit: int = 5000
    ) -> Dict[str, Any]:
        """
        Get aggregated OHLC data for an index using the Polygon SDK.
        
        Args:
            indices_ticker: Index ticker symbol (e.g., I:SPX, I:NDX)
            multiplier: Timespan multiplier
            timespan: The size of the time window
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            sort: Sort order (asc or desc)
            limit: Maximum number of results
            
        Returns:
            API response with OHLC data for the index
        """
        try:
            # Create a client with the API key
            client = RESTClient(os.getenv('POLYGON_API_KEY'))
            
            # Use the SDK to fetch aggregates
            aggs = []
            for a in client.list_aggs(
                ticker=indices_ticker,
                multiplier=multiplier,
                timespan=timespan.value,
                from_=from_date,
                to=to_date,
                sort=sort.value,
                limit=limit
            ):
                # Create aggregate data point
                agg_data = {
                    "c": a.close,
                    "h": a.high,
                    "l": a.low,
                    "o": a.open,
                    "t": a.timestamp
                }
                
                # Only include volume if it exists
                volume = getattr(a, "volume", None)
                if volume is not None:
                    agg_data["v"] = volume
                
                aggs.append(agg_data)
            
            # Format the response to match your model
            response = {
                "ticker": indices_ticker,
                "adjusted": False,  # Indices don't have adjusted values
                "queryCount": len(aggs),
                "resultsCount": len(aggs),
                "status": "OK",
                "request_id": "sdk_request",
                "results": aggs,
                "next_url": None
            }
            
            return response
            
        except Exception as e:
            raise PolygonAPIException(detail=f"Polygon API error: {str(e)}")