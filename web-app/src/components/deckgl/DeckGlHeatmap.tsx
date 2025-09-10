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

// Using a free style from CartoCDN
const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json';

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
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-20 bg-white shadow-md p-4">
        <div className="flex flex-col space-y-2">
          <h1 className="text-2xl font-bold text-gray-900">ICE Detention Facilities Heatmap</h1>
          <p className="text-sm text-gray-600 leading-relaxed">
            This interactive visualization helps bring transparency to immigration detention by mapping facility locations and population data across the United States. 
            Our goal is to make this information more accessible to advocates, researchers, and families seeking to understand the detention system.
          </p>
          <div className="flex flex-wrap gap-4 text-xs text-blue-600">
            <a 
              href="https://github.com/trose/ice-locator-mcp" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-blue-800 underline"
            >
              📁 View Source Code
            </a>
            <a 
              href="https://tracreports.org/immigration/detentionstats/facilities.html" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-blue-800 underline"
            >
              📊 Source Data: TRAC Reports
            </a>
          </div>
        </div>
      </div>

      {/* Map container */}
      <div ref={mapContainerRef} className="absolute top-0 left-0 w-full h-full"></div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-white rounded-lg shadow-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Legend</h3>
        <div className="flex items-center mb-1">
          <div className="w-4 h-4 bg-gray-200 rounded-full mr-2"></div>
          <span className="text-sm">0 population</span>
        </div>
        <div className="flex items-center mb-1">
          <div className="w-4 h-4 bg-yellow-200 rounded-full mr-2"></div>
          <span className="text-sm">1-200 population</span>
        </div>
        <div className="flex items-center mb-1">
          <div className="w-4 h-4 bg-orange-300 rounded-full mr-2"></div>
          <span className="text-sm">201-500 population</span>
        </div>
        <div className="flex items-center mb-1">
          <div className="w-4 h-4 bg-orange-500 rounded-full mr-2"></div>
          <span className="text-sm">501-1000 population</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 bg-red-600 rounded-full mr-2"></div>
          <span className="text-sm">1000+ population</span>
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