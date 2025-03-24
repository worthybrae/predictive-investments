# api/models/tickers.py
from typing import Optional, List
from pydantic import BaseModel, Field

class Ticker(BaseModel):
    """Individual ticker information."""
    ticker: str = Field(..., description="The ticker symbol")
    name: Optional[str] = Field(None, description="The name of the asset")
    market: str = Field(..., description="The market type (stocks, indices, crypto, fx, otc)")
    locale: str = Field(..., description="The locale of the asset (us, global)")
    active: bool = Field(..., description="Whether the asset is actively traded")
    currency_name: Optional[str] = Field(None, description="The name of the currency this asset trades in")
    last_updated_utc: Optional[str] = Field(None, description="When the ticker was last updated")
    primary_exchange: Optional[str] = Field(None, description="The primary exchange code")
    type: Optional[str] = Field(None, description="The asset type code")
    cik: Optional[str] = Field(None, description="The CIK number")
    composite_figi: Optional[str] = Field(None, description="The composite FIGI number")
    share_class_figi: Optional[str] = Field(None, description="The share class FIGI number")
    delisted_utc: Optional[str] = Field(None, description="When the asset was delisted, if applicable")
    source_feed: Optional[str] = Field(None, description="The data source for the ticker")
    
    class Config:
        # Allow extra fields
        extra = "allow"

class TickersResponse(BaseModel):
    """Response model for tickers listing."""
    count: Optional[int] = None
    next_url: Optional[str] = None
    request_id: Optional[str] = None
    results: Optional[List[Ticker]] = None
    status: Optional[str] = None

    class Config:
        # Allow extra fields
        extra = "allow"