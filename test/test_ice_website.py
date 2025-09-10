#!/usr/bin/env python3
"""
Test script to understand the real ICE website structure.
"""

import asyncio
import httpx
from bs4 import BeautifulSoup

async def test_ice_website():
    """Test the real ICE website structure."""
    print("Testing ICE website structure...")
    
    # Use a realistic user agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # First, get the main page to understand the structure
            print("Fetching main page...")
            response = await client.get("https://locator.ice.gov/", headers=headers)
            print(f"Main page status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                print("Page title:", soup.title.text if soup.title else "No title")
                
                # Look for search form
                forms = soup.find_all('form')
                print(f"Found {len(forms)} forms")
                
                for i, form in enumerate(forms):
                    print(f"Form {i}:")
                    print(f"  Action: {form.get('action', 'No action')}")
                    print(f"  Method: {form.get('method', 'No method')}")
                    
                    # Look for input fields
                    inputs = form.find_all('input')
                    for input_field in inputs:
                        name = input_field.get('name', 'No name')
                        type_ = input_field.get('type', 'No type')
                        print(f"    Input: {name} ({type_})")
            
            # Try to access the search page directly
            print("\nFetching search page...")
            search_response = await client.get("https://locator.ice.gov/search", headers=headers)
            print(f"Search page status: {search_response.status_code}")
            
            if search_response.status_code == 200:
                search_soup = BeautifulSoup(search_response.text, 'html.parser')
                print("Search page title:", search_soup.title.text if search_soup.title else "No title")
                
                # Look for CSRF token or other security measures
                csrf_tokens = search_soup.find_all('input', {'name': lambda x: x and 'csrf' in x.lower()})
                if csrf_tokens:
                    print(f"Found {len(csrf_tokens)} CSRF token fields")
                    for token in csrf_tokens:
                        print(f"  Token name: {token.get('name')}")
                        print(f"  Token value: {token.get('value', 'No value')}")
                
                # Look for common search fields
                search_fields = [
                    'first_name', 'last_name', 'date_of_birth', 'country_of_birth', 
                    'alien_number', 'a_number'
                ]
                
                for field in search_fields:
                    elements = search_soup.find_all('input', {'name': field})
                    if elements:
                        print(f"Found {len(elements)} elements with name '{field}'")
                        
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ice_website())