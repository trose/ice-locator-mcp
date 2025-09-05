import React, { useState, useEffect, useRef } from 'react';
// Import DeckGL components
import DeckGL from '@deck.gl/react';
import { MapView } from '@deck.gl/core';
// Import MapboxOverlay for proper MapLibre integration
import { MapboxOverlay } from '@deck.gl/mapbox';
// Import MapLibre
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
// Import the layers we need
import { HeatmapLayer } from '@deck.gl/aggregation-layers';
import { ScatterplotLayer } from '@deck.gl/layers';
import type { Color } from '@deck.gl/core';

// Using a free style from CartoCDN
const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json';

// Types for our data
interface Facility {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  address: string;
  detainee_count: number;
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

  // Fetch heatmap data from our API
  useEffect(() => {
    const fetchHeatmapData = async () => {
      try {
        console.log('Fetching heatmap data from API...');
        // Use the real API endpoint
        const response = await fetch('http://localhost:8082/api/heatmap-data');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Fetched facilities data:', data.length, 'facilities');
        console.log('Sample facilities data:', data.slice(0, 3));
        
        // Log facilities with non-zero detainee counts
        const facilitiesWithDetainees = data.filter((f: Facility) => f.detainee_count > 0);
        console.log('Facilities with detainees:', facilitiesWithDetainees.length);
        console.log('Sample facilities with detainees:', facilitiesWithDetainees.slice(0, 3));
        
        setFacilities(data);
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch heatmap data:', err);
        setError('Failed to load heatmap data: ' + (err as Error).message);
        setLoading(false);
      }
    };

    fetchHeatmapData();
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
    const updateLayers = () => {
      if (overlayRef.current) {
        overlayRef.current.setProps({ layers: getLayers() });
      }
    };

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
        facility.detainee_count > 0 // Only include facilities with detainees
      )
      .map(facility => ({
        position: [facility.longitude, facility.latitude],
        weight: facility.detainee_count,
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
      facility.detainee_count > 0 // Only include facilities with detainees
    )
    .map(facility => ({
      position: [facility.longitude, facility.latitude],
      weight: facility.detainee_count,
      facility: facility
    }));

  if (heatmapData.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Warning! </strong>
          <span className="block sm:inline">No facilities with detainees found</span>
        </div>
      </div>
    );
  }

  console.log('Creating DeckGL layers:', getLayers());

  return (
    <div className="relative h-full w-full">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-20 bg-white shadow-md p-4">
        <h1 className="text-2xl font-bold text-gray-900">ICE Detainee Locator</h1>
        <p className="text-sm text-gray-500">Heatmap view of detainee locations</p>
      </div>

      {/* Map container */}
      <div ref={mapContainerRef} className="absolute top-0 left-0 w-full h-full"></div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-white rounded-lg shadow-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Legend</h3>
        <div className="flex items-center mb-1">
          <div className="w-4 h-4 bg-gray-200 rounded-full mr-2"></div>
          <span className="text-sm">0 detainees</span>
        </div>
        <div className="flex items-center mb-1">
          <div className="w-4 h-4 bg-yellow-200 rounded-full mr-2"></div>
          <span className="text-sm">1-5 detainees</span>
        </div>
        <div className="flex items-center mb-1">
          <div className="w-4 h-4 bg-orange-300 rounded-full mr-2"></div>
          <span className="text-sm">6-10 detainees</span>
        </div>
        <div className="flex items-center mb-1">
          <div className="w-4 h-4 bg-orange-500 rounded-full mr-2"></div>
          <span className="text-sm">11-20 detainees</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 bg-red-600 rounded-full mr-2"></div>
          <span className="text-sm">21+ detainees</span>
        </div>
        <div className="mt-3 text-xs text-gray-500">
          Showing {heatmapData.length} facilities with detainees
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
          <div>{hoverInfo.object.facility.detainee_count} detainees</div>
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
              {clickInfo.object.facility.detainee_count} detainees
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