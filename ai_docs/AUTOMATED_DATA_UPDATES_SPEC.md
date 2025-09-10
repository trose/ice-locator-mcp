# Automated Data Updates Specification

## Overview
Design a secure, automated system to update ICE facility data from TRAC Reports and deploy updated heatmap applications without compromising repository security.

## Current Architecture Analysis

### Data Flow
1. **Source**: TRAC Reports (https://tracreports.org/immigration/detentionstats/facilities.json)
2. **Current Storage**: Embedded JSON in `web-app/src/data/facilities.json`
3. **Deployment**: Static site on Vercel with embedded data
4. **Update Process**: Manual (currently)

### Security Concerns
- ❌ **Direct main branch commits from cron jobs** = High risk
- ❌ **Automated git operations** = Potential for malicious code injection
- ❌ **Repository write access from external services** = Security vulnerability

## Architecture Options

### Option 1: External Data API + Dynamic Loading
**Approach**: Move data to external storage, load dynamically in frontend

**Pros**:
- ✅ No repository commits needed
- ✅ Real-time data updates
- ✅ Separation of concerns
- ✅ Can implement caching strategies

**Cons**:
- ❌ Requires external infrastructure
- ❌ Network dependency for data loading
- ❌ More complex deployment
- ❌ Potential CORS issues

**Implementation**:
```
TRAC Reports → External API/DB → Frontend (fetch on load)
```

### Option 2: Vercel Edge Functions + KV Storage
**Approach**: Use Vercel's serverless functions and KV storage

**Pros**:
- ✅ Integrated with Vercel ecosystem
- ✅ Serverless scaling
- ✅ Built-in caching
- ✅ No external dependencies

**Cons**:
- ❌ Vercel-specific (vendor lock-in)
- ❌ Additional costs for KV storage
- ❌ More complex than static approach

**Implementation**:
```
TRAC Reports → Vercel Cron → KV Storage → Edge Function → Frontend
```

### Option 3: GitHub Actions + Pull Request Workflow
**Approach**: Use GitHub Actions for secure, reviewable updates

**Pros**:
- ✅ Secure (no direct main branch access)
- ✅ Reviewable changes
- ✅ Audit trail
- ✅ Can implement approval workflows
- ✅ Uses existing GitHub infrastructure

**Cons**:
- ❌ Requires manual approval (unless auto-merge enabled)
- ❌ More complex workflow
- ❌ GitHub Actions minutes usage

**Implementation**:
```
TRAC Reports → GitHub Action → PR → Review → Merge → Deploy
```

### Option 4: Hybrid: External Storage + Build-time Embedding
**Approach**: Store data externally, embed during build process

**Pros**:
- ✅ Best of both worlds
- ✅ Static site benefits
- ✅ Automated updates
- ✅ Fallback to external API if needed

**Cons**:
- ❌ More complex build process
- ❌ Requires external storage
- ❌ Build-time dependency

**Implementation**:
```
TRAC Reports → External Storage → Build Process → Embedded JSON → Deploy
```

## Recommended Solution: Option 3 (GitHub Actions + PR Workflow)

### Why This Approach?
1. **Security**: No direct repository access from external services
2. **Transparency**: All changes are reviewable and auditable
3. **Reliability**: Uses proven GitHub infrastructure
4. **Flexibility**: Can implement approval workflows or auto-merge
5. **Cost-effective**: Uses existing GitHub Actions minutes

### Implementation Plan

#### Phase 1: GitHub Actions Workflow
```yaml
# .github/workflows/update-facility-data.yml
name: Update Facility Data
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install requests beautifulsoup4 geopy
      
      - name: Fetch TRAC data
        run: python scripts/update_facility_data.py
      
      - name: Check for changes
        id: changes
        run: |
          if git diff --quiet web-app/src/data/facilities.json; then
            echo "changed=false" >> $GITHUB_OUTPUT
          else
            echo "changed=true" >> $GITHUB_OUTPUT
          fi
      
      - name: Create Pull Request
        if: steps.changes.outputs.changed == 'true'
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: "Update facility data from TRAC Reports"
          title: "Automated: Update ICE facility data"
          body: |
            This PR contains updated facility data from TRAC Reports.
            
            **Changes:**
            - Updated facility population counts
            - Updated facility metadata
            - Data fetched on: ${{ github.run_number }}
            
            **Review Checklist:**
            - [ ] Data looks reasonable
            - [ ] No unexpected changes
            - [ ] Metadata is correct
          branch: automated-data-update-${{ github.run_number }}
          delete-branch: true
```

#### Phase 2: Data Update Script
```python
# scripts/update_facility_data.py
#!/usr/bin/env python3
"""
Automated facility data updater for GitHub Actions.
Fetches data from TRAC Reports and updates embedded JSON.
"""

import requests
import json
import os
from datetime import datetime
from typing import List, Dict

class FacilityDataUpdater:
    def __init__(self):
        self.trac_url = "https://tracreports.org/immigration/detentionstats/facilities.json"
        self.output_path = "web-app/src/data/facilities.json"
    
    def fetch_trac_data(self) -> List[Dict]:
        """Fetch latest data from TRAC Reports."""
        try:
            response = requests.get(self.trac_url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching TRAC data: {e}")
            raise
    
    def process_facility_data(self, raw_data: List[Dict]) -> Dict:
        """Process raw TRAC data into our format."""
        facilities = []
        total_population = 0
        
        for entry in raw_data:
            if entry.get('name') == 'Total':
                continue
                
            facility = {
                "name": entry.get('name', ''),
                "latitude": entry.get('latitude', 0),
                "longitude": entry.get('longitude', 0),
                "address": entry.get('address', ''),
                "population_count": entry.get('current_detainee_count', 0)
            }
            
            facilities.append(facility)
            total_population += facility['population_count']
        
        return {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "total_facilities": len(facilities),
                "total_population": total_population,
                "description": "ICE Detention Facilities - Population Data",
                "source": "TRAC Reports",
                "source_url": self.trac_url
            },
            "facilities": facilities
        }
    
    def update_facilities_file(self, data: Dict):
        """Update the facilities JSON file."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        with open(self.output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Updated {self.output_path}")
        print(f"Total facilities: {data['metadata']['total_facilities']}")
        print(f"Total population: {data['metadata']['total_population']}")
    
    def run(self):
        """Main execution method."""
        print("🔄 Starting facility data update...")
        
        # Fetch data
        raw_data = self.fetch_trac_data()
        print(f"📊 Fetched {len(raw_data)} records from TRAC")
        
        # Process data
        processed_data = self.process_facility_data(raw_data)
        
        # Update file
        self.update_facilities_file(processed_data)
        
        print("✅ Facility data update complete!")

if __name__ == "__main__":
    updater = FacilityDataUpdater()
    updater.run()
```

#### Phase 3: Auto-merge Configuration (Optional)
```yaml
# .github/workflows/auto-merge-data-updates.yml
name: Auto-merge Data Updates
on:
  pull_request:
    types: [opened, synchronize]
    paths:
      - 'web-app/src/data/facilities.json'

jobs:
  auto-merge:
    if: github.actor == 'github-actions[bot]' && contains(github.event.pull_request.title, 'Automated: Update ICE facility data')
    runs-on: ubuntu-latest
    steps:
      - name: Auto-merge PR
        uses: hmarr/auto-approve-action@v2
        with:
          github-token: "${{ secrets.GITHUB_TOKEN }}"
      
      - name: Enable auto-merge
        uses: peter-evans/enable-pull-request-automerge@v2
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          pull-request-number: ${{ github.event.pull_request.number }}
          merge-method: squash
```

### Alternative: Option 2 (Vercel Edge Functions)

If GitHub Actions approach is not preferred, here's the Vercel Edge Function approach:

#### Vercel Cron Job
```javascript
// api/update-facility-data.js
import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  // Verify cron secret
  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  try {
    // Fetch TRAC data
    const response = await fetch('https://tracreports.org/immigration/detentionstats/facilities.json');
    const data = await response.json();
    
    // Process and store in KV
    const processedData = processFacilityData(data);
    await kv.set('facility-data', JSON.stringify(processedData));
    
    res.status(200).json({ success: true, updated: new Date().toISOString() });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

function processFacilityData(rawData) {
  // Same processing logic as Python script
  // ...
}
```

#### Frontend Data Loading
```typescript
// src/hooks/useFacilityData.ts
import { useState, useEffect } from 'react';

export const useFacilityData = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/facility-data');
        const facilityData = await response.json();
        setData(facilityData);
      } catch (err) {
        setError(err);
        // Fallback to embedded data
        const embeddedData = await import('../data/facilities.json');
        setData(embeddedData.default);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  return { data, loading, error };
};
```

## Security Considerations

### GitHub Actions Approach
- ✅ No external repository access
- ✅ All changes are reviewable
- ✅ Audit trail in GitHub
- ✅ Can implement approval workflows
- ✅ Uses GitHub's secure token system

### Vercel Edge Functions Approach
- ✅ No repository access needed
- ✅ Serverless and scalable
- ✅ Built-in security features
- ⚠️ Requires Vercel KV storage costs
- ⚠️ Vendor lock-in to Vercel

## Implementation Timeline

### Week 1: GitHub Actions Setup
- [ ] Create GitHub Actions workflow
- [ ] Implement data fetching script
- [ ] Test with manual trigger
- [ ] Set up PR creation workflow

### Week 2: Testing & Refinement
- [ ] Test automated PR creation
- [ ] Implement data validation
- [ ] Add error handling and notifications
- [ ] Test auto-merge (if desired)

### Week 3: Production Deployment
- [ ] Deploy to production
- [ ] Monitor first automated runs
- [ ] Set up alerting for failures
- [ ] Document maintenance procedures

## Monitoring & Alerting

### Success Metrics
- Data update frequency (daily)
- PR creation success rate
- Data accuracy validation
- Deployment success rate

### Failure Scenarios
- TRAC Reports API unavailable
- Data format changes
- GitHub Actions failures
- Deployment failures

### Alerting
- GitHub Actions failure notifications
- Data validation failures
- Unusual data changes (spike detection)
- Deployment failures

## Cost Analysis

### GitHub Actions
- **Cost**: Included in GitHub Pro/Team plans
- **Usage**: ~5 minutes per day for data updates
- **Total**: ~150 minutes/month (well within limits)

### Vercel Edge Functions
- **Cost**: $0.20 per million requests
- **KV Storage**: $0.50 per GB per month
- **Estimated**: <$5/month for this use case

## Recommendation

**Implement Option 3 (GitHub Actions + PR Workflow)** because:

1. **Security**: Most secure approach with no external repository access
2. **Transparency**: All changes are reviewable and auditable
3. **Reliability**: Uses proven GitHub infrastructure
4. **Cost-effective**: Uses existing GitHub Actions minutes
5. **Flexibility**: Can implement approval workflows or auto-merge as needed

This approach provides the best balance of security, transparency, and automation while maintaining the simplicity of the current static site architecture.
