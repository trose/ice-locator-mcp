/**
 * Integration tests for the ICE Locator Mobile App
 * These tests use the real MCP server connection
 */

import iceClient from '../src/mcp/ICEClient';

describe('ICEClient Integration Tests', () => {
  // Increase timeout for integration tests
  jest.setTimeout(30000);

  beforeAll(async () => {
    // Connect to the real MCP server
    try {
      await iceClient.connect();
    } catch (error) {
      console.warn('Failed to connect to MCP server, skipping integration tests:', error);
      // Skip tests if server is not available
      return Promise.reject(new Error('Cannot connect to MCP server'));
    }
  });

  afterAll(async () => {
    // Clean up connection
    try {
      await iceClient.disconnect();
    } catch (error) {
      console.warn('Error during disconnect:', error);
    }
    // Clean up intervals to prevent open handles
    try {
      (iceClient as any).cleanup();
    } catch (error) {
      console.warn('Error during cleanup:', error);
    }
  });

  describe('Connection Status', () => {
    it('should be connected to the MCP server', () => {
      expect(iceClient.isConnectedToServer()).toBe(true);
    });
  });

  describe('Search Functionality', () => {
    it('should search for a detainee by name', async () => {
      // Skip if not connected
      if (!iceClient.isConnectedToServer()) {
        return Promise.reject(new Error('Not connected to server'));
      }

      const result = await iceClient.searchDetaineeByName(
        'John',
        'Doe',
        '1990-01-01',
        'Mexico'
      );

      expect(result).toBeDefined();
      expect(result.content).toBeDefined();
      expect(Array.isArray(result.content)).toBe(true);
      expect(result.content.length).toBeGreaterThan(0);
      
      const content = result.content[0];
      expect(content.type).toBe('text');
      
      // Parse the response
      const data = JSON.parse(content.text);
      expect(data).toHaveProperty('status');
      
      // Either success or error response is valid
      if (data.status === 'success') {
        expect(data.data).toBeDefined();
        // Validate the structure of the data
        expect(data.data).toHaveProperty('detainee_id');
        expect(data.data).toHaveProperty('first_name');
        expect(data.data).toHaveProperty('last_name');
        expect(data.data).toHaveProperty('date_of_birth');
        expect(data.data).toHaveProperty('country_of_birth');
        expect(data.data).toHaveProperty('location');
        expect(data.data).toHaveProperty('status');
        expect(data.data).toHaveProperty('booking_date');
      } else {
        // Error case - still valid response
        expect(data).toHaveProperty('error_message');
      }
    });

    it('should search for a detainee by alien number', async () => {
      // Skip if not connected
      if (!iceClient.isConnectedToServer()) {
        return Promise.reject(new Error('Not connected to server'));
      }

      const result = await iceClient.searchDetaineeByAlienNumber('A00000000');

      expect(result).toBeDefined();
      expect(result.content).toBeDefined();
      expect(Array.isArray(result.content)).toBe(true);
      expect(result.content.length).toBeGreaterThan(0);
      
      const content = result.content[0];
      expect(content.type).toBe('text');
      
      // Parse the response
      const data = JSON.parse(content.text);
      expect(data).toHaveProperty('status');
      
      // Either success or error response is valid
      if (data.status === 'success') {
        expect(data.data).toBeDefined();
        // Validate the structure of the data
        expect(data.data).toHaveProperty('detainee_id');
        expect(data.data).toHaveProperty('first_name');
        expect(data.data).toHaveProperty('last_name');
        expect(data.data).toHaveProperty('date_of_birth');
        expect(data.data).toHaveProperty('country_of_birth');
        expect(data.data).toHaveProperty('location');
        expect(data.data).toHaveProperty('status');
        expect(data.data).toHaveProperty('booking_date');
      } else {
        // Error case - still valid response
        expect(data).toHaveProperty('error_message');
      }
    });
  });

  describe('Cache Functionality', () => {
    it('should cache search results', async () => {
      // Skip if not connected
      if (!iceClient.isConnectedToServer()) {
        return Promise.reject(new Error('Not connected to server'));
      }

      // First search
      const result1 = await iceClient.searchDetaineeByName(
        'John',
        'Doe',
        '1990-01-01',
        'Mexico'
      );

      // Second search should use cache
      const result2 = await iceClient.searchDetaineeByName(
        'John',
        'Doe',
        '1990-01-01',
        'Mexico'
      );

      // Results should be identical
      expect(result1).toEqual(result2);
    });

    it('should clear cache when requested', async () => {
      // Skip if not connected
      if (!iceClient.isConnectedToServer()) {
        return Promise.reject(new Error('Not connected to server'));
      }

      // Perform a search to populate cache
      await iceClient.searchDetaineeByName(
        'Jane',
        'Smith',
        '1985-05-15',
        'Guatemala'
      );

      // Clear cache
      iceClient.clearCache();

      // Perform another search - should work fine after cache clear
      const result = await iceClient.searchDetaineeByName(
        'Jane',
        'Smith',
        '1985-05-15',
        'Guatemala'
      );

      expect(result).toBeDefined();
    });
  });
});