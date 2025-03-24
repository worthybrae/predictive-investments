# api/processors/prediction.py
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from api.services.polygon import PolygonService
from api.models.enums import Timespan, SortOrder

logger = logging.getLogger(__name__)

class PredictionProcessor:
    """Class for processing prediction data and related operations."""
    
    @staticmethod
    async def get_stock_data(
        tickers: List[str],
        include_year_data: bool = False,
        include_week_data: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get stock data for a list of tickers.
        
        Args:
            tickers: List of ticker symbols
            include_year_data: Whether to include 1-year historical data
            include_week_data: Whether to include 1-week hourly data
            
        Returns:
            List of dictionaries with stock data
        """
        stock_data = []
        
        for ticker in tickers:
            try:
                # Get ticker details
                details_response = await PolygonService.get_ticker_details(ticker=ticker)
                
                if details_response.get("status") == "OK" and details_response.get("results"):
                    details = details_response["results"]
                    ticker_data = {
                        "ticker": ticker,
                        "name": details.get("name", ""),
                        "description": details.get("description", ""),
                        "market_cap": details.get("market_cap", None),
                        "website": details.get("homepage_url", ""),
                        "currency": details.get("currency_name", "USD"),
                        "exchange": details.get("primary_exchange", ""),
                        "ohlc": []
                    }
                    
                    # Get OHLC data if requested
                    if include_year_data:
                        yearly_data = await PredictionProcessor._get_yearly_data(ticker)
                        if yearly_data:
                            ticker_data["ohlc"].append(yearly_data)
                    
                    # Get 1-week hourly data
                    if include_week_data:
                        weekly_data = await PredictionProcessor._get_weekly_data(ticker)
                        if weekly_data:
                            ticker_data["ohlc"].append(weekly_data)
                    
                    stock_data.append(ticker_data)
            
            except Exception as e:
                logger.error(f"Error getting stock data for {ticker}: {str(e)}")
        
        return stock_data
    
    @staticmethod
    async def _get_yearly_data(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get 1-year daily OHLC data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with 1-year data summary
        """
        try:
            # Calculate date range for 1 year
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            
            ohlc_response = await PolygonService.get_stock_aggregates(
                ticker=ticker,
                multiplier=1,
                timespan=Timespan.day,
                from_date=start_date,
                to_date=end_date,
                adjusted=True,
                sort=SortOrder.desc,
                limit=365
            )
            
            if ohlc_response.get("status") == "OK" and ohlc_response.get("results"):
                yearly_data = ohlc_response["results"]
                
                if yearly_data:
                    # Get most recent price and calculate yearly metrics
                    current_price = yearly_data[0]["c"] if yearly_data else None
                    year_ago_price = yearly_data[-1]["c"] if len(yearly_data) > 1 else None
                    yearly_change = None
                    if current_price and year_ago_price:
                        yearly_change = ((current_price - year_ago_price) / year_ago_price) * 100
                    
                    return {
                        "timeframe": "1-year daily",
                        "current_price": current_price,
                        "yearly_change_pct": yearly_change,
                        "year_high": max([d["h"] for d in yearly_data]) if yearly_data else None,
                        "year_low": min([d["l"] for d in yearly_data]) if yearly_data else None,
                        "start_date": start_date,
                        "end_date": end_date
                    }
        
        except Exception as e:
            logger.error(f"Error getting yearly data for {ticker}: {str(e)}")
        
        return None
    
    @staticmethod
    async def _get_weekly_data(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get 1-week hourly OHLC data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with 1-week data summary
        """
        try:
            # Calculate date range for 1 week
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            ohlc_response = await PolygonService.get_stock_aggregates(
                ticker=ticker,
                multiplier=1,
                timespan=Timespan.hour,
                from_date=start_date,
                to_date=end_date,
                adjusted=True,
                sort=SortOrder.desc,
                limit=168  # 24 * 7 = 168 hours in a week
            )
            
            if ohlc_response.get("status") == "OK" and ohlc_response.get("results"):
                weekly_data = ohlc_response["results"]
                
                if weekly_data:
                    # Calculate weekly metrics
                    current_price = weekly_data[0]["c"] if weekly_data else None
                    week_ago_price = weekly_data[-1]["c"] if len(weekly_data) > 1 else None
                    weekly_change = None
                    if current_price and week_ago_price:
                        weekly_change = ((current_price - week_ago_price) / week_ago_price) * 100
                    
                    return {
                        "timeframe": "1-week hourly",
                        "current_price": current_price,
                        "weekly_change_pct": weekly_change,
                        "week_high": max([d["h"] for d in weekly_data]) if weekly_data else None,
                        "week_low": min([d["l"] for d in weekly_data]) if weekly_data else None,
                        "start_date": start_date,
                        "end_date": end_date
                    }
        
        except Exception as e:
            logger.error(f"Error getting weekly data for {ticker}: {str(e)}")
        
        return None
    
    @staticmethod
    def extract_tickers_from_result(result: Dict[str, Any]) -> List[str]:
        """
        Extract tickers from a ticker finder result.
        
        Args:
            result: The result from the ticker finder
            
        Returns:
            List of ticker symbols
        """
        if not result or "tickers" not in result:
            return []
        
        return result["tickers"]