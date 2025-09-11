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
import facilitiesData from '../../data/facilities.json';

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

const INITIAL_VIEW_STATE = {
  longitude: -98.5795,
  latitude: 39.8283,
  zoom: 3.5,
  pitch: 0,
  bearing: 0
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
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const overlayRef = useRef<MapboxOverlay | null>(null);

  // Load embedded facilities data
  useEffect(() => {
    try {
      console.log('Loading embedded facilities data...');
      console.log('Data metadata:', facilitiesData.metadata);
      console.log('Sample facilities data:', facilitiesData.facilities.slice(0, 3));
      
      setFacilities(facilitiesData.facilities);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load embedded data:', err);
      setError('Failed to load facilities data: ' + (err as Error).message);
      setLoading(false);
    }
  }, []);

  // Initialize MapLibre map and DeckGL overlay
  useEffect(() => {
    if (loading || error || !mapContainerRef.current) return;

    // Create MapLibre map
    mapRef.current = new maplibregl.Map({
      container: mapContainerRef.current,
      style: MAP_STYLE,
      center: [INITIAL_VIEW_STATE.longitude, INITIAL_VIEW_STATE.latitude],
      zoom: INITIAL_VIEW_STATE.zoom,
      pitch: INITIAL_VIEW_STATE.pitch,
      bearing: INITIAL_VIEW_STATE.bearing
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
        getRadius: 5000, // Reduced radius for sparse data
        getFillColor: [255, 0, 0, 180],
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
      {/* Info Panel */}
      <div className="absolute top-4 right-4 z-20 max-w-sm">
        <div className="bg-white/95 backdrop-blur-sm rounded-lg shadow-lg border border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <h1 className="text-lg font-semibold text-gray-900">ICE Facilities</h1>
          </div>
          <p className="text-xs text-gray-600 leading-relaxed mb-3">
            Interactive heatmap showing detention facilities and population data across the US. 
            Bringing transparency to immigration detention.
          </p>
          
          {/* Data update info */}
          <div className="mb-3 p-2 bg-blue-50 rounded border-l-2 border-blue-200">
            <div className="text-xs text-blue-800">
              <div className="font-medium">📅 Latest Data Update</div>
              <div className="text-blue-600">
                {facilitiesData.metadata?.exported_at || 'Unknown'}
              </div>
              <div className="text-blue-500 text-xs mt-1">
                {facilitiesData.metadata?.total_facilities || 0} facilities • {facilitiesData.metadata?.total_population?.toLocaleString() || 0} detainees
              </div>
            </div>
          </div>
          
          <div className="flex flex-col gap-1">
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
              📊 Data: TRAC Reports (auto-updated daily)
            </a>
          </div>
        </div>
      </div>

      {/* Map container */}
      <div ref={mapContainerRef} className="absolute top-0 left-0 w-full h-full"></div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg border border-gray-200 p-3">
        <h3 className="text-sm font-medium text-gray-900 mb-2">Population Density</h3>
        <div className="flex items-center mb-1">
          <div className="w-3 h-3 bg-gray-200 rounded-full mr-2"></div>
          <span className="text-xs">0 population</span>
        </div>
        <div className="flex items-center mb-1">
          <div className="w-3 h-3 bg-yellow-200 rounded-full mr-2"></div>
          <span className="text-xs">1-200 population</span>
        </div>
        <div className="flex items-center mb-1">
          <div className="w-3 h-3 bg-orange-300 rounded-full mr-2"></div>
          <span className="text-xs">201-500 population</span>
        </div>
        <div className="flex items-center mb-1">
          <div className="w-3 h-3 bg-orange-500 rounded-full mr-2"></div>
          <span className="text-xs">501-1000 population</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-red-600 rounded-full mr-2"></div>
          <span className="text-xs">1000+ population</span>
        </div>
        <div className="mt-3 text-xs text-gray-500">
          Showing {heatmapData.length} facilities with population data
        </div>
      </div>

      {/* Hover tooltip */}
      {hoverInfo && hoverInfo.object && (
        <div 
          style={{
            position: 'absolute',
            left: hoverInfo.x + 10,
            top: hoverInfo.y + 10,
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            padding: '8px',
            borderRadius: '4px',
            pointerEvents: 'none',
            fontSize: '12px',
            zIndex: 30
          }}
        >
          <div className="font-semibold">{hoverInfo.object.facility.name}</div>
          <div>{hoverInfo.object.facility.address || 'No address available'}</div>
          <div>{hoverInfo.object.facility.population_count} population</div>
        </div>
      )}
      
      {/* Click popup */}
      {clickInfo && clickInfo.object && (
        <div 
          style={{
            position: 'absolute',
            left: clickInfo.x,
            top: clickInfo.y,
            background: 'white',
            padding: '12px',
            borderRadius: '4px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
            zIndex: 30,
            minWidth: '200px'
          }}
        >
          <div className="font-semibold text-lg">{clickInfo.object.facility.name}</div>
          <div className="text-gray-600">{clickInfo.object.facility.address || 'No address available'}</div>
          <div className="mt-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
              {clickInfo.object.facility.population_count} population
            </span>
          </div>
          <button 
            onClick={() => setClickInfo(null)}
            className="absolute top-1 right-1 text-gray-500 hover:text-gray-700"
          >
            ×
          </button>
        </div>
      )}
    </div>
  );
};

export default DeckGlHeatmap;