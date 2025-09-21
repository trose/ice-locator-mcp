#!/usr/bin/env python3
import json
import os
from pathlib import Path
from datetime import datetime

def generate_sitemap():
    """Generate XML sitemap for all pages"""

    # Base URL for the site
    base_url = "https://ice-locator.org"

    # Find all HTML files
    static_pages_dir = Path("/Users/trose/src/ice-locator-mcp/static-pages")

    if not static_pages_dir.exists():
        print(f"Error: {static_pages_dir} not found")
        return

    # Collect all HTML files
    html_files = []
    for root, dirs, files in os.walk(static_pages_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = Path(root) / file
                rel_path = filepath.relative_to(static_pages_dir)
                html_files.append(rel_path)

    # Generate sitemap XML
    sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''

    # Add main pages
    main_pages = [
        '',
        'facilities/',
        'statistics/',
        'about/'
    ]

    for page in main_pages:
        url = f"{base_url}/{page}".rstrip('/')
        if page == '':
            url = base_url
        sitemap_content += f'''  <url>
    <loc>{url}</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>daily</changefreq>
    <priority>{'1.0' if page == '' else '0.8'}</priority>
  </url>
'''

    # Add facility pages
    facilities_dir = static_pages_dir / 'facilities'
    if facilities_dir.exists():
        for file in facilities_dir.glob('*.html'):
            if file.name != 'index.html':
                rel_path = file.relative_to(static_pages_dir)
                url = f"{base_url}/{rel_path}"
                sitemap_content += f'''  <url>
    <loc>{url}</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>
'''

    sitemap_content += '</urlset>'

    # Write sitemap
    sitemap_file = static_pages_dir / 'sitemap.xml'
    with open(sitemap_file, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)

    print(f"Generated sitemap: {sitemap_file}")
    print(f"Total URLs in sitemap: {len(html_files) + len(main_pages)}")

if __name__ == "__main__":
    generate_sitemap()