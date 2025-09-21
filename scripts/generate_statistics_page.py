#!/usr/bin/env python3
import json
import os
from pathlib import Path
from string import Template
from collections import Counter

def generate_statistics_page():
    """Generate the statistics page"""

    # Load all facilities data
    facilities_file = Path("/Users/trose/src/ice-locator-mcp/data/facilities/comprehensive_ice_facilities.json")

    if not facilities_file.exists():
        print(f"Error: {facilities_file} not found")
        return

    with open(facilities_file, 'r') as f:
        facilities = json.load(f)

    # Calculate statistics
    total_facilities = len(facilities)
    total_population = sum(f.get('population', 0) for f in facilities)
    avg_population = total_population / total_facilities if total_facilities > 0 else 0

    # State distribution
    state_counts = Counter(f.get('state', 'Unknown') for f in facilities)
    top_states = state_counts.most_common(10)

    # Population distribution
    population_ranges = {
        '0-100': 0,
        '101-500': 0,
        '501-1000': 0,
        '1001-2000': 0,
        '2000+': 0
    }

    for facility in facilities:
        pop = facility.get('population', 0)
        if pop <= 100:
            population_ranges['0-100'] += 1
        elif pop <= 500:
            population_ranges['101-500'] += 1
        elif pop <= 1000:
            population_ranges['501-1000'] += 1
        elif pop <= 2000:
            population_ranges['1001-2000'] += 1
        else:
            population_ranges['2000+'] += 1



    # Generate structured data for JSON-LD
    structured_data = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "ICE Detention Facilities Statistics",
        "description": "Statistical analysis of ICE detention facilities across the United States",
        "variableMeasured": [
            {
                "@type": "PropertyValue",
                "name": "Total Facilities",
                "value": total_facilities
            },
            {
                "@type": "PropertyValue",
                "name": "Total Capacity",
                "value": total_population
            }
        ]
    }

    # Generate content for the statistics page
    content = f"""
    <div class="facility-card">
        <p style="margin-bottom: 2rem; font-size: 1.1rem;">
            Comprehensive statistics and analysis of ICE detention facilities across the United States.
            Data includes facility counts, population capacity, and geographic distribution.
        </p>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_facilities}</div>
                <div class="stat-label">Total Facilities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_population:,}</div>
                <div class="stat-label">Total Capacity</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{avg_population:.1f}</div>
                <div class="stat-label">Average per Facility</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(state_counts)}</div>
                <div class="stat-label">States with Facilities</div>
            </div>
        </div>
    </div>

    <div class="facility-card">
        <h2 style="margin-bottom: 1.5rem; color: #1f2937;">Population Distribution</h2>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f8f9fa;">
                        <th style="padding: 1rem; text-align: left; border-bottom: 2px solid #e5e7eb;">Population Range</th>
                        <th style="padding: 1rem; text-align: right; border-bottom: 2px solid #e5e7eb;">Number of Facilities</th>
                        <th style="padding: 1rem; text-align: right; border-bottom: 2px solid #e5e7eb;">Percentage</th>
                    </tr>
                </thead>
                <tbody>
    """

    for range_name, count in population_ranges.items():
        percentage = (count / total_facilities * 100) if total_facilities > 0 else 0
        content += f"""
                    <tr>
                        <td style="padding: 1rem; border-bottom: 1px solid #e5e7eb;">{range_name}</td>
                        <td style="padding: 1rem; text-align: right; border-bottom: 1px solid #e5e7eb;">{count}</td>
                        <td style="padding: 1rem; text-align: right; border-bottom: 1px solid #e5e7eb;">{percentage:.1f}%</td>
                    </tr>
        """

    content += """
                </tbody>
            </table>
        </div>
    </div>

    <div class="facility-card">
        <h2 style="margin-bottom: 1.5rem; color: #1f2937;">Top States by Facility Count</h2>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f8f9fa;">
                        <th style="padding: 1rem; text-align: left; border-bottom: 2px solid #e5e7eb;">State</th>
                        <th style="padding: 1rem; text-align: right; border-bottom: 2px solid #e5e7eb;">Facilities</th>
                        <th style="padding: 1rem; text-align: right; border-bottom: 2px solid #e5e7eb;">Total Population</th>
                    </tr>
                </thead>
                <tbody>
    """

    for state, count in top_states:
        state_population = sum(f.get('population', 0) for f in facilities if f.get('state') == state)
        content += f"""
                    <tr>
                        <td style="padding: 1rem; border-bottom: 1px solid #e5e7eb;">{state}</td>
                        <td style="padding: 1rem; text-align: right; border-bottom: 1px solid #e5e7eb;">{count}</td>
                        <td style="padding: 1rem; text-align: right; border-bottom: 1px solid #e5e7eb;">{state_population:,}</td>
                    </tr>
        """

    content += """
                </tbody>
            </table>
        </div>
    </div>
    """

    # Generate meta tags and other SEO elements
    title = "ICE Detention Facilities Statistics - Data & Analysis"
    description = f"Statistical analysis of {total_facilities} ICE detention facilities with {total_population:,} total capacity. View population distribution, state breakdown, and facility statistics."
    keywords = "ICE statistics, detention data, facility analysis, population statistics, immigration data"

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
    <meta property="og:url" content="https://ice-locator-mcp.vercel.app/statistics/">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="https://ice-locator-mcp.vercel.app/assets/statistics.jpg">
    <meta property="og:site_name" content="ICE Facility Locator">

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://ice-locator-mcp.vercel.app/statistics/">
    <meta property="twitter:title" content="{title}">
    <meta property="twitter:description" content="{description}">
    <meta property="twitter:image" content="https://ice-locator-mcp.vercel.app/assets/statistics.jpg">

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
                <a href="/">Home</a> > Statistics
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
    output_file = Path("/Users/trose/src/ice-locator-mcp/static-pages/statistics/index.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Generated statistics page: {output_file}")

if __name__ == "__main__":
    generate_statistics_page()