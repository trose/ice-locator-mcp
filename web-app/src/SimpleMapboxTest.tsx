import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

// Using a free style from CartoCDN
const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json';

const SimpleMapboxTest: React.FC = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    try {
      const map = new maplibregl.Map({
        container: mapContainerRef.current,
        style: MAP_STYLE,
        center: [-74.5, 40],
        zoom: 9
      });

      mapRef.current = map;

      map.on('load', () => {
        console.log('MapLibre test map loaded successfully');
      });

      map.on('error', (e) => {
        console.error('MapLibre test map error:', e);
      });

      return () => {
        if (mapRef.current) {
          mapRef.current.remove();
        }
      };
    } catch (error) {
      console.error('Error initializing MapLibre test map:', error);
    }
  }, []);

  return (
    <div className="h-screen w-screen">
      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
};

export default SimpleMapboxTest;