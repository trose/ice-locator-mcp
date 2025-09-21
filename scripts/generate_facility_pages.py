#!/usr/bin/env python3
import json
import os
from pathlib import Path
from string import Template

def generate_facility_pages():
    """Generate individual HTML pages for top facilities"""

    # Load the top 30 facilities data
    facilities_file = Path("/Users/trose/src/ice-locator-mcp/data/facilities/top_30_facilities.json")

    if not facilities_file.exists():
        print(f"Error: {facilities_file} not found")
        return

    with open(facilities_file, 'r') as f:
        facilities = json.load(f)



    # Create output directory
    output_dir = Path("/Users/trose/src/ice-locator-mcp/static-pages/facilities")
    output_dir.mkdir(exist_ok=True)

    print(f"Generating {len(facilities)} facility pages...")

    for facility in facilities:
        name = facility.get('name', 'Unknown Facility')
        city = facility.get('city', 'Unknown')
        state = facility.get('state', 'Unknown')
        zip_code = facility.get('zip', 'Unknown')
        population = facility.get('population', 0)

        # Create URL-friendly filename
        filename = name.lower().replace(' ', '-').replace('/', '-').replace('\'', '')
        filename = ''.join(c for c in filename if c.isalnum() or c in '-')
        filepath = output_dir / f"{filename}.html"

        # Generate structured data for JSON-LD
        structured_data = {
            "@context": "https://schema.org",
            "@type": "GovernmentBuilding",
            "name": name,
            "description": f"ICE detention facility located in {city}, {state} with capacity for {population:,} detainees",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": city,
                "addressRegion": state,
                "postalCode": zip_code
            },
            "containedInPlace": {
                "@type": "City",
                "name": city
            },
            "additionalProperty": {
                "@type": "PropertyValue",
                "name": "Detainee Capacity",
                "value": population
            }
        }

        # Generate content for the facility page
        content = f"""
        <div class="facility-card">
            <div class="facility-header">
                <div>
                    <h2 class="facility-name">{name}</h2>
                    <div class="facility-location">{city}, {state} {zip_code}</div>
                </div>
                <div class="population-badge">{population:,} detainees</div>
            </div>

            <div class="facility-details">
                <div class="detail-item">
                    <div class="detail-label">Location</div>
                    <div class="detail-value">{city}, {state}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">ZIP Code</div>
                    <div class="detail-value">{zip_code}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Detainee Capacity</div>
                    <div class="detail-value">{population:,}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Facility Type</div>
                    <div class="detail-value">ICE Detention Center</div>
                </div>
            </div>

            <div class="related-links">
                <h3>Related Information</h3>
                <div class="related-grid">
                    <a href="/facilities/" class="related-link">All Facilities</a>
                    <a href="/statistics/" class="related-link">Statistics</a>
                    <a href="/about/" class="related-link">About ICE Detention</a>
                </div>
            </div>
        </div>
        """

        # Generate meta tags and other SEO elements
        title = f"{name} - ICE Detention Facility Information"
        description = f"Comprehensive information about {name} in {city}, {state}. Current detainee population: {population:,}. Find location, capacity, and related information."
        keywords = f"{name}, ICE, detention, {city}, {state}, immigration, facility, detainees"

        # Generate the complete HTML
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <meta name="author" content="ICE Locator">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://ice-locator-mcp.vercel.app/facilities/{filename}.html">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="https://ice-locator-mcp.vercel.app/assets/facility-default.jpg">
    <meta property="og:site_name" content="ICE Facility Locator">

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://ice-locator-mcp.vercel.app/facilities/{filename}.html">
    <meta property="twitter:title" content="{title}">
    <meta property="twitter:description" content="{description}">
    <meta property="twitter:image" content="https://ice-locator-mcp.vercel.app/assets/facility-default.jpg">

    <title>{title}</title>

    <!-- JSON-LD Structured Data -->
    <script type="application/ld+json">
    {json.dumps(structured_data, indent=2)}
    </script>

    <!-- Styles -->
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        header {{
            background: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .header-content {{
            padding: 1rem 0;
        }}

        .logo {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #2563eb;
            text-decoration: none;
        }}

        nav {{
            margin-top: 1rem;
        }}

        .nav-links {{
            list-style: none;
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }}

        .nav-links a {{
            color: #666;
            text-decoration: none;
            transition: color 0.3s;
        }}

        .nav-links a:hover {{
            color: #2563eb;
        }}

        main {{
            padding: 2rem 0;
        }}

        .breadcrumb {{
            margin-bottom: 2rem;
            font-size: 0.9rem;
        }}

        .breadcrumb a {{
            color: #2563eb;
            text-decoration: none;
        }}

        .breadcrumb a:hover {{
            text-decoration: underline;
        }}

        .page-title {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: #1f2937;
        }}

        .facility-card {{
            background: #fff;
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .facility-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .facility-name {{
            font-size: 1.8rem;
            color: #1f2937;
            margin-bottom: 0.5rem;
        }}

        .facility-location {{
            color: #666;
            font-size: 1.1rem;
        }}

        .population-badge {{
            background: #ef4444;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: bold;
        }}

        .facility-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .detail-item {{
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 6px;
        }}

        .detail-label {{
            font-weight: bold;
            color: #666;
            margin-bottom: 0.5rem;
        }}

        .detail-value {{
            color: #333;
        }}

        .related-links {{
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid #e5e7eb;
        }}

        .related-links h3 {{
            margin-bottom: 1rem;
            color: #1f2937;
        }}

        .related-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }}

        .related-link {{
            display: block;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 6px;
            text-decoration: none;
            color: #2563eb;
            transition: background-color 0.3s;
        }}

        .related-link:hover {{
            background: #e5e7eb;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: #fff;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .stat-number {{
            font-size: 3rem;
            font-weight: bold;
            color: #2563eb;
            margin-bottom: 0.5rem;
        }}

        .stat-label {{
            color: #666;
            font-size: 1.1rem;
        }}

        footer {{
            background: #1f2937;
            color: #fff;
            padding: 2rem 0;
            margin-top: 4rem;
        }}

        .footer-content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
        }}

        .footer-section h4 {{
            margin-bottom: 1rem;
        }}

        .footer-links {{
            list-style: none;
        }}

        .footer-links a {{
            color: #d1d5db;
            text-decoration: none;
            display: block;
            margin-bottom: 0.5rem;
        }}

        .footer-links a:hover {{
            color: #fff;
        }}

        @media (max-width: 768px) {{
            .facility-header {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .page-title {{
                font-size: 2rem;
            }}

            .facility-name {{
                font-size: 1.5rem;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <a href="/" class="logo">ICE Detention Facilities</a>
                <nav>
                    <ul class="nav-links">
                        <li><a href="/">Home</a></li>
                        <li><a href="/facilities/">All Facilities</a></li>
                        <li><a href="/statistics/">Statistics</a></li>
                        <li><a href="/about/">About</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    <main>
        <div class="container">
            <nav class="breadcrumb">
                <a href="/">Home</a> > <a href="/facilities/">Facilities</a> > {name}
            </nav>

            <h1 class="page-title">{title}</h1>

            {content}
        </div>
    </main>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h4>ICE Detention Facilities</h4>
                    <p>Comprehensive information about ICE detention facilities across the United States.</p>
                </div>
                <div class="footer-section">
                    <h4>Quick Links</h4>
                    <ul class="footer-links">
                        <li><a href="/facilities/">All Facilities</a></li>
                        <li><a href="/statistics/">Statistics</a></li>
                        <li><a href="/about/">About</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>Resources</h4>
                    <ul class="footer-links">
                        <li><a href="https://www.ice.gov/detention-facilities">ICE Official Site</a></li>
                        <li><a href="https://www.aclu.org/">ACLU</a></li>
                        <li><a href="https://www.immigrantjustice.org/">NIJC</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </footer>
</body>
</html>"""

        # Write the HTML file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Generated: {filepath}")

    print(f"\nSuccessfully generated {len(facilities)} facility pages in {output_dir}")

if __name__ == "__main__":
    generate_facility_pages()