# ICE Detention Facilities Heatmap - Immigration Data Visualization

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/trose/ice-locator-mcp)

An interactive, real-time heatmap visualization of Immigration and Customs Enforcement (ICE) detention facilities across the United States. This web application provides transparency into immigration detention statistics, facility locations, and population trends from 2019-2025.

## 🗺️ Live Demo

**[View the Interactive Heatmap →](https://ice-locator-mcp.vercel.app/)**

## 📊 Key Features

### Data Visualization
- **Interactive Heatmap**: Real-time visualization of 186+ ICE detention facilities
- **Population Density Mapping**: Color-coded facility populations with dynamic scaling
- **Historical Data**: Monthly population trends from 2019-2025
- **Facility Details**: Comprehensive information including addresses, coordinates, and current populations

### User Experience
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Mobile-First**: Touch-friendly interface with collapsible UI elements
- **Real-Time Updates**: Monthly data synchronization with TRAC Reports
- **Accessibility**: Screen reader compatible with proper ARIA labels

### Technical Features
- **Self-Contained**: No backend required - all data embedded in frontend
- **Fast Loading**: Optimized bundle size with lazy loading
- **SEO Optimized**: Structured data, meta tags, and sitemap for search engines
- **Performance**: Built with Vite for optimal build times and hot reloading

## 🏗️ Technology Stack

- **Frontend**: React 18 with TypeScript
- **Mapping**: Deck.gl + MapLibre GL JS
- **Styling**: Tailwind CSS with responsive design
- **Build Tool**: Vite for fast development and optimized builds
- **Deployment**: Vercel with automatic deployments
- **Data Source**: TRAC Reports (Transactional Records Access Clearinghouse)

## 📈 Data Coverage

### Facility Statistics
- **186+ Active Facilities**: Comprehensive coverage of ICE detention centers
- **Population Range**: 0-4,000+ detainees per facility
- **Geographic Coverage**: All 50 states and territories
- **Data Freshness**: Updated monthly with latest TRAC Reports data

### Historical Trends
- **Time Period**: 2019-2025 (ongoing)
- **Update Frequency**: Monthly synchronization
- **Data Points**: Average daily population per facility per month
- **Total Records**: 10,000+ monthly population data points

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (recommended: Node.js 20+)
- npm or yarn package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/trose/ice-locator-mcp.git
cd ice-locator-mcp/web-app

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5173 in your browser
```

### Development Commands

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## 🌐 Deployment

### Vercel (Recommended)

1. **Connect Repository**: Link your GitHub repository to Vercel
2. **Configure Build**:
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
3. **Deploy**: Automatic deployments on every push to main branch

### Other Platforms

The app is a static site and can be deployed to any static hosting service:
- **Netlify**: Connect repository and set build command to `npm run build`
- **GitHub Pages**: Use GitHub Actions to build and deploy
- **AWS S3**: Upload the `dist` folder to an S3 bucket with static hosting
- **Firebase Hosting**: Use Firebase CLI to deploy the built application

## 📊 Data Management

### Updating Facility Data

The application uses automated data collection from TRAC Reports:

```bash
# Run data collection (from project root)
python scripts/collect_monthly_population_data.py

# Export optimized data for frontend
python scripts/export_facilities_for_frontend.py

# Update TypeScript data file
python scripts/update_monthly_data_ts.py
```

### Data Sources
- **Primary**: [TRAC Reports](https://trac.syr.edu/) - Syracuse University
- **Format**: JSON API with monthly population statistics
- **Update Schedule**: Automated monthly collection via GitHub Actions
- **Validation**: Entity discernment algorithm prevents duplicate records

## 🎯 SEO & Performance

### Search Engine Optimization
- **Structured Data**: JSON-LD schema markup for rich search results
- **Meta Tags**: Comprehensive Open Graph and Twitter Card support
- **Sitemap**: XML sitemap for search engine indexing
- **Robots.txt**: Proper crawling directives for search engines

### Performance Metrics
- **Lighthouse Score**: 95+ across all categories
- **Bundle Size**: Optimized with code splitting and tree shaking
- **Loading Speed**: <2s initial load time on 3G networks
- **Core Web Vitals**: Excellent LCP, FID, and CLS scores

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file for local development:

```env
# Optional: Custom map tile server
VITE_MAP_TILE_URL=https://your-tile-server.com/{z}/{x}/{y}.png

# Optional: Analytics tracking
VITE_GA_TRACKING_ID=your-google-analytics-id
```

### Customization

- **Map Styling**: Modify `src/components/deckgl/DeckGlHeatmap.tsx`
- **Color Scheme**: Update Tailwind classes in component files
- **Data Format**: Adjust TypeScript interfaces in `src/types/`
- **Build Settings**: Configure Vite options in `vite.config.ts`

## 📱 Mobile Optimization

### Responsive Features
- **Collapsible UI**: Mobile-first design with expandable panels
- **Touch Gestures**: Pinch-to-zoom and pan support
- **Optimized Controls**: Large touch targets and intuitive navigation
- **Performance**: Reduced bundle size for mobile networks

### Browser Support
- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile Browsers**: iOS Safari 14+, Chrome Mobile 90+
- **Progressive Enhancement**: Graceful degradation for older browsers

## 🤝 Contributing

We welcome contributions to improve the ICE detention facility heatmap:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and test thoroughly
4. Commit with descriptive messages
5. Push to your fork and submit a pull request

### Areas for Contribution
- **Data Accuracy**: Help validate facility information
- **UI/UX Improvements**: Enhance mobile experience or accessibility
- **Performance**: Optimize bundle size or loading times
- **Documentation**: Improve README or add code comments
- **Testing**: Add unit tests or integration tests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **TRAC Reports**: Syracuse University for providing comprehensive immigration data
- **Deck.gl**: Uber's visualization framework for the interactive heatmap
- **MapLibre GL**: Open-source mapping library for base maps
- **Vercel**: Hosting platform for seamless deployment

## 📞 Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/trose/ice-locator-mcp/issues)
- **Discussions**: Join community discussions in [GitHub Discussions](https://github.com/trose/ice-locator-mcp/discussions)
- **Email**: Contact the maintainers for security issues or private inquiries

---

**Built with ❤️ for immigration transparency and data accessibility**