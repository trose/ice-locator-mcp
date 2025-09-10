#!/usr/bin/env python3
"""
Fetch complete TRAC Reports facility data.
This script will attempt to find and download the complete dataset.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
import os

class TRACDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def fetch_trac_main_page(self):
        """Fetch the main TRAC Reports page to find facility data links."""
        print("🌐 Fetching TRAC Reports main page...")
        
        try:
            response = self.session.get("https://tracreports.org/", timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for links related to detention facilities
            facility_links = []
            
            # Search for various patterns
            patterns = [
                r'detention.*facilit',
                r'facilit.*detention',
                r'immigration.*detention',
                r'detention.*statistics',
                r'facility.*data',
                r'detention.*data'
            ]
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                for pattern in patterns:
                    if re.search(pattern, href) or re.search(pattern, text):
                        facility_links.append({
                            'url': link['href'],
                            'text': link.get_text().strip(),
                            'full_url': self._make_absolute_url(link['href'])
                        })
            
            print(f"📋 Found {len(facility_links)} potential facility data links:")
            for link in facility_links:
                print(f"   - {link['text']}: {link['full_url']}")
            
            return facility_links
            
        except Exception as e:
            print(f"❌ Error fetching main page: {e}")
            return []
    
    def fetch_detention_page(self):
        """Fetch the detention statistics page."""
        print("🌐 Fetching TRAC detention statistics page...")
        
        try:
            response = self.session.get("https://tracreports.org/immigration/detentionstats/", timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for facility-specific links
            facility_links = []
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text().strip()
                
                if any(keyword in href.lower() or keyword in text.lower() 
                      for keyword in ['facility', 'facilities', 'detention', 'center']):
                    facility_links.append({
                        'url': href,
                        'text': text,
                        'full_url': self._make_absolute_url(href)
                    })
            
            print(f"📋 Found {len(facility_links)} detention-related links:")
            for link in facility_links:
                print(f"   - {link['text']}: {link['full_url']}")
            
            return facility_links
            
        except Exception as e:
            print(f"❌ Error fetching detention page: {e}")
            return []
    
    def fetch_facilities_page(self):
        """Fetch the facilities page directly."""
        print("🌐 Fetching TRAC facilities page...")
        
        try:
            response = self.session.get("https://tracreports.org/immigration/detentionstats/facilities.html", timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for data tables
            tables = soup.find_all('table')
            print(f"📊 Found {len(tables)} tables on facilities page")
            
            # Look for download links
            download_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text().strip()
                
                if any(ext in href.lower() for ext in ['.csv', '.xlsx', '.xls', '.json']):
                    download_links.append({
                        'url': href,
                        'text': text,
                        'full_url': self._make_absolute_url(href)
                    })
            
            print(f"📥 Found {len(download_links)} download links:")
            for link in download_links:
                print(f"   - {link['text']}: {link['full_url']}")
            
            # Look for data in tables
            facilities_data = []
            for i, table in enumerate(tables):
                print(f"\n🔍 Processing table {i+1}...")
                table_data = self._extract_table_data(table)
                if table_data:
                    facilities_data.extend(table_data)
                    print(f"   ✅ Extracted {len(table_data)} records from table {i+1}")
            
            return facilities_data, download_links
            
        except Exception as e:
            print(f"❌ Error fetching facilities page: {e}")
            return [], []
    
    def _extract_table_data(self, table):
        """Extract data from a table."""
        facilities = []
        
        try:
            # Get headers
            headers = []
            header_row = table.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                print(f"   Headers: {headers}")
            
            # Get data rows
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:  # Minimum expected columns
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    
                    # Try to identify facility data
                    if self._is_facility_row(row_data, headers):
                        facility = self._parse_facility_row(row_data, headers)
                        if facility:
                            facilities.append(facility)
            
        except Exception as e:
            print(f"   ⚠️ Error extracting table data: {e}")
        
        return facilities
    
    def _is_facility_row(self, row_data, headers):
        """Check if a row contains facility data."""
        facility_indicators = ['detention', 'center', 'facility', 'jail', 'prison', 'processing', 'correctional']
        
        for cell in row_data:
            if any(indicator in cell.lower() for indicator in facility_indicators):
                return True
        
        # Check if row has numeric population data
        for cell in row_data:
            if cell.isdigit() and int(cell) > 0:
                return True
                
        return False
    
    def _parse_facility_row(self, row_data, headers):
        """Parse a facility row into a structured format."""
        try:
            facility = {
                'name': '',
                'city': '',
                'state': '',
                'zip': '',
                'population': 0,
                'raw_data': row_data
            }
            
            # Map data based on headers if available
            if headers:
                for i, header in enumerate(headers):
                    if i < len(row_data):
                        value = row_data[i]
                        
                        if 'facility' in header.lower() or 'name' in header.lower():
                            facility['name'] = value
                        elif 'city' in header.lower():
                            facility['city'] = value
                        elif 'state' in header.lower():
                            facility['state'] = value
                        elif 'zip' in header.lower() or 'postal' in header.lower():
                            facility['zip'] = value
                        elif 'population' in header.lower() or 'daily' in header.lower() or 'count' in header.lower():
                            try:
                                facility['population'] = int(value.replace(',', ''))
                            except:
                                facility['population'] = 0
            else:
                # Try to infer data from row content
                for i, value in enumerate(row_data):
                    if not facility['name'] and len(value) > 5:
                        facility['name'] = value
                    elif value.isdigit():
                        facility['population'] = int(value)
                    elif len(value) == 2 and value.isalpha():
                        facility['state'] = value
                    elif len(value) == 5 and value.isdigit():
                        facility['zip'] = value
            
            # Only return if we have at least a name
            if facility['name']:
                return facility
                
        except Exception as e:
            print(f"   ⚠️ Error parsing facility row: {e}")
            
        return None
    
    def _make_absolute_url(self, url):
        """Convert relative URL to absolute URL."""
        if url.startswith('http'):
            return url
        elif url.startswith('/'):
            return f"https://tracreports.org{url}"
        else:
            return f"https://tracreports.org/{url}"
    
    def download_data_file(self, url):
        """Download a data file from TRAC."""
        print(f"📥 Downloading data file: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Save the file
            filename = url.split('/')[-1]
            if not filename or '.' not in filename:
                filename = f"trac_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            filepath = f"trac_data_{filename}"
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")
            return None
    
    def search_for_data_updates(self):
        """Search for recent data updates on TRAC."""
        print("🔍 Searching for recent TRAC data updates...")
        
        try:
            # Check the "What's New" page
            response = self.session.get("https://tracreports.org/whatsnew/", timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for recent updates mentioning facilities or detention
            updates = []
            for link in soup.find_all('a', href=True):
                text = link.get_text().strip()
                href = link.get('href', '')
                
                if any(keyword in text.lower() for keyword in ['facility', 'detention', 'immigration', 'ice']):
                    updates.append({
                        'text': text,
                        'url': self._make_absolute_url(href),
                        'date': self._extract_date_from_text(text)
                    })
            
            print(f"📅 Found {len(updates)} recent updates:")
            for update in updates[:10]:  # Show first 10
                print(f"   - {update['date']}: {update['text']}")
            
            return updates
            
        except Exception as e:
            print(f"❌ Error searching for updates: {e}")
            return []
    
    def _extract_date_from_text(self, text):
        """Extract date from text."""
        # Look for date patterns
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\w+ \d{1,2}, \d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "Unknown date"
    
    def fetch_complete_data(self):
        """Main method to fetch complete TRAC data."""
        print("🚀 Starting comprehensive TRAC data fetch...")
        
        all_facilities = []
        download_files = []
        
        # 1. Fetch main page links
        main_links = self.fetch_trac_main_page()
        
        # 2. Fetch detention page
        detention_links = self.fetch_detention_page()
        
        # 3. Fetch facilities page directly
        facilities_data, download_links = self.fetch_facilities_page()
        all_facilities.extend(facilities_data)
        download_files.extend(download_links)
        
        # 4. Search for recent updates
        updates = self.search_for_data_updates()
        
        # 5. Try to download any data files found
        for download_link in download_links:
            filepath = self.download_data_file(download_link['full_url'])
            if filepath:
                print(f"📁 Downloaded data file: {filepath}")
        
        print(f"\n📊 Summary:")
        print(f"   Total facilities found: {len(all_facilities)}")
        print(f"   Download links found: {len(download_files)}")
        print(f"   Recent updates found: {len(updates)}")
        
        # Save results
        if all_facilities:
            with open('trac_facilities_complete.json', 'w') as f:
                json.dump(all_facilities, f, indent=2)
            print(f"💾 Saved {len(all_facilities)} facilities to trac_facilities_complete.json")
        
        return all_facilities, download_files, updates

def main():
    """Main function."""
    fetcher = TRACDataFetcher()
    facilities, downloads, updates = fetcher.fetch_complete_data()
    
    print(f"\n🎉 TRAC data fetch complete!")
    print(f"📊 Found {len(facilities)} facilities")
    print(f"📥 Found {len(downloads)} download links")
    print(f"📅 Found {len(updates)} recent updates")

if __name__ == "__main__":
    main()

