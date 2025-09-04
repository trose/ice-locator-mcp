import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Heatmap API Client for ICE Locator Mobile App
 * 
 * This client connects to the heatmap API server and provides
 * methods to retrieve heatmap data for visualization.
 */
class HeatmapAPI {
  private static instance: HeatmapAPI;
  private baseUrl: string;
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes

  private constructor() {
    // Default to localhost for simulator, but can be configured for different environments
    // For mobile devices, this would need to be the IP address of the development machine
    this.baseUrl = 'http://localhost:8082'; // Mock API server
  }

  /**
   * Get singleton instance
   */
  static getInstance(): HeatmapAPI {
    if (!HeatmapAPI.instance) {
      HeatmapAPI.instance = new HeatmapAPI();
    }
    return HeatmapAPI.instance;
  }

  /**
   * Set the base URL for the API (useful for mobile devices)
   */
  setBaseUrl(url: string): void {
    this.baseUrl = url;
  }

  /**
   * Get all facilities with their GPS coordinates
   */
  async getFacilities(): Promise<any[]> {
    const cacheKey = 'facilities';
    const cached = this.getCachedData(cacheKey);
    if (cached) {
      console.log('Returning cached facilities data');
      return cached;
    }

    try {
      console.log('Fetching facilities data from API:', `${this.baseUrl}/api/facilities`);
      const response = await fetch(`${this.baseUrl}/api/facilities`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      this.setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch facilities:', error);
      throw error;
    }
  }

  /**
   * Get current detainee count for a specific facility
   */
  async getFacilityCurrentDetainees(facilityId: number): Promise<any> {
    const cacheKey = `facility_${facilityId}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) {
      console.log(`Returning cached data for facility ${facilityId}`);
      return cached;
    }

    try {
      console.log(`Fetching current detainees for facility ${facilityId}`);
      const response = await fetch(`${this.baseUrl}/api/facility/${facilityId}/current-detainees`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      this.setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error(`Failed to fetch facility ${facilityId} data:`, error);
      throw error;
    }
  }

  /**
   * Get aggregated data for heatmap visualization
   */
  async getHeatmapData(): Promise<any[]> {
    const cacheKey = 'heatmap_data';
    const cached = this.getCachedData(cacheKey);
    if (cached) {
      console.log('Returning cached heatmap data');
      return cached;
    }

    try {
      console.log('Fetching heatmap data from API:', `${this.baseUrl}/api/heatmap-data`);
      const response = await fetch(`${this.baseUrl}/api/heatmap-data`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      this.setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch heatmap data:', error);
      throw error;
    }
  }

  /**
   * Get cached data if still valid
   */
  private getCachedData(key: string): any | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const now = Date.now();
    if (now - cached.timestamp < this.CACHE_TTL) {
      return cached.data;
    } else {
      // Remove expired cache entry
      this.cache.delete(key);
      return null;
    }
  }

  /**
   * Set cached data with timestamp
   */
  private setCachedData(key: string, data: any): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  /**
   * Clear all cached data
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Clear specific cache entry
   */
  clearCacheEntry(key: string): void {
    this.cache.delete(key);
  }
}

export default HeatmapAPI.getInstance();