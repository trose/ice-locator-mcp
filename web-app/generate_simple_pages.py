#!/usr/bin/env python3
"""
Simple script to generate static HTML pages for ICE detention facilities
"""

import json
import os

def load_facilities_data():
    """Load facilities data from JSON file"""
    with open('src/data/facilities.json', 'r') as f:
        return json.load(f)

def create_facilities_directory():
    """Create facilities directory if it doesn't exist"""
    os.makedirs('public/facilities', exist_ok=True)

def generate_facility_page(facility, index):
    """Generate HTML page for a single facility"""
    name = facility['name']
    address = facility['address']
    population = facility['population_count']
    lat = facility['latitude']
    lng = facility['longitude']

    # Create URL-friendly name
    url_name = name.lower().replace(' ', '-').replace('/', '-').replace(',', '').replace('(', '').replace(')', '')

    # Generate state from address
    state = address.split(', ')[-2] if ', ' in address else 'Unknown'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - ICE Detention Facility | Population & Location</title>
    <meta name="description" content="{name} is an ICE detention facility located in {address} with a population of {population:,","detainees. Get detailed information about this immigration detention center.">
    <meta name="keywords" content="{name}, ICE detention, immigration detention center, {state}, detention facility, population {population}">

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="{name} - ICE Detention Facility">
    <meta property="og:description" content="{name} immigration detention facility information including location, population, and statistics.">
    <meta property="og:url" content="https://ice-locator-mcp.vercel.app/facilities/{url_name}.html">
    <meta property="og:site_name" content="ICE Facility Locator">

    <!-- Twitter -->
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{name} - ICE Detention Facility">
    <meta name="twitter:description" content="{name} immigration detention facility information.">

    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #1e40af, #3b82f6);
            color: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        .stat-card {{
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }}
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #1e40af;
        }}
        .stat-label {{
            color: #64748b;
            font-size: 0.9rem;
        }}
        .map-container {{
            height: 400px;
            margin: 2rem 0;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #e2e8f0;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 2rem;
            color: #3b82f6;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border: 1px solid #3b82f6;
            border-radius: 4px;
        }}
        .back-link:hover {{
            background: #3b82f6;
            color: white;
        }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-link">← Back to Home</a>
    <a href="index.html" class="back-link">← All Facilities</a>

    <div class="header">
        <h1>{name}</h1>
        <p>ICE Immigration Detention Facility</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{population:,","</div>
            <div class="stat-label">Current Population</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{state}</div>
            <div class="stat-label">State</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">#{index + 1}</div>
            <div class="stat-label">Facility Rank</div>
        </div>
    </div>

    <h2>Facility Information</h2>
    <div class="stat-card">
        <h3>Location Details</h3>
        <p><strong>Address:</strong> {address}</p>
        <p><strong>Coordinates:</strong> {lat}, {lng}</p>
        <p><strong>State:</strong> {state}</p>
    </div>

    <h2>Interactive Map</h2>
    <div class="map-container">
        <iframe
            width="100%"
            height="100%"
            frameborder="0"
            style="border:0"
            src="https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dOMLD0k9XKTtf8&q={lat},{lng}&zoom=15"
            allowfullscreen>
        </iframe>
    </div>

    <h2>About This Facility</h2>
    <p>{name} is an Immigration and Customs Enforcement (ICE) detention facility located in {address}. This facility is part of the U.S. immigration detention system and currently holds {population:,","detainees.</p>

    <p>The facility provides detention services for individuals awaiting immigration proceedings or deportation. ICE detention facilities are operated by private contractors or local governments under contract with the federal government.</p>

    <h2>Related Facilities</h2>
    <p>Compare with other major ICE detention facilities:</p>
    <ul>
        <li><a href="adelanto-ice-processing-center.html">Adelanto ICE Processing Center</a></li>
        <li><a href="stewart-detention-center.html">Stewart Detention Center</a></li>
        <li><a href="otay-mesa-detention-center.html">Otay Mesa Detention Center</a></li>
        <li><a href="eloy-detention-center.html">Eloy Detention Center</a></li>
    </ul>

    <h2>Data Sources</h2>
    <p>Information provided by <a href="https://tracreports.org/" target="_blank">TRAC Reports</a> from Syracuse University. Data is updated monthly and represents average daily population counts.</p>

    <footer style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #e2e8f0; color: #64748b; text-align: center;">
        <p>&copy; 2025 ICE Facility Locator. Data transparency for immigration detention.</p>
    </footer>
</body>
</html>"""

    return html

def generate_facilities_index_page(facilities):
    """Generate the main facilities index page"""
    # Sort facilities by population (descending)
    sorted_facilities = sorted(facilities, key=lambda x: x['population_count'], reverse=True)

    # Get statistics
    total_facilities = len(facilities)
    total_population = sum(f['population_count'] for f in facilities)
    avg_population = total_population / total_facilities

    # Group by state
    states = {}
    for facility in facilities:
        state = facility['address'].split(', ')[-2] if ', ' in facility['address'] else 'Unknown'
        if state not in states:
            states[state] = []
        states[state].append(facility)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ICE Detention Facilities Directory | Complete List & Statistics</title>
    <meta name="description" content="Complete directory of {total_facilities} ICE detention facilities across the United States. Find locations, population data, and statistics for immigration detention centers.">
    <meta name="keywords" content="ICE facilities, detention centers, immigration detention, facility directory, population statistics">

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="ICE Detention Facilities Directory">
    <meta property="og:description" content="Complete directory of ICE detention facilities with locations and population data.">
    <meta property="og:url" content="https://ice-locator-mcp.vercel.app/facilities/index.html">

    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #1e40af, #3b82f6);
            color: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        .stat-card {{
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #1e40af;
        }}
        .stat-label {{
            color: #64748b;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}
        .facilities-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        .facility-card {{
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1.5rem;
            transition: box-shadow 0.2s;
        }}
        .facility-card:hover {{
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .facility-name {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #1e40af;
            margin-bottom: 0.5rem;
        }}
        .facility-location {{
            color: #64748b;
            margin-bottom: 1rem;
        }}
        .facility-population {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #dc2626;
        }}
        .state-section {{
            margin-bottom: 2rem;
        }}
        .state-header {{
            background: #f1f5f9;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            font-weight: 600;
            color: #334155;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 2rem;
            color: #3b82f6;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border: 1px solid #3b82f6;
            border-radius: 4px;
        }}
        .back-link:hover {{
            background: #3b82f6;
            color: white;
        }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-link">← Back to Home</a>

    <div class="header">
        <h1>ICE Detention Facilities Directory</h1>
        <p>Complete list of {total_facilities} immigration detention facilities across the United States</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{total_facilities}</div>
            <div class="stat-label">Total Facilities</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{total_population:,","</div>
            <div class="stat-label">Total Population</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{avg_population".1f"}</div>
            <div class="stat-label">Average per Facility</div>
        </div>
    </div>

    <h2>Facilities by State</h2>"""

    # Add state sections
    for state in sorted(states.keys()):
        facilities_in_state = states[state]
        html += f"""
    <div class="state-section">
        <div class="state-header">
            {state} ({len(facilities_in_state)} facilities)
        </div>
        <div class="facilities-grid">"""

        for facility in sorted(facilities_in_state, key=lambda x: x['population_count'], reverse=True):
            name = facility['name']
            address = facility['address']
            population = facility['population_count']
            url_name = name.lower().replace(' ', '-').replace('/', '-').replace(',', '').replace('(', '').replace(')', '')

            html += f"""
            <div class="facility-card">
                <div class="facility-name">{name}</div>
                <div class="facility-location">{address}</div>
                <div class="facility-population">{population:,","detainees</div>
                <a href="{url_name}.html" style="color: #3b82f6; text-decoration: none; font-size: 0.9rem;">View Details →</a>
            </div>"""

        html += """
        </div>
    </div>"""

    html += """
    <h2>About This Directory</h2>
    <p>This directory contains information about all ICE detention facilities currently in operation across the United States. Data includes facility locations, population counts, and operational details.</p>

    <p>Information is sourced from <a href="https://tracreports.org/" target="_blank">TRAC Reports</a> and updated regularly to provide the most current information available.</p>

    <footer style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #e2e8f0; color: #64748b; text-align: center;">
        <p>&copy; 2025 ICE Facility Locator. Data transparency for immigration detention.</p>
    </footer>
</body>
</html>"""

    return html

def main():
    """Main function to generate all static pages"""
    print("Loading facilities data...")
    data = load_facilities_data()
    facilities = data['facilities']

    print(f"Found {len(facilities)} facilities")

    # Create facilities directory
    create_facilities_directory()

    # Generate facilities index page
    print("Generating facilities index page...")
    index_html = generate_facilities_index_page(facilities)
    with open('public/facilities/index.html', 'w') as f:
        f.write(index_html)

    # Generate individual facility pages (top 30 by population)
    print("Generating individual facility pages...")
    sorted_facilities = sorted(facilities, key=lambda x: x['population_count'], reverse=True)[:30]

    for i, facility in enumerate(sorted_facilities):
        print(f"  Generating page for {facility['name']}...")
        facility_html = generate_facility_page(facility, i)
        url_name = facility['name'].lower().replace(' ', '-').replace('/', '-').replace(',', '').replace('(', '').replace(')', '')
        with open(f'public/facilities/{url_name}.html', 'w') as f:
            f.write(facility_html)

    print("✅ Static pages generated successfully!")
    print("  - Facilities index: public/facilities/index.html")
    print(f"  - Individual pages: {len(sorted_facilities)} facility pages")

if __name__ == "__main__":
    main()