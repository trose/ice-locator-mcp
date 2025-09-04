import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Types for our data
interface Facility {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  address: string;
  current_detainee_count: number; // Updated to match API response
}

const App: React.FC = () => {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch heatmap data from our API
  useEffect(() => {
    const fetchHeatmapData = async () => {
      try {
        // Use the real API endpoint
        const response = await fetch('http://localhost:8082/api/heatmap-data');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-lg">Loading heatmap data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error! </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">ICE Detainee Locator</h1>
          <p className="mt-1 text-sm text-gray-500">Heatmap view of detainee locations</p>
        </div>
      </header>

      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {/* Map Container */}
          <div className="px-4 py-6 sm:px-0">
            <div className="rounded-lg overflow-hidden shadow-lg h-[600px]">
              <MapContainer 
                center={[39.8283, -98.5795]} // Center of US
                zoom={4} 
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                {facilities.map(facility => (
                  <Marker 
                    key={facility.id} 
                    position={[facility.latitude, facility.longitude]}
                  >
                    <Popup>
                      <div className="font-semibold">{facility.name}</div>
                      <div className="text-sm text-gray-600">{facility.address}</div>
                      <div className="mt-1">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          {facility.current_detainee_count} detainees
                        </span>
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>
            </div>
          </div>

          {/* Facilities List */}
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Facilities</h2>
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {facilities.map(facility => (
                  <li key={facility.id}>
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div className="text-sm font-medium text-indigo-600 truncate">
                          {facility.name}
                        </div>
                        <div className="ml-2 flex-shrink-0 flex">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                            {facility.current_detainee_count} detainees
                          </span>
                        </div>
                      </div>
                      <div className="mt-2 sm:flex sm:justify-between">
                        <div className="sm:flex">
                          <p className="flex items-center text-sm text-gray-500">
                            {facility.address}
                          </p>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                          <span>
                            {facility.latitude.toFixed(4)}, {facility.longitude.toFixed(4)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white mt-8">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            This tool helps locate detained individuals in ICE custody.
          </p>
          <p className="mt-1 text-center text-sm text-gray-500">
            <a href="https://www.ice.gov/contact" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-500">
              Visit ICE.gov for official information
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;