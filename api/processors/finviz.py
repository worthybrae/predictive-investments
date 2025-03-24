# api/processors/finviz.py
import logging
from typing import Dict, Any, List

from api.services.finviz import FinvizService

logger = logging.getLogger(__name__)

class FinvizProcessor:
    """Class for processing Finviz screener data and operations."""
    
    @staticmethod
    async def get_filter_info() -> List[Dict[str, Any]]:
        """
        Get available filters from Finviz and format them for use in prompts.
        
        Returns:
            List of dictionaries with filter info
        """
        try:
            # Get available filters from Finviz
            available_filters = await FinvizService.get_available_filters()
            
            if not available_filters or "filters" not in available_filters:
                logger.error("Failed to get available Finviz filters")
                return []
            
            # Prepare filter information for the prompt with human-readable descriptions
            filter_info = []
            for name, info in available_filters["filters"].items():
                filter_info.append({
                    "id": name,  # Store the internal ID
                    "name": info.get("title", ""),  # Use the human-readable name
                    "description": info.get("description", "")
                })
            
            return filter_info
            
        except Exception as e:
            logger.exception(f"Error getting filter info: {str(e)}")
            return []
    
    @staticmethod
    async def get_filter_options(selected_filters: List[str]) -> Dict[str, Any]:
        """
        Get options for selected filters and format them for use in prompts.
        
        Args:
            selected_filters: List of filter names
            
        Returns:
            Dictionary with filter options
        """
        try:
            # Get options for the selected filters
            filter_options_result = await FinvizService.get_filter_options(selected_filters)
            
            if not filter_options_result or "filters" not in filter_options_result:
                logger.error("Failed to get Finviz filter options")
                return {}
            
            # Restructure filter options to be more human-readable
            filter_options_formatted = {}
            for filter_name, filter_data in filter_options_result["filters"].items():
                # Prepare human-readable option information
                option_info = []
                for option_id, option_display_name in filter_data.get("options", {}).items():
                    # For some filters, the option ID might be the same as the filter name + underscore + value
                    # Extract just the value part for better readability
                    if option_id.startswith(f"{filter_name}_"):
                        value_id = option_id[len(filter_name)+1:]
                    else:
                        value_id = option_id
                    
                    option_info.append({
                        "id": option_id,  # Keep the full ID for reference
                        "value": value_id,  # The value part
                        "display_name": option_display_name  # The human-readable name
                    })
                
                filter_options_formatted[filter_name] = {
                    "title": filter_data.get("title", ""),
                    "description": filter_data.get("description", ""),
                    "options": option_info
                }
            
            return filter_options_formatted
            
        except Exception as e:
            logger.exception(f"Error getting filter options: {str(e)}")
            return {}
    
    @staticmethod
    async def run_screener(filters: Dict[str, str]) -> List[str]:
        """
        Run the Finviz screener with the given filters.
        
        Args:
            filters: Dictionary of filter name-value pairs
            
        Returns:
            List of tickers from the screener results
        """
        try:
            screener_result = await FinvizService.scrape_screener_results(filters)
            
            if not screener_result or not screener_result.get("success"):
                logger.error(f"Failed to run screener: {screener_result.get('message', 'Unknown error')}")
                return []
            
            return screener_result.get("results", [])
            
        except Exception as e:
            logger.exception(f"Error running screener: {str(e)}")
            return []