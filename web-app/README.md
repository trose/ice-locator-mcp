# ICE Detention Facilities Heatmap

A React-based heatmap visualization of ICE detention facilities across the United States.

## Features

- Interactive heatmap showing facility populations
- 186 facilities with comprehensive population data
- Built with DeckGL and MapLibre GL
- Self-contained (no backend required)
- Optimized for Vercel deployment

## Data

The app includes embedded data for 186 ICE detention facilities with:
- Facility names and addresses
- GPS coordinates (latitude/longitude)
- Population counts
- Total population: 62,005 detainees

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Deployment

This app is optimized for Vercel deployment:

1. Connect your GitHub repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Deploy!

## Data Updates

To update the facility data:

1. Run the data export script: `python export_facilities_for_frontend.py`
2. Commit the updated `src/data/facilities.json` file
3. Redeploy to Vercel

## Cost

- **Vercel**: Free tier (100GB bandwidth, unlimited static sites)
- **No database costs**: Data is embedded in the frontend
- **No API costs**: Self-contained application