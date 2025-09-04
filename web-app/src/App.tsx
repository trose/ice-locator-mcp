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
  detainee_count: number;
}

const App: React.FC = () => {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch heatmap data from our API
  useEffect(() => {
    const fetchHeatmapData = async () => {
      try {
        // In a real implementation, this would point to our actual API
        // For now, we'll use mock data
        const mockData: Facility[] = [
          {
            id: 1,
            name: "Adams County Correctional Center",
            latitude: 31.4839,
            longitude: -91.5140,
            address: "Natchez, MS",
            detainee_count: 15
          },
          {
            id: 2,
            name: "Baltimore Field Office",
            latitude: 39.2904,
            longitude: -76.6122,
            address: "Baltimore, MD",
            detainee_count: 8
          },
          {
            id: 3,
            name: "Broward Transitional Center",
            latitude: 26.1224,
            longitude: -80.1368,
            address: "Miami, FL",
            detainee_count: 22
          },
          {
            id: 4,
            name: "Chicago Field Office",
            latitude: 41.8781,
            longitude: -87.6298,
            address: "Chicago, IL",
            detainee_count: 12
          },
          {
            id: 5,
            name: "Cibola County Correctional Center",
            latitude: 34.9167,
            longitude: -107.6500,
            address: "Milan, NM",
            detainee_count: 18
          }
        ];

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setFacilities(mockData);
        setLoading(false);
      } catch (err) {
        setError('Failed to load heatmap data');
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
                          {facility.detainee_count} detainees
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
                            {facility.detainee_count} detainees
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