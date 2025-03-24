# api/models/finviz.py
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ScreenerRequest(BaseModel):
    """Request model for the finviz screener endpoint."""
    filters: Optional[Dict[str, str]] = Field(
        None, 
        description="Dictionary of filter names and their values (e.g., {'index': 'idx_sp500', 'sector': 'sec_technology'})"
    )

class ScreenerResponse(BaseModel):
    """Response model for the finviz screener endpoint."""
    url: str = Field(..., description="The URL that was scraped")
    success: bool = Field(..., description="Whether the scraping was successful")
    count: Optional[int] = Field(None, description="Number of results found")
    message: Optional[str] = Field(None, description="Error message if scraping failed")
    results: List[str] = Field(..., description="List of ticker symbols from the screener")

class FilterOption(BaseModel):
    """Model for a single filter option."""
    title: str = Field(..., description="Display title of the filter")
    description: str = Field(..., description="Description of the filter")

class FullOption(BaseModel):
    """Model for a full filter option."""
    title: str = Field(..., description="Display title of the filter")
    description: str = Field(..., description="Description of the filter")
    options: Dict[str, str] = Field(..., description="Available options for this filter")

class FiltersResponse(BaseModel):
    """Response model for the available filters endpoint."""
    count: int = Field(..., description="Number of available filters")
    filters: Dict[str, FilterOption] = Field(..., description="Dictionary of available filters")

class OptionResponse(BaseModel):
    """Response model for the available option endpoint."""
    filters: Dict[str, FullOption] = Field(..., description="Dictionary of options")

class OptionRequest(BaseModel):
    filters: List[str] = Field(..., description="List of selected filters to get options for")