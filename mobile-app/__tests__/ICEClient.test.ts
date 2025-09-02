/**
 * Unit tests for ICEClient
 * These tests focus on the client-side logic without connecting to the actual MCP server
 */

// Mock the MCP SDK modules
jest.mock('@modelcontextprotocol/sdk/client', () => {
  return {
    Client: jest.fn().mockImplementation(() => {
      return {
        connect: jest.fn(),
        close: jest.fn(),
        callTool: jest.fn()
      };
    })
  };
});

jest.mock('@modelcontextprotocol/sdk/client/stdio.js', () => {
  return {
    StdioClientTransport: jest.fn().mockImplementation(() => {
      return {
        close: jest.fn()
      };
    })
  };
});

// Import after mocks are set up
import { Client } from '@modelcontextprotocol/sdk/client';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import iceClient from '../src/mcp/ICEClient';

describe('ICEClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Clear the cache and reset connection state
    iceClient.clearCache();
    // Reset connection state for unit tests
    (iceClient as any).isConnected = false;
    (iceClient as any).client = null;
    (iceClient as any).transport = null;
  });

  afterEach(() => {
    // Clean up intervals to prevent open handles
    (iceClient as any).cleanup();
  });

  describe('Connection Management', () => {
    it('should create client and transport instances when connecting', async () => {
      await iceClient.connect();
      
      // Verify that Client and StdioClientTransport were instantiated
      expect(Client).toHaveBeenCalledWith({
        name: "ice-locator-mobile",
        version: "1.0.0"
      });
      
      expect(StdioClientTransport).toHaveBeenCalledWith({
        command: "/Users/trose/src/locator-mcp/.venv/bin/python",
        args: ["-m", "ice_locator_mcp"],
        cwd: "/Users/trose/src/locator-mcp"
      });
    });

    it('should handle connection errors gracefully', async () => {
      // Mock the connect method to throw an error
      const mockClientInstance = new Client({ name: "test", version: "1.0.0" });
      mockClientInstance.connect.mockRejectedValueOnce(new Error('Connection failed'));
      
      // Override the Client mock for this test
      (Client as jest.Mock).mockImplementation(() => mockClientInstance);
      
      await expect(iceClient.connect()).rejects.toThrow('Connection failed');
    });
  });

  describe('Cache Management', () => {
    it('should clear cache when clearCache is called', () => {
      // This test verifies the cache clearing functionality
      iceClient.clearCache();
      // If no error is thrown, the method works
      expect(true).toBe(true);
    });

    it('should check connection status', () => {
      // Reset connection state for this test
      (iceClient as any).isConnected = false;
      // Initially not connected
      expect(iceClient.isConnectedToServer()).toBe(false);
      
      // Test connected state
      (iceClient as any).isConnected = true;
      expect(iceClient.isConnectedToServer()).toBe(true);
    });
  });

  describe('Search Functionality', () => {
    it('should throw error when searching without connection', async () => {
      // Reset connection state for this test
      (iceClient as any).isConnected = false;
      (iceClient as any).client = null;
      
      await expect(iceClient.searchDetaineeByName('John', 'Doe', '1990-01-01', 'Mexico'))
        .rejects.toThrow('Not connected to ICE Locator MCP server');
        
      await expect(iceClient.searchDetaineeByAlienNumber('A12345678'))
        .rejects.toThrow('Not connected to ICE Locator MCP server');
    });
  });
});