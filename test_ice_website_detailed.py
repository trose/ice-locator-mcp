#!/usr/bin/env python3
"""
Enhanced test script to understand the real ICE website structure using browser simulation.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from src.ice_locator_mcp.core.config import SearchConfig
from bs4 import BeautifulSoup


async def test_ice_website_detailed():
    """Test the real ICE website structure with browser simulation."""
    print("Testing ICE website structure with browser simulation...")
    
    # Create search config
    config = SearchConfig(
        base_url="https://locator.ice.gov",
        timeout=30,
        requests_per_minute=10,
        burst_allowance=5
    )
    
    # Initialize browser simulator
    browser_sim = BrowserSimulator(config)
    await browser_sim.initialize()
    
    try:
        # Create a session
        session_id = "test_session"
        
        # Navigate to the main page
        print("Navigating to main page...")
        main_page_content = await browser_sim.navigate_to_page(session_id, "https://locator.ice.gov/")
        print("Main page loaded successfully")
        
        # Parse the main page
        main_soup = BeautifulSoup(main_page_content, 'html.parser')
        print(f"Main page title: {main_soup.title.text if main_soup.title else 'No title'}")
        
        # Look for links to the search page
        links = main_soup.find_all('a', href=True)
        search_links = [link for link in links if 'search' in link.get('href', '').lower()]
        print(f"Found {len(search_links)} links containing 'search'")
        
        for link in search_links:
            print(f"  Link: {link.get('href')} - Text: {link.get_text(strip=True)}")
        
        # Try to navigate to the search page
        print("\nNavigating to search page...")
        search_page_content = await browser_sim.navigate_to_page(session_id, "https://locator.ice.gov/search")
        print("Search page loaded successfully")
        
        # Parse the search page
        search_soup = BeautifulSoup(search_page_content, 'html.parser')
        print(f"Search page title: {search_soup.title.text if search_soup.title else 'No title'}")
        
        # Look for forms
        forms = search_soup.find_all('form')
        print(f"Found {len(forms)} forms on search page")
        
        for i, form in enumerate(forms):
            print(f"\nForm {i}:")
            print(f"  Action: {form.get('action', 'No action')}")
            print(f"  Method: {form.get('method', 'No method')}")
            
            # Look for input fields
            inputs = form.find_all('input')
            print(f"  Found {len(inputs)} input fields:")
            for input_field in inputs:
                name = input_field.get('name', 'No name')
                type_ = input_field.get('type', 'No type')
                placeholder = input_field.get('placeholder', 'No placeholder')
                print(f"    Name: {name}, Type: {type_}, Placeholder: {placeholder}")
            
            # Look for select fields
            selects = form.find_all('select')
            print(f"  Found {len(selects)} select fields:")
            for select in selects:
                name = select.get('name', 'No name')
                print(f"    Name: {name}")
                
                # Look for options
                options = select.find_all('option')
                if options:
                    print(f"      Options: {[opt.get_text(strip=True) for opt in options[:3]]}...")
        
        # Look for CSRF tokens or other security measures
        csrf_tokens = search_soup.find_all('input', {'name': lambda x: x and ('csrf' in x.lower() or '_token' in x.lower())})
        if csrf_tokens:
            print(f"\nFound {len(csrf_tokens)} CSRF token fields:")
            for token in csrf_tokens:
                name = token.get('name')
                value = token.get('value', 'No value')
                print(f"  Token name: {name}, Value: {value}")
        
        # Look for JavaScript that might be important
        scripts = search_soup.find_all('script')
        print(f"\nFound {len(scripts)} script tags")
        
        # Look for specific search-related elements
        search_elements = search_soup.find_all(['input', 'select'], 
                                              {'name': lambda x: x and any(keyword in x.lower() for keyword in 
                                              ['first', 'last', 'name', 'birth', 'country', 'alien', 'number'])})
        print(f"\nFound {len(search_elements)} potential search elements:")
        for element in search_elements:
            name = element.get('name', 'No name')
            type_ = element.get('type', 'No type')
            placeholder = element.get('placeholder', 'No placeholder')
            print(f"  Name: {name}, Type: {type_}, Placeholder: {placeholder}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        await browser_sim.close_all_sessions()


if __name__ == "__main__":
    asyncio.run(test_ice_website_detailed())