import React, { useState, useEffect, useRef } from 'react';
// Import MapboxOverlay for proper MapLibre integration
import { MapboxOverlay } from '@deck.gl/mapbox';
// Import MapLibre
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
// Import the layers we need
import { HeatmapLayer } from '@deck.gl/aggregation-layers';
import { ScatterplotLayer } from '@deck.gl/layers';
import type { Color } from '@deck.gl/core';
// Import embedded data
import { monthlyFacilitiesData } from '../../data/monthlyFacilitiesData';
import { getFacilitiesForMonth, getAvailableMonths, formatMonthYear, getTopFacilitiesForMonth, getTotalPopulationForMonth, type MonthlyFacilityData } from '../../utils/monthlyDataUtils';

// Mobile detection utility
const isMobileDevice = (): boolean => {
  // Check screen size
  if (window.innerWidth <= 768) return true;
  
  // Check user agent
  const userAgent = navigator.userAgent.toLowerCase();
  const mobileKeywords = ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone'];
  return mobileKeywords.some(keyword => userAgent.includes(keyword));
};

// Using Voyager style from CartoCDN - colorful and detailed
const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json';

// Types for our data
interface Facility {
  name: string;
  latitude: number;
  longitude: number;
  address: string;
  population_count: number;
}

interface HeatmapPoint {
  position: [number, number];
  weight: number;
  facility: Facility;
}

// Mobile-responsive initial view state
const getInitialViewState = () => {
  const isMobile = isMobileDevice();
  return {
    longitude: -98.5795,
    latitude: 39.8283,
    zoom: isMobile ? 2.5 : 3.5, // Zoom out more on mobile
    pitch: 0,
    bearing: 0
  };
};

// Color range for the heatmap - properly typed as Color[]
const COLOR_RANGE: Color[] = [
  [255, 255, 204], // Light yellow
  [255, 237, 160],
  [254, 217, 118],
  [254, 178, 76],
  [253, 141, 60],
  [252, 78, 42],
  [227, 26, 28],
  [189, 0, 38],
  [128, 0, 38]  // Dark purple
];

const DeckGlHeatmap: React.FC = () => {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoverInfo, setHoverInfo] = useState<any>(null);
  const [clickInfo, setClickInfo] = useState<any>(null);
  const [isMobile, setIsMobile] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState<string>(monthlyFacilitiesData.meta.l);
  const [topFacilities, setTopFacilities] = useState<MonthlyFacilityData[]>([]);
  const [totalPopulation, setTotalPopulation] = useState<number>(0);
  const [isFacilitiesListExpanded, setIsFacilitiesListExpanded] = useState(false);
  const [hoveredFacilityName, setHoveredFacilityName] = useState<string | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState<{ x: number; y: number } | null>(null);
  const [isMobileUIVisible, setIsMobileUIVisible] = useState(false);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const overlayRef = useRef<MapboxOverlay | null>(null);

  // Mobile detection and data loading
  useEffect(() => {
    // Detect mobile device
    setIsMobile(isMobileDevice());
    
    // Load monthly facilities data for selected month
    try {
      console.log('Loading monthly facilities data for:', selectedMonth);
      console.log('Monthly data metadata:', monthlyFacilitiesData.meta);
      
      const monthlyFacilities = getFacilitiesForMonth(monthlyFacilitiesData, selectedMonth);
      const topFacilitiesData = getTopFacilitiesForMonth(monthlyFacilitiesData, selectedMonth, 8);
      const totalPop = getTotalPopulationForMonth(monthlyFacilitiesData, selectedMonth);
      
      setFacilities(monthlyFacilities);
      setTopFacilities(topFacilitiesData);
      setTotalPopulation(totalPop);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load monthly data:', err);
      setError('Failed to load facilities data: ' + (err as Error).message);
      setLoading(false);
    }
  }, [selectedMonth]);

  // Initialize MapLibre map and DeckGL overlay
  useEffect(() => {
    if (loading || error || !mapContainerRef.current) return;

    const initialViewState = getInitialViewState();
    
    // Create MapLibre map
    mapRef.current = new maplibregl.Map({
      container: mapContainerRef.current,
      style: MAP_STYLE,
      center: [initialViewState.longitude, initialViewState.latitude],
      zoom: initialViewState.zoom,
      pitch: initialViewState.pitch,
      bearing: initialViewState.bearing
    });

    // Add navigation controls
    mapRef.current.addControl(new maplibregl.NavigationControl(), 'top-right');

    // Create MapboxOverlay for DeckGL integration (overlaid mode)
    overlayRef.current = new MapboxOverlay({
      interleaved: false, // Use overlaid mode for better compatibility
      layers: getLayers()
    });

    // Add overlay to map when map is loaded
    mapRef.current.on('load', () => {
      if (mapRef.current && overlayRef.current) {
        mapRef.current.addControl(overlayRef.current);
      }
    });

    // Update layers when facilities change
    // const updateLayers = () => {
    //   if (overlayRef.current) {
    //     overlayRef.current.setProps({ layers: getLayers() });
    //   }
    // };

    // Cleanup
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
      }
    };
  }, [loading, error, facilities]);

  // Get layers for the heatmap
  const getLayers = () => {
    // Convert facilities to heatmap points, filtering out invalid coordinates
    const heatmapData: HeatmapPoint[] = facilities
      .filter(facility => 
        facility.latitude !== 0 && 
        facility.longitude !== 0 &&
        !isNaN(facility.latitude) &&
        !isNaN(facility.longitude) &&
        facility.population_count > 0 // Only include facilities with population
      )
      .map(facility => ({
        position: [facility.longitude, facility.latitude],
        weight: facility.population_count,
        facility: facility
      }));

    console.log('Heatmap data points:', heatmapData.length);
    console.log('Sample heatmap data:', heatmapData.slice(0, 3));

    if (heatmapData.length === 0) {
      return [];
    }

    // Create layers using the functional approach to avoid constructor issues
    return [
      new HeatmapLayer({
        id: 'heatmap-layer',
        data: heatmapData,
        getPosition: (d: HeatmapPoint) => d.position,
        getWeight: (d: HeatmapPoint) => d.weight,
        radiusPixels: 30, // Reduced radius for sparse data
        intensity: 1, // Reduced intensity for sparse data
        threshold: 0.05, // Adjusted threshold for sparse data
        colorRange: COLOR_RANGE,
        aggregation: 'SUM',
        pickable: true
      }),
      new ScatterplotLayer({
        id: 'scatterplot-layer',
        data: heatmapData,
        getPosition: (d: HeatmapPoint) => d.position,
        getRadius: (d: HeatmapPoint) => hoveredFacilityName === d.facility.name ? 8000 : 5000,
        getFillColor: (d: HeatmapPoint) => hoveredFacilityName === d.facility.name ? [255, 165, 0, 255] : [255, 0, 0, 180],
        getLineColor: (d: HeatmapPoint) => hoveredFacilityName === d.facility.name ? [255, 165, 0, 255] : [0, 0, 0, 0],
        getLineWidth: (d: HeatmapPoint) => hoveredFacilityName === d.facility.name ? 3 : 0,
        pickable: true,
        onHover: (info: any) => {
          setHoverInfo(info);
        },
        onClick: (info: any) => {
          setClickInfo(info);
        }
      })
    ];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-lg">Loading heatmap data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error! </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      </div>
    );
  }

  // Check if we have data to display
  const heatmapData: HeatmapPoint[] = facilities
    .filter(facility => 
      facility.latitude !== 0 && 
      facility.longitude !== 0 &&
      !isNaN(facility.latitude) &&
      !isNaN(facility.longitude) &&
      facility.population_count > 0 // Only include facilities with population
    )
    .map(facility => ({
      position: [facility.longitude, facility.latitude],
      weight: facility.population_count,
      facility: facility
    }));

  if (heatmapData.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Warning! </strong>
          <span className="block sm:inline">No facilities with population data found</span>
        </div>
      </div>
    );
  }

  console.log('Creating DeckGL layers:', getLayers());

  return (
    <div className="relative h-full w-full">
      {/* Mobile UI Controls */}
      {isMobile && (
        <div className="absolute top-2 left-2 z-30 flex items-center gap-2">
          {/* Month selector dropdown */}
          <select
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="bg-white/95 backdrop-blur-sm rounded-lg px-2 py-1 shadow-lg border border-gray-200 text-xs text-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {getAvailableMonths(monthlyFacilitiesData).map((month) => (
              <option key={month} value={month}>
                {formatMonthYear(month)}
              </option>
            ))}
          </select>
          
          {/* UI toggle button */}
          <button
            onClick={() => setIsMobileUIVisible(!isMobileUIVisible)}
            className="bg-white/95 backdrop-blur-sm rounded-full p-2 shadow-lg border border-gray-200 hover:bg-white transition-colors"
            aria-label="Toggle UI elements"
          >
            <div className="w-5 h-5 flex flex-col justify-center items-center">
              <div className={`w-3 h-0.5 bg-gray-600 transition-transform ${isMobileUIVisible ? 'rotate-45 translate-y-0.5' : ''}`}></div>
              <div className={`w-3 h-0.5 bg-gray-600 transition-opacity ${isMobileUIVisible ? 'opacity-0' : 'mt-0.5'}`}></div>
              <div className={`w-3 h-0.5 bg-gray-600 transition-transform ${isMobileUIVisible ? '-rotate-45 -translate-y-0.5' : 'mt-0.5'}`}></div>
            </div>
          </button>
        </div>
      )}

      {/* Info Panel - Mobile Responsive */}
      <div className={`absolute z-20 transition-all duration-300 ${
        isMobile 
          ? (isMobileUIVisible ? 'top-2 right-2 left-2 max-w-none opacity-100' : 'top-2 right-2 left-2 max-w-none opacity-0 pointer-events-none')
          : 'top-4 right-4 max-w-sm'
      }`}>
        <div className={`bg-white/95 backdrop-blur-sm rounded-lg shadow-lg border border-gray-200 ${isMobile ? 'p-2' : 'p-4'}`}>
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <h1 className={`font-semibold text-gray-900 ${isMobile ? 'text-sm' : 'text-lg'}`}>ICE Facilities</h1>
          </div>
          <p className={`text-gray-600 leading-relaxed mb-3 ${isMobile ? 'text-xs' : 'text-xs'}`}>
            {isMobile 
              ? 'Interactive heatmap of ICE detention facilities across the US.'
              : 'Interactive heatmap showing detention facilities and population data across the US. Bringing transparency to immigration detention.'
            }
          </p>
          
          {/* Data update info - Mobile Responsive */}
          <div className={`mb-3 bg-blue-50 rounded border-l-2 border-blue-200 ${isMobile ? 'p-1' : 'p-2'}`}>
            <div className={`text-blue-800 ${isMobile ? 'text-xs' : 'text-xs'}`}>
              <div className="font-medium">📅 Historical Data Available</div>
              <div className="text-blue-600">
                {monthlyFacilitiesData.meta.t}
              </div>
              <div className={`text-blue-500 mt-1 ${isMobile ? 'text-xs' : 'text-xs'}`}>
                {isMobile 
                  ? `${monthlyFacilitiesData.meta.f} facilities • ${monthlyFacilitiesData.meta.m.length} months of data`
                  : `${monthlyFacilitiesData.meta.f} facilities • ${monthlyFacilitiesData.meta.m.length} months of historical data (2019-2025)`
                }
              </div>
            </div>
          </div>
          
          <div className={`flex flex-col gap-1 ${isMobile ? 'text-xs' : ''}`}>
            <a 
              href="https://github.com/trose/ice-locator-mcp" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-xs text-blue-600 hover:text-blue-800 hover:underline transition-colors"
            >
              📁 Source Code
            </a>
            <a 
              href="https://tracreports.org/immigration/detentionstats/facilities.html" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-xs text-blue-600 hover:text-blue-800 hover:underline transition-colors"
            >
              📊 Data: TRAC Reports {isMobile ? '(daily)' : '(auto-updated daily)'}
            </a>
          </div>
        </div>
      </div>

      {/* Month Selector - Desktop Only */}
      {!isMobile && (
        <div className="absolute z-20 top-4 left-4">
          <div className="bg-white/95 backdrop-blur-sm rounded-lg shadow-lg border border-gray-200 p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <h3 className="font-medium text-gray-900 text-base">Select Month</h3>
            </div>
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="w-full bg-white border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm p-2"
            >
              {getAvailableMonths(monthlyFacilitiesData).map((month) => (
                <option key={month} value={month}>
                  {formatMonthYear(month)}
                </option>
              ))}
            </select>
            <div className="mt-2 text-gray-500 text-xs">
              Showing data for {formatMonthYear(selectedMonth)}
            </div>
          </div>
        </div>
      )}

      {/* Facility Population Overview - Mobile Responsive */}
      <div className={`absolute z-20 transition-all duration-300 ${
        isMobile 
          ? (isMobileUIVisible ? 'top-20 left-2 right-2 opacity-100' : 'top-20 left-2 right-2 opacity-0 pointer-events-none')
          : 'top-40 left-4'
      }`}>
        <div className={`bg-white/95 backdrop-blur-sm rounded-lg shadow-lg border border-gray-200 ${isMobile ? 'p-2' : 'p-3'}`}>
          <div 
            className="flex items-center gap-2 mb-2 cursor-pointer hover:bg-gray-50 rounded p-1 -m-1"
            onClick={() => setIsFacilitiesListExpanded(!isFacilitiesListExpanded)}
          >
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <h3 className={`font-medium text-gray-900 ${isMobile ? 'text-sm' : 'text-base'}`}>
              Population Overview
            </h3>
            <span className={`text-gray-500 ${isMobile ? 'text-xs' : 'text-sm'}`}>
              ({totalPopulation.toLocaleString()} total)
            </span>
            <button className="ml-auto text-gray-400 hover:text-gray-600">
              {isFacilitiesListExpanded ? '−' : '+'}
            </button>
          </div>
          
          {isFacilitiesListExpanded && (
            <div className={`space-y-1 max-h-64 overflow-y-auto ${isMobile ? 'text-xs' : 'text-sm'}`}>
              {topFacilities.map((facility, index) => (
                <div 
                  key={facility.id} 
                  className={`flex items-center justify-between py-1 px-2 rounded cursor-pointer transition-colors ${
                    hoveredFacilityName === facility.name 
                      ? 'bg-orange-100 border border-orange-300' 
                      : 'hover:bg-gray-50'
                  }`}
                  onMouseEnter={(e) => {
                    setHoveredFacilityName(facility.name);
                    // Get mouse position for tooltip
                    const rect = e.currentTarget.getBoundingClientRect();
                    setTooltipPosition({
                      x: rect.left + rect.width / 2,
                      y: rect.top - 10
                    });
                    // Create hover info for the tooltip
                    const facilityData = facilities.find(f => f.name === facility.name);
                    if (facilityData) {
                      setHoverInfo({
                        object: {
                          facility: facilityData
                        },
                        x: rect.left + rect.width / 2,
                        y: rect.top - 10
                      });
                    }
                  }}
                  onMouseLeave={() => {
                    setHoveredFacilityName(null);
                    setHoverInfo(null);
                    setTooltipPosition(null);
                  }}
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <span className={`font-medium text-gray-600 ${isMobile ? 'text-xs' : 'text-sm'}`}>
                      #{index + 1}
                    </span>
                    <span className="truncate text-gray-900" title={facility.name}>
                      {facility.name}
                    </span>
                  </div>
                  <span className={`font-semibold text-blue-600 ${isMobile ? 'text-xs' : 'text-sm'}`}>
                    {facility.population_count.toLocaleString()}
                  </span>
                </div>
              ))}
              {topFacilities.length === 0 && (
                <div className={`text-gray-500 text-center py-2 ${isMobile ? 'text-xs' : 'text-sm'}`}>
                  No data available for this month
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Map container */}
      <div ref={mapContainerRef} className="absolute top-0 left-0 w-full h-full"></div>

      {/* Legend - Mobile Responsive */}
      <div className={`absolute z-10 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg border border-gray-200 ${isMobile ? 'bottom-2 left-2 right-2 p-2' : 'bottom-4 left-4 p-3'}`}>
        {isMobile ? (
          // Compact mobile legend
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-yellow-200 rounded-full"></div>
              <div className="w-2 h-2 bg-orange-300 rounded-full"></div>
              <div className="w-2 h-2 bg-red-600 rounded-full"></div>
            </div>
            <span className="text-xs text-gray-600">Population</span>
            <span className="text-xs text-gray-500">{heatmapData.length} facilities</span>
          </div>
        ) : (
          // Full desktop legend
          <>
            <h3 className="font-medium text-gray-900 mb-2 text-sm">Population Density</h3>
            <div className="flex items-center mb-1">
              <div className="bg-gray-200 rounded-full mr-2 w-3 h-3"></div>
              <span className="text-xs">0 population</span>
            </div>
            <div className="flex items-center mb-1">
              <div className="bg-yellow-200 rounded-full mr-2 w-3 h-3"></div>
              <span className="text-xs">1-200 population</span>
            </div>
            <div className="flex items-center mb-1">
              <div className="bg-orange-300 rounded-full mr-2 w-3 h-3"></div>
              <span className="text-xs">201-500 population</span>
            </div>
            <div className="flex items-center mb-1">
              <div className="bg-orange-500 rounded-full mr-2 w-3 h-3"></div>
              <span className="text-xs">501-1000 population</span>
            </div>
            <div className="flex items-center">
              <div className="bg-red-600 rounded-full mr-2 w-3 h-3"></div>
              <span className="text-xs">1000+ population</span>
            </div>
            <div className="mt-3 text-gray-500 text-xs">
              Showing {heatmapData.length} facilities with population data
            </div>
          </>
        )}
      </div>

      {/* Hover tooltip - Mobile Responsive */}
      {hoverInfo && hoverInfo.object && (
        <div 
          style={{
            position: 'fixed',
            left: tooltipPosition ? tooltipPosition.x : (isMobile ? '10px' : '20px'),
            top: tooltipPosition ? tooltipPosition.y : (isMobile ? '10px' : '20px'),
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            padding: isMobile ? '6px' : '8px',
            borderRadius: '4px',
            pointerEvents: 'none',
            fontSize: isMobile ? '10px' : '12px',
            zIndex: 30,
            maxWidth: isMobile ? '200px' : 'none',
            transform: tooltipPosition ? 'translateX(-50%)' : 'none'
          }}
        >
          <div className="font-semibold">{hoverInfo.object.facility.name}</div>
          <div>{hoverInfo.object.facility.address || 'No address available'}</div>
          <div>{hoverInfo.object.facility.population_count} population</div>
        </div>
      )}
      
      {/* Click popup - Mobile Responsive */}
      {clickInfo && clickInfo.object && (
        <div 
          style={{
            position: 'absolute',
            left: isMobile ? '10px' : clickInfo.x,
            top: isMobile ? '50%' : clickInfo.y,
            transform: isMobile ? 'translateY(-50%)' : 'none',
            background: 'white',
            padding: isMobile ? '8px' : '12px',
            borderRadius: '4px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
            zIndex: 30,
            minWidth: isMobile ? 'calc(100vw - 20px)' : '200px',
            maxWidth: isMobile ? 'calc(100vw - 20px)' : 'none'
          }}
        >
          <div className={`font-semibold ${isMobile ? 'text-sm' : 'text-lg'}`}>{clickInfo.object.facility.name}</div>
          <div className={`text-gray-600 ${isMobile ? 'text-xs' : ''}`}>{clickInfo.object.facility.address || 'No address available'}</div>
          <div className="mt-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full font-medium bg-red-100 text-red-800 ${isMobile ? 'text-xs' : 'text-xs'}`}>
              {clickInfo.object.facility.population_count} population
            </span>
          </div>
          <button 
            onClick={() => setClickInfo(null)}
            className={`absolute top-1 right-1 text-gray-500 hover:text-gray-700 ${isMobile ? 'text-lg' : ''}`}
          >
            ×
          </button>
        </div>
      )}
    </div>
  );
};

export default DeckGlHeatmap;