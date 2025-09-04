import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ActivityIndicator, 
  Alert,
  Dimensions,
  ScrollView
} from 'react-native';
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import HeatmapAPI from './HeatmapAPI';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

interface Facility {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  address: string;
  current_detainee_count: number;
}

const HeatmapView = ({ isConnected }: { isConnected: boolean }) => {
  const [heatmapData, setHeatmapData] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isConnected) {
      loadHeatmapData();
    }
  }, [isConnected]);

  const loadHeatmapData = async () => {
    if (!isConnected) {
      setError('Not connected to server. Please wait for connection.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await HeatmapAPI.getHeatmapData();
      setHeatmapData(data);
      setError(null);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to load heatmap data';
      setError(errorMessage);
      console.error('Heatmap error:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = () => {
    HeatmapAPI.clearCache();
    loadHeatmapData();
  };

  // Calculate initial region for the map
  const calculateInitialRegion = () => {
    if (heatmapData.length === 0) {
      // Default to US center
      return {
        latitude: 39.8283,
        longitude: -98.5795,
        latitudeDelta: 50,
        longitudeDelta: 50,
      };
    }

    // Calculate bounds based on facilities
    let minLat = heatmapData[0].latitude;
    let maxLat = heatmapData[0].latitude;
    let minLng = heatmapData[0].longitude;
    let maxLng = heatmapData[0].longitude;

    heatmapData.forEach(facility => {
      if (facility.latitude < minLat) minLat = facility.latitude;
      if (facility.latitude > maxLat) maxLat = facility.latitude;
      if (facility.longitude < minLng) minLng = facility.longitude;
      if (facility.longitude > maxLng) maxLng = facility.longitude;
    });

    const latitudeDelta = (maxLat - minLat) * 1.2; // Add some padding
    const longitudeDelta = (maxLng - minLng) * 1.2; // Add some padding
    const latitude = (minLat + maxLat) / 2;
    const longitude = (minLng + maxLng) / 2;

    return {
      latitude,
      longitude,
      latitudeDelta: latitudeDelta || 5, // Fallback if delta is 0
      longitudeDelta: longitudeDelta || 5, // Fallback if delta is 0
    };
  };

  // Get color based on detainee count
  const getColorForCount = (count: number) => {
    if (count === 0) return '#90EE90'; // Light green
    if (count < 10) return '#9ACD32'; // Yellow green
    if (count < 50) return '#FFD700'; // Gold
    if (count < 100) return '#FF8C00'; // Dark orange
    return '#FF4500'; // Orange red
  };

  return (
    <View style={styles.container}>
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0000ff" />
          <Text style={styles.loadingText}>Loading heatmap data...</Text>
        </View>
      )}

      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {!loading && !error && (
        <>
          <MapView
            provider={PROVIDER_GOOGLE}
            style={styles.map}
            initialRegion={calculateInitialRegion()}
            showsUserLocation={true}
            showsMyLocationButton={true}
          >
            {heatmapData.map((facility) => (
              <Marker
                key={facility.id}
                coordinate={{
                  latitude: facility.latitude,
                  longitude: facility.longitude,
                }}
                title={facility.name}
                description={`${facility.current_detainee_count} detainees`}
                pinColor={getColorForCount(facility.current_detainee_count)}
              />
            ))}
          </MapView>

          <View style={styles.facilityListContainer}>
            <Text style={styles.listTitle}>
              Facilities ({heatmapData.length})
            </Text>
            <ScrollView style={styles.facilityList}>
              {heatmapData.map((facility) => (
                <View key={facility.id} style={styles.facilityItem}>
                  <Text style={styles.facilityName}>{facility.name}</Text>
                  <Text style={[styles.facilityCount, { color: getColorForCount(facility.current_detainee_count) }]}>
                    {facility.current_detainee_count} detainees
                  </Text>
                </View>
              ))}
            </ScrollView>
          </View>
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    color: '#c62828',
    textAlign: 'center',
    fontSize: 16,
  },
  map: {
    width: SCREEN_WIDTH,
    height: SCREEN_HEIGHT * 0.5,
  },
  facilityListContainer: {
    flex: 1,
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    marginTop: -20,
    paddingTop: 20,
    paddingHorizontal: 20,
  },
  listTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  facilityList: {
    flex: 1,
  },
  facilityItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  facilityName: {
    fontSize: 16,
    color: '#333',
    flex: 2,
  },
  facilityCount: {
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
    textAlign: 'right',
  },
});

export default HeatmapView;