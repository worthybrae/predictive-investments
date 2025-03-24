# api/services/finviz.py
import json
import asyncio
import re
from playwright.async_api import async_playwright
from typing import List, Dict, Any, Optional

class FinvizService:
    """Service for interacting with Finviz stock screener."""
    
    BASE_URL = "https://finviz.com/screener.ashx?v=111&ft=4"
    RESULTS_PER_PAGE = 20  # Finviz shows 20 results per page
    
    @classmethod
    async def _load_filters(cls) -> List[Dict[str, Any]]:
        """
        Load finviz filters from the JSON file.
        
        Returns:
            List of filter definitions
        """
        # Assume finviz.json is in the root directory
        try:
            with open("finviz.json", "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading finviz.json: {str(e)}")
            return []
    
    @classmethod
    def _build_url(cls, filters: Optional[Dict[str, str]] = None, page_offset: int = 0) -> str:
        """
        Build Finviz URL with specified filters and pagination.
        
        Args:
            filters: Dictionary of filter names and values
            page_offset: Row offset for pagination (0 for first page, 21 for second page, etc.)
            
        Returns:
            Complete Finviz URL with applied filters and pagination
        """
        # Start with the base URL
        url = cls.BASE_URL
        cleaned_filters = [f"{k}_{v}" for k, v in filters.items()]

        # Add filters if provided
        if cleaned_filters and len(cleaned_filters) > 0:
            filter_params = "%2C".join(cleaned_filters)
            url += f"&f={filter_params}"
        
        # Add pagination offset if not the first page
        if page_offset > 0:
            url += f"&r={page_offset + 1}"  # Finviz uses 1-based indexing
        
        return url
    
    @classmethod
    async def scrape_screener_results(cls, filters: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Scrape Finviz screener results based on provided filters using Playwright.
        Automatically handles pagination to get all results.
        
        Args:
            filters: Dictionary of filter names and values
            
        Returns:
            Dictionary with scraped data and metadata
        """
        all_results = []
        base_url = cls._build_url(filters)
        
        try:
            # Use Playwright to fetch and parse the page
            async with async_playwright() as p:
                # Launch a browser with a realistic user agent
                browser = await p.chromium.launch(headless=True)
                
                try:
                    # Create a context with more realistic settings
                    context = await browser.new_context(
                        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        viewport={"width": 1920, "height": 1080}
                    )
                    
                    # Open a new page
                    page = await context.new_page()
                    
                    # Initialize pagination variables
                    offset = 0
                    total_count = None
                    have_more_pages = True
                    page_number = 1
                    
                    while have_more_pages:
                        # Build URL for the current page

                        current_url = cls._build_url(filters, offset)
                        print(f"Fetching page {page_number} (offset {offset}): {current_url}")
                        
                        # Navigate to the URL and wait for the page to load
                        try:
                            await page.goto(current_url, wait_until="domcontentloaded", timeout=30000)
                            
                            # Wait a bit for any dynamic content to load
                            await asyncio.sleep(2)
                        except Exception as e:
                            print(f"Error navigating to page: {str(e)}")
                            if offset == 0:  # First page failed
                                return {
                                    "url": base_url,
                                    "success": False,
                                    "message": f"Navigation error: {str(e)}",
                                    "results": []
                                }
                            else:
                                # We've already got some data, break the loop
                                break
                        
                        # Check if the screener table exists
                        screener_table = await page.query_selector('tr#screener-table')
                        if not screener_table:
                            if offset == 0:  # First page failed
                                return {
                                    "url": base_url,
                                    "success": False,
                                    "message": "Screener table not found",
                                    "results": []
                                }
                            else:
                                # We've already got some data, break the loop
                                break
                        
                        # Extract all <a> elements with class "tab-link"
                        tab_links = await page.query_selector_all('tr#screener-table a.tab-link')
                        
                        # Extract the text from each link
                        page_results = []
                        for link in tab_links:
                            text = await link.inner_text()
                            page_results.append(text.strip())
                        
                        # Add results from this page to the overall results
                        all_results.extend(page_results)
                        
                        # Check if we need to fetch more pages
                        
                        # First, try to get the total count from the pagination text
                        if total_count is None:
                            pagination_text = await page.query_selector('div.screener-pages')
                            if pagination_text:
                                text = await pagination_text.inner_text()
                                count_match = re.search(r'Total: (\d+)', text)
                                if count_match:
                                    total_count = int(count_match.group(1))
                                    print(f"Total tickers found: {total_count}")
                        
                        # Check if we have all results based on the total count
                        if total_count is not None and len(all_results) >= total_count:
                            have_more_pages = False
                            print(f"Reached all {total_count} results. Stopping pagination.")
                        # Check if we got a full page of results (if we didn't, there are no more results)
                        elif len(page_results) < cls.RESULTS_PER_PAGE:
                            have_more_pages = False
                            print(f"Partial page with {len(page_results)} results. Stopping pagination.")
                        # Otherwise, move to the next page
                        else:
                            offset += cls.RESULTS_PER_PAGE
                            page_number += 1
                            
                            # Add a small delay to avoid hitting rate limits
                            await asyncio.sleep(1.5)
                    
                    # Return all the collected results
                    return {
                        "url": base_url,
                        "success": True,
                        "count": len(all_results),
                        "results": all_results
                    }
                    
                finally:
                    # Always close the browser
                    await browser.close()
                    
        except Exception as e:
            # If we already have some results, return those along with an error message
            if all_results:
                return {
                    "url": base_url,
                    "success": True,
                    "count": len(all_results),
                    "message": f"Partial results returned. Error: {str(e)}",
                    "results": all_results
                }
            else:
                return {
                    "url": base_url,
                    "success": False,
                    "message": f"Playwright error: {str(e)}",
                    "results": []
                }
            
    @classmethod
    async def get_available_filters(cls) -> Dict[str, Any]:
        """
        Get all available filters from the JSON file.
        
        Returns:
            Dictionary with filter definitions
        """
        filters = await cls._load_filters()
        
        # Convert to a more useful format
        result = {
            "count": len(filters),
            "filters": {}
        }
        
        for filter_def in filters:
            metric_name = filter_def.get("metric_name")
            if metric_name:
                result["filters"][metric_name] = {
                    "title": filter_def.get("metric_title", ""),
                    "description": filter_def.get("metric_description", "")
                }
        
        return result
    
    @classmethod
    async def get_filter_options(cls, selected_filters: List[str]) -> Dict[str, Any]:
        """
        Get all filter options from the JSON file.
        
        Args:
            selected_filters: List of filter names to get options for
            
        Returns:
            Dictionary with filter options
        """
        filters = await cls._load_filters()
        
        # Convert to a more useful format
        result = {
            "filters": {}
        }
        
        for filter_def in filters:
            metric_name = filter_def.get("metric_name")
            if metric_name in selected_filters:
                result["filters"][metric_name] = {
                    "title": filter_def.get("metric_title", ""),
                    "description": filter_def.get("metric_description", ""),
                    "options": filter_def.get("values", {})
                }
        
        return result