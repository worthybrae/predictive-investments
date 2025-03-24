# api/models/stocks.py
from typing import Optional, List
from pydantic import BaseModel, Field

class OHLCData(BaseModel):
    """Individual OHLC data point."""
    c: float = Field(..., description="The close price for the symbol")
    h: float = Field(..., description="The highest price for the symbol")
    l: float = Field(..., description="The lowest price for the symbol")
    o: float = Field(..., description="The open price for the symbol")
    t: int = Field(..., description="Unix millisecond timestamp")
    v: Optional[float] = Field(None, description="Trading volume (may be None for indices)")
    vw: Optional[float] = Field(None, description="Volume weighted average price")
    n: Optional[int] = Field(None, description="Number of transactions")

class StockDataResponse(BaseModel):
    """Response model for stock OHLC data."""
    ticker: str
    adjusted: bool
    queryCount: int
    resultsCount: int
    status: str
    request_id: str
    results: Optional[List[OHLCData]] = None
    next_url: Optional[str] = None

class Address(BaseModel):
    """Company headquarters address details."""
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class Branding(BaseModel):
    """Company branding assets."""
    icon_url: Optional[str] = None
    logo_url: Optional[str] = None

class StockDetails(BaseModel):
    """Detailed information about a stock ticker."""
    active: bool = Field(..., description="Whether the asset is actively traded")
    address: Optional[Address] = None
    branding: Optional[Branding] = None
    cik: Optional[str] = Field(None, description="The CIK number for this ticker")
    composite_figi: Optional[str] = Field(None, description="The composite OpenFIGI number")
    currency_name: str = Field(..., description="The currency used for trading")
    currency_symbol: Optional[str] = Field(None, description="Currency symbol")
    base_currency_name: Optional[str] = Field(None, description="Base currency name for FX pairs")
    base_currency_symbol: Optional[str] = Field(None, description="Base currency symbol for FX pairs")
    delisted_utc: Optional[str] = Field(None, description="The last date asset was traded")
    description: Optional[str] = Field(None, description="Company description")
    homepage_url: Optional[str] = Field(None, description="Company website URL")
    list_date: Optional[str] = Field(None, description="Date first publicly listed (YYYY-MM-DD)")
    locale: str = Field(..., description="Locale of the asset (us, global)")
    market: str = Field(..., description="Market type (stocks, crypto, fx, otc, indices)")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    name: str = Field(..., description="Company or asset name")
    phone_number: Optional[str] = Field(None, description="Company phone number")
    primary_exchange: Optional[str] = Field(None, description="Primary listing exchange ISO code")
    round_lot: Optional[int] = Field(None, description="Round lot size")
    share_class_figi: Optional[str] = Field(None, description="Share class OpenFIGI number")
    share_class_shares_outstanding: Optional[float] = Field(None, description="Outstanding shares for this share class")
    sic_code: Optional[str] = Field(None, description="Standard industrial classification code")
    sic_description: Optional[str] = Field(None, description="SIC code description")
    ticker: str = Field(..., description="Trading symbol")
    ticker_root: Optional[str] = Field(None, description="Root of the ticker")
    ticker_suffix: Optional[str] = Field(None, description="Suffix of the ticker")
    total_employees: Optional[int] = Field(None, description="Approximate number of employees")
    type: Optional[str] = Field(None, description="Asset type")
    weighted_shares_outstanding: Optional[float] = Field(None, description="Weighted shares outstanding")
    
    # Added to support model validation from SDK objects
    class Config:
        # Enable extra fields so we don't lose data
        extra = "allow"
        # Allow converting SDK objects to this model
        arbitrary_types_allowed = True

class StockDetailsResponse(BaseModel):
    """Response model for stock ticker details."""
    request_id: Optional[str] = None
    results: Optional[StockDetails] = None
    status: Optional[str] = None

class Publisher(BaseModel):
    """News article publisher details."""
    favicon_url: Optional[str] = None
    homepage_url: Optional[str] = None
    logo_url: Optional[str] = None
    name: str

class NewsInsight(BaseModel):
    """Sentiment and reasoning for a news article."""
    sentiment: Optional[str] = None
    sentiment_reasoning: Optional[str] = None
    ticker: Optional[str] = None

class NewsArticle(BaseModel):
    """Individual news article."""
    amp_url: Optional[str] = None
    article_url: str
    author: str
    description: Optional[str] = None
    id: str
    image_url: Optional[str] = None
    insights: Optional[List[NewsInsight]] = None
    keywords: Optional[List[str]] = None
    published_utc: str
    publisher: Publisher
    tickers: List[str]
    title: str

class NewsResponse(BaseModel):
    """Response model for news articles."""
    count: Optional[int] = None
    next_url: Optional[str] = None
    request_id: Optional[str] = None
    results: Optional[List[NewsArticle]] = None
    status: Optional[str] = None