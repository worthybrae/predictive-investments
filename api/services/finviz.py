# api/services/finviz.py
import json
import asyncio
from playwright.async_api import async_playwright
from typing import List, Dict, Any, Optional

class FinvizService:
    """Service for interacting with Finviz stock screener."""
    
    BASE_URL = "https://finviz.com/screener.ashx?v=111&ft=4"
    
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
    def _build_url(cls, filters: Optional[Dict[str, str]] = None) -> str:
        """
        Build Finviz URL with specified filters.
        
        Args:
            filters: Dictionary of filter names and values
            
        Returns:
            Complete Finviz URL with applied filters
        """
        if not filters or len(filters) == 0:
            return cls.BASE_URL
            
        # Start with the base URL
        url = f"{cls.BASE_URL}&f="
        
        # Add filters separated by %2C (URL encoded comma)
        filter_params = "%2C".join(filters.values())
        url += filter_params
        
        return url
    
    @classmethod
    async def scrape_screener_results(cls, filters: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Scrape Finviz screener results based on provided filters using Playwright.
        
        Args:
            filters: Dictionary of filter names and values
            
        Returns:
            Dictionary with scraped data and metadata
        """
        # Build the URL with filters
        url = cls._build_url(filters)
        
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
                    
                    # Navigate to the URL and wait for the page to load
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        
                        # Wait a bit for any dynamic content to load
                        await asyncio.sleep(2)
                        
                        # Check if the screener table exists
                        screener_table = await page.query_selector('tr#screener-table')
                        if not screener_table:
                            return {
                                "url": url,
                                "success": False,
                                "message": "Screener table not found",
                                "results": []
                            }
                        
                        # Extract all <a> elements with class "tab-link"
                        tab_links = await page.query_selector_all('tr#screener-table a.tab-link')
                        
                        # Extract the text from each link
                        results = []
                        for link in tab_links:
                            text = await link.inner_text()
                            results.append(text.strip())
                        
                        return {
                            "url": url,
                            "success": True,
                            "count": len(results),
                            "results": results
                        }
                        
                    except Exception as e:
                        return {
                            "url": url,
                            "success": False,
                            "message": f"Navigation or parsing error: {str(e)}",
                            "results": []
                        }
                        
                finally:
                    # Always close the browser
                    await browser.close()
                    
        except Exception as e:
            return {
                "url": url,
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
    async def get_filter_options(cls, selected_filters) -> Dict[str, Any]:
        """
        Get all filter options from the JSON file.
        
        Returns:
            Dictionary with filter definitions
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