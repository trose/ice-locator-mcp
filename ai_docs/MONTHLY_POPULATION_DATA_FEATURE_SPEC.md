# Monthly Population Data Feature Specification

## Overview
This document outlines the design and implementation of a feature to organize facility population data by month, enabling historical analysis and month-by-month visualization in the ICE Locator heatmap.

## Current State Analysis

### Existing Data Structure
- **Current Format**: Single snapshot of facility population data
- **Location**: `web-app/src/data/facilities.json`
- **Structure**: 
  ```json
  {
    "metadata": {
      "exported_at": "2025-09-09T18:51:48.942864",
      "total_facilities": 186,
      "total_population": 62005
    },
    "facilities": [
      {
        "name": "Facility Name",
        "latitude": 28.6695971,
        "longitude": -99.1672017,
        "address": "Address",
        "population_count": 2000
      }
    ]
  }
  ```

### Current Update Process
- **GitHub Action**: `.github/workflows/update-facility-data.yml`
- **Frequency**: Daily at 6 AM UTC
- **Process**: Fetches current data → Updates JSON → Creates PR → Auto-merges

## Proposed Data Structure

### New Monthly Data Format
```json
{
  "metadata": {
    "exported_at": "2025-09-09T18:51:48.942864",
    "total_facilities": 186,
    "available_months": ["2024-01", "2024-02", ..., "2025-09"],
    "latest_month": "2025-09",
    "description": "ICE Detention Facilities - Monthly Population Data"
  },
  "facilities": [
    {
      "name": "Facility Name",
      "latitude": 28.6695971,
      "longitude": -99.1672017,
      "address": "Address",
      "monthly_population": {
        "2024-01": 1800,
        "2024-02": 1850,
        "2024-03": 1900,
        "2025-09": 2000
      }
    }
  ]
}
```

## Implementation Plan

### Phase 1: Data Collection & Parsing
1. **TRAC Data Scraper**
   - Target URL: `https://tracreports.org/immigration/detentionstats/facilities.html`
   - Parse HTML tables for historical data
   - Extract facility names, locations, and monthly population counts
   - Handle pagination and data inconsistencies

2. **Data Processing Script**
   - Merge historical data with existing facility database
   - Normalize facility names and locations
   - Validate data quality and handle missing values
   - Generate monthly population snapshots

### Phase 2: Data Layer Updates
1. **Database Schema Updates**
   - Add `monthly_population` JSON field to facilities table
   - Create migration script for existing data
   - Update data export scripts for frontend

2. **GitHub Action Enhancement**
   - Modify existing workflow to collect historical data
   - Implement incremental updates for new months
   - Add data validation and quality checks

### Phase 3: Frontend Integration
1. **Heatmap Component Updates**
   - Add month selection dropdown
   - Update data loading logic for monthly data
   - Implement default to latest available month
   - Add loading states for month switching

2. **UI/UX Enhancements**
   - Month selector with available data indicators
   - Smooth transitions between months
   - Population trend indicators

## Technical Considerations

### Data Layer Size Management
- **Current Size**: ~186 facilities × 1 snapshot = ~186 records (~200KB)
- **Projected Size**: ~186 facilities × ~75 months = ~13,950 records (~15-20MB)
- **Mitigation Strategies**:
  - Compress monthly data using efficient JSON structure
  - Implement lazy loading for historical months
  - Consider data compression and optimization techniques
  - Evaluate hybrid approach if size becomes problematic

### Performance Optimization
- **Frontend Loading**: Lazy load monthly data on demand
- **Caching**: Implement client-side caching for recently viewed months
- **Compression**: Use efficient data structures and compression

### Data Quality & Validation
- **Source Validation**: Cross-reference TRAC data with multiple sources
- **Consistency Checks**: Validate population totals and facility counts
- **Error Handling**: Graceful degradation for missing or invalid data

## Risk Assessment

### High Risk
- **Data Source Changes**: TRAC website structure changes could break scraping
- **Data Inconsistencies**: Known issues with TRAC data accuracy
- **Performance Impact**: Large data layer could slow frontend loading

### Medium Risk
- **Storage Limits**: GitHub repository size limits for embedded data
- **Update Frequency**: Balancing data freshness with resource usage
- **Browser Compatibility**: Large JSON files in older browsers

### Low Risk
- **UI Complexity**: Month selector adds minimal complexity
- **Backward Compatibility**: Existing functionality remains unchanged

## Success Metrics
- [ ] **Complete historical dataset from 9/30/2019 to present** (100% data coverage)
- [ ] Frontend month selector functional with all available months
- [ ] Data layer optimized for 6+ years of monthly data
- [ ] Page load time < 3 seconds with full historical dataset
- [ ] 95%+ data accuracy compared to source

## Historical Data Scope
- **Target Period**: September 30, 2019 to present (~6+ years)
- **Expected Data Points**: ~186 facilities × ~75 months = ~13,950 data points
- **Data Retention**: Keep complete historical dataset (no rolling window)
- **Update Frequency**: Monthly collection of new data

## Remaining Questions for Stakeholder Review
1. **Performance Trade-offs**: Acceptable data layer size vs. performance for 6+ years of data?
 - investigate Vercel persistent storage through Edge Config & Blob features
2. **Data Validation**: How should we handle TRAC data inconsistencies?
 - dont worry about it right now
3. **Initial Data Collection**: Should we collect all historical data in one batch or incrementally?
 - should be able to handle it in one large batch, curl the html table data. parse to csv. organize by month
## Next Steps
1. **Stakeholder Review**: Get approval on design and scope
2. **TRAC Analysis**: Deep dive into TRAC data structure and availability
3. **Prototype Development**: Build proof-of-concept scraper
4. **Data Structure Validation**: Test with sample historical data
5. **Implementation**: Phase-by-phase development and testing
