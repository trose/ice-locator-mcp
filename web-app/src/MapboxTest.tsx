import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4M29iazA2Z2gycXA4N2pmbDZmangifQ.-g_vE53SD2WrJ6tFX7QHmA';

const MapboxTest: React.FC = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    try {
      const map = new mapboxgl.Map({
        container: mapContainerRef.current,
        style: 'mapbox://styles/mapbox/light-v10',
        center: [-74.5, 40],
        zoom: 9
      });

      mapRef.current = map;

      map.on('load', () => {
        console.log('Mapbox test map loaded successfully');
      });

      map.on('error', (e) => {
        console.error('Mapbox test map error:', e);
      });

      return () => {
        if (mapRef.current) {
          mapRef.current.remove();
        }
      };
    } catch (error) {
      console.error('Error initializing Mapbox test map:', error);
    }
  }, []);

  return (
    <div className="h-screen w-screen">
      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
};

export default MapboxTest;