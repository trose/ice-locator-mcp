# ICE Detention Facilities Static Pages

This directory contains a comprehensive set of static HTML pages for ICE detention facilities, designed to improve SEO and provide detailed information about facilities across the United States.

## Overview

The static pages system includes:

- **34 HTML pages** total
- **30 individual facility pages** for top facilities by population
- **4 main pages**: Home, Facilities Directory, Statistics, and About
- **1 XML sitemap** for search engine optimization
- **Mobile-friendly responsive design**
- **SEO-optimized** with meta tags, Open Graph, and JSON-LD structured data

## Directory Structure

```
static-pages/
├── index.html                    # Home page
├── sitemap.xml                   # XML sitemap for SEO
├── about/
│   └── index.html               # About page
├── facilities/
│   ├── index.html               # Facilities directory
│   ├── dilley-family-residential-center.html
│   ├── adelanto-ice-processing-center.html
│   └── ... (28 more facility pages)
├── statistics/
│   └── index.html               # Statistics and data analysis
└── templates/
    └── base.html                # Base HTML template
```

## Pages Generated

### Main Pages

1. **Home Page** (`index.html`)
   - Overview of the ICE facilities database
   - Key statistics and top facilities
   - Quick navigation links

2. **Facilities Directory** (`facilities/index.html`)
   - Complete list of all 186 ICE facilities
   - Sorted by population (descending)
   - Searchable table with location and population data

3. **Statistics Page** (`statistics/index.html`)
   - Population distribution analysis
   - State-by-state breakdown
   - Facility capacity statistics

4. **About Page** (`about/index.html`)
   - Information about the resource
   - Data sources and methodology
   - Related organizations and links

### Individual Facility Pages

30 individual pages for the top facilities by population, including:

- **Dilley Family Residential Center** (2,000 capacity)
- **Adelanto ICE Processing Center** (1,847 capacity)
- **South Texas Family Residential Center** (1,800 capacity)
- **Stewart Detention Center** (1,800 capacity)
- And 26 more top facilities...

Each facility page includes:
- Facility name, location, and capacity
- Detailed information and statistics
- Related links and navigation
- SEO-optimized meta tags and structured data

## SEO Features

### Meta Tags
- Title tags optimized for each page
- Meta descriptions with relevant keywords
- Author and keyword meta tags

### Open Graph Tags
- Facebook sharing optimization
- Twitter card support
- Image and description tags

### JSON-LD Structured Data
- Schema.org markup for better search understanding
- Government building and organization schemas
- Dataset and statistical information schemas

### Technical SEO
- XML sitemap with all pages
- Proper URL structure
- Mobile-responsive design
- Fast loading times
- Internal linking structure

## Data Sources

- **Facilities data**: `data/facilities/comprehensive_ice_facilities.json`
- **Top 30 facilities**: `data/facilities/top_30_facilities.json`
- **Statistics**: Calculated from comprehensive facilities data

## Generation Scripts

The pages are generated using Python scripts:

1. `scripts/analyze_facilities.py` - Analyzes data and creates top 30 list
2. `scripts/generate_facility_pages.py` - Creates individual facility pages
3. `scripts/generate_facilities_index.py` - Creates facilities directory
4. `scripts/generate_statistics_page.py` - Creates statistics page
5. `scripts/generate_home_page.py` - Creates home page
6. `scripts/generate_about_page.py` - Creates about page
7. `scripts/generate_sitemap.py` - Creates XML sitemap

## Usage

### To regenerate all pages:
```bash
cd /Users/trose/src/ice-locator-mcp
python3 scripts/analyze_facilities.py
python3 scripts/generate_facility_pages.py
python3 scripts/generate_facilities_index.py
python3 scripts/generate_statistics_page.py
python3 scripts/generate_home_page.py
python3 scripts/generate_about_page.py
python3 scripts/generate_sitemap.py
```

### To update with new data:
1. Update the facilities JSON files in `data/facilities/`
2. Run the generation scripts to rebuild all pages
3. Deploy the updated static pages

## Deployment

The static pages can be deployed to any web server or static hosting service:

- **GitHub Pages**
- **Netlify**
- **Vercel**
- **Traditional web hosting**

Simply upload the contents of the `static-pages/` directory to your web server.

## Benefits

### SEO Impact
- **30+ indexed pages** for facility-specific searches
- **Structured data** for rich snippets in search results
- **Internal linking** for improved site authority
- **Mobile optimization** for better search rankings

### User Experience
- **Fast loading** static pages
- **Responsive design** for all devices
- **Clear navigation** and breadcrumbs
- **Comprehensive information** in organized format

### Data Transparency
- **Public information** readily accessible
- **Statistical analysis** for better understanding
- **Complete directory** of all facilities
- **Regular updates** with latest data

## Future Enhancements

Potential improvements for the static pages system:

1. **Search functionality** within the facilities directory
2. **Interactive maps** showing facility locations
3. **Data visualization** charts and graphs
4. **Multi-language support** for accessibility
5. **API endpoints** for programmatic access
6. **Real-time updates** from data sources

## Support

For questions or issues with the static pages system, please refer to the main project documentation or contact the development team.