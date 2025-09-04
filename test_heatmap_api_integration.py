#!/usr/bin/env python3
"""
Test script to verify heatmap API integration with the web app.
"""

import requests
import json

def test_heatmap_api():
    """Test the heatmap API endpoints."""
    base_url = "http://localhost:8082"
    
    print("Testing Heatmap API Integration")
    print("=" * 40)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Message: {data.get('message')}")
            print(f"  Version: {data.get('version')}")
            print(f"  Endpoints: {data.get('endpoints')}")
    except Exception as e:
        print(f"Error accessing root endpoint: {e}")
    
    # Test facilities endpoint
    try:
        response = requests.get(f"{base_url}/api/facilities")
        print(f"\nFacilities endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Number of facilities: {len(data)}")
            if data:
                print(f"  First facility: {data[0].get('name')}")
    except Exception as e:
        print(f"Error accessing facilities endpoint: {e}")
    
    # Test heatmap data endpoint
    try:
        response = requests.get(f"{base_url}/api/heatmap-data")
        print(f"\nHeatmap data endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Number of heatmap entries: {len(data)}")
            if data:
                facility = data[0]
                print(f"  First facility: {facility.get('name')}")
                print(f"  Detainee count: {facility.get('current_detainee_count')}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Error accessing heatmap data endpoint: {e}")

if __name__ == "__main__":
    test_heatmap_api()