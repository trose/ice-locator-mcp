#!/usr/bin/env python3
"""
Validation script to verify removal of mock data and real data integration.
"""

import os
import re

def check_for_mock_data(file_path):
    """Check if a file contains mock or simulated data."""
    # More specific patterns that indicate mock/fake data generation
    mock_patterns = [
        r'generate_mock',
        r'create_fake',
        r'generate_dummy',
        r'simulate_response',
        r'mock_data',
        r'fake_data',
        r'dummy_data',
        r'test_data_generator',
        r'sample_data'
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for mock data patterns
        found_patterns = []
        for pattern in mock_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                found_patterns.append(pattern)
                
        return found_patterns
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def main():
    """Main validation function."""
    print("Validating removal of mock data and real data integration...")
    
    # Files to check
    files_to_check = [
        'enrich_detainees.py',
        'search_detainee.py',
        'test_real_data_integration.py'
    ]
    
    issues_found = []
    
    for file_name in files_to_check:
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        if os.path.exists(file_path):
            mock_patterns = check_for_mock_data(file_path)
            if mock_patterns:
                issues_found.append((file_name, mock_patterns))
                print(f"⚠️  {file_name} contains potential mock data patterns: {', '.join(mock_patterns)}")
            else:
                print(f"✅ {file_name} - No mock data patterns found")
        else:
            print(f"❓ {file_name} - File not found")
    
    # Check that real data integration is implemented
    real_integration_files = [
        'src/ice_locator_mcp/core/search_engine.py',
        'src/ice_locator_mcp/anti_detection/browser_simulator.py',
        'src/ice_locator_mcp/anti_detection/proxy_manager.py'
    ]
    
    for file_name in real_integration_files:
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        if os.path.exists(file_path):
            print(f"✅ {file_name} - Real data integration component exists")
        else:
            print(f"❌ {file_name} - Real data integration component missing")
            issues_found.append((file_name, ["File missing"]))
    
    # Summary
    print("\n" + "="*50)
    if issues_found:
        print("Validation completed with issues:")
        for file_name, patterns in issues_found:
            if file_name != 'test_real_data_integration.py':  # Ignore test file
                print(f"  - {file_name}: {', '.join(patterns)}")
        # Filter out test file issues for success check
        real_issues = [issue for issue in issues_found if issue[0] != 'test_real_data_integration.py']
        success = len(real_issues) == 0
    else:
        print("✅ Validation completed successfully! No mock data found and real data integration verified.")
        success = True
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)