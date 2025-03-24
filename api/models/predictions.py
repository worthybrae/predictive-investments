# Updated api/models/predictions.py
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class PredictionStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    RESEARCHING = "researching"
    FINDING_TICKERS = "finding_tickers"
    CREATING_STRATEGY = "creating_strategy"
    COMPLETED = "completed"
    FAILED = "failed"

class PredictionStatusResponse(BaseModel):
    prediction_id: str = Field(..., description="Unique ID for the prediction")
    status: PredictionStatus = Field(..., description="Current status of the prediction")
    created_at: datetime = Field(..., description="Time when prediction was created")
    updated_at: datetime = Field(..., description="Time when status was last updated")
    message: Optional[str] = Field(None, description="Additional status message or error")
    progress: float = Field(0.0, description="Progress percentage (0-100)")
    result: Optional[Dict[str, Any]] = Field(None, description="Prediction results (if completed)")

class PredictionAnalysis(BaseModel):
    """Prediction analysis extraction model."""
    timing: str = Field(..., description="In how many days, months, or years the prediction will come true")
    confidence: float = Field(..., description="Confidence level (0.0-1.0 in 0.1 intervals)")
    tolerance: float = Field(..., description="Risk tolerance level (0.0-1.0 in 0.1 intervals)")
    related_industries: List[str] = Field(..., description="List of industries related to the prediction")
    name: str = Field(..., description="Short name summarizing the prediction (5 words or less)")
    category: str = Field(..., description="Type of prediction (e.g., climate, political, invention)")
    best_case_scenario: str = Field(..., description="Best case scenario (3 sentences)")
    worst_case_scenario: str = Field(..., description="Worst case scenario (3 sentences)")

class Trade(BaseModel):
    """Model for a single trade in an investment strategy."""
    ticker: str = Field(..., description="Stock ticker symbol")
    price: float = Field(..., description="Target price for the trade")
    volume: float = Field(..., description="Percentage of total capital to allocate to this trade")
    type: str = Field(..., description="Type of trade (buy, sell, option, etc.)")
    date: str = Field(..., description="Date of transaction (can be relative to current date)")

class InvestmentStrategy(BaseModel):
    """Investment strategy extraction model."""
    name: str = Field(..., description="Short name summarizing the strategy (5 words or less)")
    description: str = Field(..., description="Description of the strategy (3-5 sentences)")
    pros: List[str] = Field(..., description="Three benefits of the strategy")
    cons: List[str] = Field(..., description="Three drawbacks of the strategy")
    timing: str = Field(..., description="In how many days, months, or years the strategy will realize")
    risk: float = Field(..., description="Risk level (0.0-1.0 in 0.1 intervals)")
    estimated_return: float = Field(..., description="Estimated percentage return")
    involved_tickers: List[str] = Field(..., description="List of tickers involved in the strategy")
    trades: List[Trade] = Field(..., description="List of trades to execute")

class TickerQuery(BaseModel):
    """Model for finding relevant tickers based on prediction."""
    query: str = Field(..., description="Search query for finding relevant tickers")
    industries: List[str] = Field(..., description="List of industries to focus on")
    timeframe: str = Field(..., description="Relevant timeframe for the prediction")
    filters: Dict[str, str] = Field(..., description="Finviz filters to apply")
    
class RelevantTickers(BaseModel):
    """Response model with tickers relevant to a prediction."""
    tickers: List[str] = Field(..., description="List of relevant ticker symbols")


class EnhancedTickerRequest(BaseModel):
    """Request model for finding tickers with enhanced data."""
    prediction_text: str = Field(..., description="The prediction text to analyze")
    prediction_analysis: Optional[Dict[str, Any]] = Field(None, description="Optional pre-computed prediction analysis")
    use_web_search: bool = Field(False, description="Whether to enhance analysis with web search")
    search_model: str = Field("sonar", description="Perplexity model to use for web search")
    model: str = Field("gpt-4o-mini-mini", description="OpenAI model to use")
    include_stock_data: bool = Field(False, description="Whether to include OHLC and ticker details")
    include_year_data: bool = Field(False, description="Whether to include 1-year historical OHLC data")
    include_week_data: bool = Field(False, description="Whether to include 1-week hourly OHLC data")

class FilterSelection(BaseModel):
    """Model for Finviz filter selection."""
    selected_filters: List[str] = Field(..., description="List of selected filter IDs")
    reasoning: Dict[str, str] = Field(..., description="Explanation for each selected filter")

class FilterValueSelection(BaseModel):
    """Model for Finviz filter value selection."""
    filters: Dict[str, str] = Field(..., description="Mapping of filter names to selected option IDs")
    selections: Dict[str, str] = Field(..., description="Explanation for each filter value selection")