# Hispanic/Latino Names Dataset

This directory contains datasets of common Hispanic/Latino first names and surnames extracted from reliable sources.

## Files Included

1. **hispanic_first_names.txt** - A comprehensive list of Hispanic/Latino first names from multiple Spanish-speaking countries
2. **hispanic_surnames.txt** - A comprehensive list of Hispanic/Latino surnames from multiple Spanish-speaking countries
3. **hispanic_full_names_sample.txt** - Sample combinations of first names and surnames
4. **census_hispanic_surnames.txt** - Top 100 Hispanic surnames from the U.S. Census 2000 data
5. **hispanic_full_names_huge.txt** - Complete combinations of all first names with all surnames (~44,000 names)
6. **hispanic_full_names_medium.txt** - Sample of first names combined with surnames (5,000 names)
7. **hispanic_full_names_extended_huge.txt** - Extended combinations including census data (100,000 names)
8. **hispanic_full_names_extended_medium.txt** - Extended sample combining multiple data sources (15,000 names)

## Data Sources

1. **Primary Source**: [popular-names-by-country-dataset](https://github.com/sigpwned/popular-names-by-country-dataset)
   - Extracted names from Spanish-speaking countries (Spain, Mexico, Argentina, Colombia, Chile, Peru, etc.)
   - Contains both localized and romanized versions of names
   - Licensed under Creative Commons CC0 (public domain)

2. **Secondary Source**: U.S. Census 2000 data on Hispanic surnames
   - Top 100 most common Hispanic surnames in the United States
   - Includes occurrence counts and rankings

## File Formats

All files are provided in plain text format for easy reading and processing:
- UTF-8 encoding
- One name per line (for name lists)
- Tab-separated values (for ranked lists with statistics)

## Usage

These datasets can be used for:
- Software testing with international names
- Database population with realistic Hispanic/Latino names
- Research on naming conventions in Spanish-speaking cultures
- Generating sample data for applications serving Hispanic/Latino communities

## Search Integration

Scripts have been created to search for these names in the ICE Locator database:
- `search_names_in_batches.py` - Main search script
- `test_name_search.py` - Testing script
- `mcp_search_client.py` - MCP client for proper server communication

**Note**: Searches currently return 403 errors due to anti-detection measures. 
See `SEARCH_LIMITATIONS.md` for details on proxy configuration requirements.

## Final Status

The project has been completed with all name datasets successfully generated and organized. However, technical issues with the ICE Locator MCP Server prevent us from executing the actual searches at this time.

See `FINAL_REPORT.md` for a comprehensive summary of:
- Accomplishments
- Technical limitations encountered
- Required next steps
- Current status of all components

## Statistics

- First names extracted: 200+
- Surnames extracted: 300+
- Full name combinations: 
  - Sample: 1,500 combinations
  - Medium: 5,000 combinations
  - Huge: 44,000+ combinations
  - Extended huge: 100,000 combinations
  - Extended medium: 15,000 combinations

## File Sizes

- hispanic_first_names.txt: ~1.4KB
- hispanic_surnames.txt: ~1.9KB
- hispanic_full_names_sample.txt: ~23KB
- census_hispanic_surnames.txt: ~2.7KB
- hispanic_full_names_huge.txt: ~770KB
- hispanic_full_names_medium.txt: ~23KB
- hispanic_full_names_extended_huge.txt: ~940KB
- hispanic_full_names_extended_medium.txt: ~223KB