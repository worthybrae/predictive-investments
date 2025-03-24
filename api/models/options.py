# api/models/options.py
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from enum import Enum

class ExerciseStyle(str, Enum):
    """Option exercise style."""
    american = "american"
    european = "european" 
    bermudan = "bermudan"

class ContractType(str, Enum):
    """Option contract type."""
    call = "call"
    put = "put"
    other = "other"

class AdditionalUnderlying(BaseModel):
    """Additional underlying or deliverable for an option contract."""
    type: str
    underlying: str
    amount: float

class OptionContract(BaseModel):
    """Options contract details."""
    cfi: Optional[str] = Field(None, description="The 6 letter CFI code of the contract (defined in ISO 10962)")
    contract_type: Optional[ContractType] = Field(None, description="The type of contract (put or call)")
    correction: Optional[int] = Field(None, description="The correction number for this option contract")
    exercise_style: Optional[ExerciseStyle] = Field(None, description="The exercise style of this contract")
    expiration_date: Optional[str] = Field(None, description="The contract's expiration date in YYYY-MM-DD format")
    primary_exchange: Optional[str] = Field(None, description="The MIC code of the primary exchange")
    shares_per_contract: Optional[float] = Field(None, description="The number of shares per contract")
    strike_price: Optional[float] = Field(None, description="The strike price of the option contract")
    ticker: Optional[str] = Field(None, description="The ticker for the option contract")
    underlying_ticker: Optional[str] = Field(None, description="The underlying ticker that the option contract relates to")
    additional_underlyings: Optional[List[AdditionalUnderlying]] = Field(None, description="Additional underlyings or deliverables")

class OptionsContractsResponse(BaseModel):
    """Response model for options contracts listing."""
    next_url: Optional[str] = None
    request_id: Optional[str] = None
    results: Optional[List[OptionContract]] = None
    status: Optional[str] = None

class OptionsDataResponse(BaseModel):
    """Response model for options OHLC data."""
    ticker: str
    adjusted: bool
    queryCount: int
    resultsCount: int
    status: str
    request_id: str
    results: Optional[List[Any]] = None
    next_url: Optional[str] = None