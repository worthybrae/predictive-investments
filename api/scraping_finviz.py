import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import re
import html
import json

async def extract_description_from_boxover(boxover_text):
    """
    Extract and clean the description from a boxover attribute.
    """
    try:
        # Debug: Print the raw boxover text to help understand its structure
        print("Raw boxover text:", boxover_text)
        
        # Extract the entire body content in a single pattern with non-greedy matching
        tab_match = re.search(r"body=\[.*?class='tooltip_tab'>(.*?)</td>", boxover_text, re.DOTALL)
        if tab_match:
            description = tab_match.group(1)
            print("Raw description text:", description)
            
            # Clean HTML entities
            description = html.unescape(description)
            # Remove any remaining HTML tags
            description = re.sub(r'<.*?>', ' ', description)
            # Clean up extra spaces
            description = re.sub(r'\s+', ' ', description).strip()
            print("Cleaned description:", description)
            return description
        else:
            print("No tooltip_tab pattern match found")
            
            # Try a more relaxed pattern as fallback
            body_text = re.search(r'body=\[(.*?)\]', boxover_text, re.DOTALL)
            if body_text:
                print("Found body text, trying alternate extraction")
                # Try to find any text content inside the body
                text_content = re.sub(r'<[^>]*>', ' ', body_text.group(1))
                text_content = html.unescape(text_content)
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                if text_content and len(text_content) > 5:  # Require some minimum content
                    print("Extracted alternate description:", text_content)
                    return text_content
                    
    except Exception as e:
        print(f"Error extracting description: {e}")
    
    return "No description available"

async def extract_header_from_boxover(boxover_text):
    """
    Extract the header (metric name) from a boxover attribute.
    """
    try:
        # Extract text between header=[ and ]
        header_match = re.search(r'header=\[(.*?)\]', boxover_text)
        if header_match:
            header = header_match.group(1)
            # Clean HTML entities
            header = html.unescape(header)
            # Remove any remaining HTML tags
            header = re.sub(r'<.*?>', ' ', header)
            # Clean up extra spaces
            header = re.sub(r'\s+', ' ', header).strip()
            return header
    except Exception as e:
        print(f"Error extracting header: {e}")
    
    return "No header available"

async def process_metric_cell(span, select, output_file):
    """
    Process a metric cell with its span (containing description) and select (containing options).
    Prompt the user whether to include this metric.
    """
    # Get metric information
    metric_title = await span.inner_text()
    boxover_text = await span.get_attribute('data-boxover')
    
    # Get metric ID from select
    select_id = await select.get_attribute('id')
    metric_id = select_id.replace('fs_', '')
    
    # Extract description and header
    description = await extract_description_from_boxover(boxover_text)
    
    # Prompt user
    print("\n" + "="*50)
    print(f"METRIC: {metric_title} ({metric_id})")
    print(f"DESCRIPTION: {description}")
    user_input = input("Include this metric? (y/n): ").strip().lower()
    
    if user_input == 'y':
        # Write to file
        data = {
            "metric_name": metric_id,
            "metric_title": metric_title,
            "metric_description": description,
            "values": {}
        }
        
        # Get and write all options
        options = await select.query_selector_all('option')
        if options:
            for option in options:
                option_value = await option.get_attribute('value')
                option_text = await option.inner_text()
                data["values"][f"{metric_id}_{option_value}"] = option_text
        
        return data
    else:
        print(f"Skipping metric: {metric_title}")
        return {}

async def scrape_url(page, url, output_file):
    """
    Scrape a specific FinViz URL for filter table data and write to output file.
    """
    output_file.write(f"\n--- Navigating to {url} ---\n")
    print(f"\n--- Navigating to {url} ---")
    
    try:
        # Try with domcontentloaded which is faster
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        print("Page loaded (domcontentloaded).")
    except Exception as e:
        print(f"Initial navigation failed: {e}")
        print("Trying again with a different strategy...")
        try:
            # If that fails, try with a direct navigation and wait for load event
            await page.goto(url, wait_until="load", timeout=90000)
            print("Page loaded (load event).")
        except Exception as e:
            print(f"Navigation failed again: {e}")
            print("Continuing anyway to see if we can extract data...")
    
    # Wait a moment for any scripts to initialize
    await asyncio.sleep(5)
    
    # Check if we can find the table
    filter_table = await page.query_selector('#filter-table-filters')
    if not filter_table:
        print("Could not find the table with id 'filter-table-filters'")
        print("Taking a screenshot for debugging...")
        
        screenshot_filename = f"finviz_debug_{url.split('=')[-1].replace('&', '_')}.png"
        await page.screenshot(path=screenshot_filename)
        
        print(f"Screenshot saved as {screenshot_filename}")
        print("Check if there's a CAPTCHA or other blocking mechanism")
        return False
    
    # Find all rows in the table
    rows = await filter_table.query_selector_all('tr')
    metrics_processed = 0
    
    # Process each row
    filters = []
    for row in rows:
        # Find all cells in the row
        cells = await row.query_selector_all('td')
        
        # Process cells in pairs (description cell followed by select cell)
        i = 0
        while i < len(cells) - 1:
            title_cell = cells[i]
            select_cell = cells[i + 1]
            
            # Check if this is a title cell (with span.screener-combo-title)
            span = await title_cell.query_selector('span.screener-combo-title')
            if not span:
                i += 1
                continue
            
            # Check if the next cell has a select element
            select = await select_cell.query_selector('select')
            if not select:
                i += 1
                continue
            
            # Process this metric
            included = await process_metric_cell(span, select, output_file)
            if included:
                filters.append(included)
                metrics_processed += 1
            
            # Move to the next pair
            i += 2
    
    
    print(f"\nProcessed {metrics_processed} metrics from {url}")
    with open("data.json", "w") as f:
        json.dump(filters, f, indent=4)
    return True

async def scrape_filter_tables():
    """
    Scrape the filter-table-filters from multiple FinViz URLs using Playwright.
    """
    # URLs to scrape
    urls = [
        "https://finviz.com/screener.ashx?v=111&ft=4"
    ]
    
    # Create output file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"finviz_metrics_{timestamp}.txt"
    
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        output_file.write(f"FinViz Filter Metrics - Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output_file.write("=" * 80 + "\n\n")
        output_file.write("FORMAT: METRIC_ID_VALUE: DISPLAY_TEXT\n\n")
        
        print(f"Output will be saved to: {output_filename}")
        print("Starting to scrape FinViz filter tables with Playwright...")
        
        async with async_playwright() as p:
            # Launch a browser with a viewport that looks more like a real browser
            browser = await p.chromium.launch(headless=False)  # Set to False to see what's happening
            
            try:
                # Create a new context with a more realistic user agent
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    viewport={"width": 1280, "height": 800}
                )
                
                # Create a new page
                page = await context.new_page()
                
                # Process each URL sequentially
                for url in urls:
                    success = await scrape_url(page, url, output_file)
                    if not success:
                        output_file.write(f"Failed to process {url}, moving to next URL\n\n")
                        print(f"Failed to process {url}, moving to next URL")
                    # Wait a bit between URLs to avoid rate limiting
                    await asyncio.sleep(3)
            
            except Exception as e:
                error_msg = f"An error occurred: {e}"
                output_file.write(f"{error_msg}\n")
                print(error_msg)
            
            finally:
                # Always close the browser
                await browser.close()
        
        output_file.write("\n" + "=" * 80 + "\n")
        output_file.write(f"Scraping completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\nScraping completed. Results saved to {output_filename}")

async def parse_html_snippet():
    """
    Parse the HTML snippet provided by the user and save as JSON.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"finviz_metrics_from_snippet_{timestamp}.json"
    
    print(f"Output will be saved to: {output_filename}")
    
    # Data structure for JSON output
    metrics_data = {}
    
    # Read the HTML snippet from paste.txt
    try:
        with open('paste.txt', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Use regex to directly parse the HTML without loading it into a browser
        # This should handle the specific structure we've seen in the paste.txt file
        
        # Pattern to find span elements with their data-boxover attributes
        span_pattern = r'<span class="screener-combo-title"[^>]*data-boxover="([^"]*)"[^>]*>([^<]*)</span>'
        spans = re.findall(span_pattern, html_content)
        
        # Pattern to find select elements with their IDs and options
        select_pattern = r'<select id="([^"]*)"[^>]*>(.*?)</select>'
        selects = re.findall(select_pattern, html_content, re.DOTALL)
        
        # Make sure we have the same number of spans and selects
        if len(spans) != len(selects):
            print(f"Warning: Found {len(spans)} spans but {len(selects)} selects. Some metrics may be missing.")
        
        metrics_processed = 0
        
        # Process each span and select pair
        for i in range(min(len(spans), len(selects))):
            boxover_text, metric_title = spans[i]
            select_id, options_html = selects[i]
            
            # Extract metric ID
            metric_id = select_id.replace('fs_', '')
            
            # Extract header from boxover
            header_match = re.search(r'header=\[(.*?)\]', boxover_text)
            header = header_match.group(1) if header_match else "No header available"
            
            # Clean up header
            header = html.unescape(header)
            header = re.sub(r'<.*?>', ' ', header)
            header = re.sub(r'\s+', ' ', header).strip()
            
            # Extract description from boxover
            description = "No description available"
            try:
                # Try to extract description from tooltip_tab
                desc_match = re.search(r"body=\[.*?class='tooltip_tab'>(.*?)</td>", boxover_text, re.DOTALL)
                if desc_match:
                    description = desc_match.group(1)
                    description = html.unescape(description)
                    description = re.sub(r'<.*?>', ' ', description)
                    description = re.sub(r'\s+', ' ', description).strip()
            except Exception as e:
                print(f"Error extracting description for {metric_id}: {e}")
            
            # Parse options
            option_pattern = r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>'
            parsed_options = re.findall(option_pattern, options_html)
            
            # Create values dictionary
            values = {}
            for option_value, option_text in parsed_options:
                key = f"{metric_id}_{option_value}" if option_value else "Any"
                values[key] = option_text.strip()
            
            # Prompt user
            print("\n" + "="*50)
            print(f"METRIC: {metric_title} ({metric_id})")
            print(f"HEADER: {header}")
            print(f"DESCRIPTION: {description}")
            user_input = input("Include this metric? (y/n): ").strip().lower()
            
            if user_input == 'y':
                # Add to JSON data
                metrics_data[metric_id] = {
                    "metric_name": metric_id,
                    "metric_title": metric_title,
                    "metric_description": description,
                    "values": values
                }
                
                metrics_processed += 1
                print(f"Added metric {metric_id} to output")
            else:
                print(f"Skipping metric: {metric_title}")
        
        # Write JSON data to file
        with open(output_filename, 'w', encoding='utf-8') as json_file:
            json.dump(metrics_data, json_file, indent=2)
        
        print(f"\nProcessed {metrics_processed} metrics from HTML snippet")
        print(f"Data saved to {output_filename}")
    
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        print(error_msg)
        # Try to save whatever data we have
        if metrics_data:
            with open(output_filename, 'w', encoding='utf-8') as json_file:
                json.dump(metrics_data, json_file, indent=2)
            print(f"Partial data saved to {output_filename}")
        return False
    
    return True

if __name__ == "__main__":
    # Ask the user whether to scrape the website or parse the HTML snippet
    print("Choose an option:")
    print("1: Scrape FinViz website")
    print("2: Parse HTML snippet from paste.txt")
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(scrape_filter_tables())
    elif choice == "2":
        asyncio.run(parse_html_snippet())
    else:
        print("Invalid choice. Please run the script again and enter 1 or 2.")