#!/usr/bin/env python3
"""
Enhanced test script to verify browser simulation with improved anti-detection measures.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from src.ice_locator_mcp.core.config import SearchConfig
from bs4 import BeautifulSoup


async def test_enhanced_browser_simulation():
    """Test enhanced browser simulation with improved anti-detection measures."""
    print("Testing enhanced browser simulation...")
    
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
        session_id = "enhanced_test_session"
        
        # Navigate to the main page with enhanced anti-detection
        print("Navigating to main page with enhanced anti-detection...")
        main_page_content = await browser_sim.navigate_to_page(session_id, "https://locator.ice.gov/")
        
        # Parse the main page
        main_soup = BeautifulSoup(main_page_content, 'html.parser')
        print(f"Main page title: {main_soup.title.text if main_soup.title else 'No title'}")
        print(f"Main page status: Success")
        
        # Check for common security indicators
        security_indicators = [
            'access denied', 'forbidden', '403', 'blocked', 
            'security check', 'captcha', 'unusual traffic'
        ]
        
        page_text = main_soup.get_text().lower()
        found_indicators = [indicator for indicator in security_indicators if indicator in page_text]
        
        if found_indicators:
            print(f"Security indicators found: {found_indicators}")
        else:
            print("No obvious security indicators found")
        
        # Try to navigate to the search page
        print("\nNavigating to search page...")
        search_page_content = await browser_sim.navigate_to_page(session_id, "https://locator.ice.gov/search")
        
        # Parse the search page
        search_soup = BeautifulSoup(search_page_content, 'html.parser')
        print(f"Search page title: {search_soup.title.text if search_soup.title else 'No title'}")
        print(f"Search page status: Success")
        
        # Look for forms
        forms = search_soup.find_all('form')
        print(f"Found {len(forms)} forms on search page")
        
        # Look for input fields that might be used for searching
        all_inputs = search_soup.find_all('input')
        search_inputs = [inp for inp in all_inputs if inp.get('type') in ['text', 'search'] or 
                        any(keyword in inp.get('name', '').lower() for keyword in 
                            ['first', 'last', 'name', 'birth', 'country', 'alien', 'number'])]
        
        print(f"Found {len(search_inputs)} potential search input fields:")
        for inp in search_inputs:
            name = inp.get('name', 'No name')
            type_ = inp.get('type', 'No type')
            placeholder = inp.get('placeholder', 'No placeholder')
            print(f"  Name: {name}, Type: {type_}, Placeholder: {placeholder}")
        
        # Try to simulate a search (without actually submitting)
        if search_inputs and forms:
            print("\nSimulating search form interaction...")
            
            # Create form data mapping
            form_fields = {}
            for inp in search_inputs[:3]:  # Limit to first 3 fields to avoid overloading
                name = inp.get('name')
                if name:
                    # Use realistic test data
                    if 'first' in name.lower():
                        form_fields[f'input[name="{name}"]'] = "John"
                    elif 'last' in name.lower():
                        form_fields[f'input[name="{name}"]'] = "Doe"
                    elif 'birth' in name.lower():
                        form_fields[f'input[name="{name}"]'] = "01/01/1990"
                    elif 'country' in name.lower():
                        form_fields[f'input[name="{name}"]'] = "Mexico"
                    else:
                        form_fields[f'input[name="{name}"]'] = "Test"
            
            if form_fields:
                print(f"Preparing to fill {len(form_fields)} form fields")
                # In a real implementation, we would fill the form here
                # but for testing purposes, we'll just show what would be filled
                for selector, value in form_fields.items():
                    print(f"  Would fill {selector} with '{value}'")
            
            print("Form interaction simulation completed")
        
        print("\nEnhanced browser simulation test completed successfully!")
        
    except Exception as e:
        print(f"Error during enhanced browser simulation test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        await browser_sim.close_all_sessions()


if __name__ == "__main__":
    asyncio.run(test_enhanced_browser_simulation())