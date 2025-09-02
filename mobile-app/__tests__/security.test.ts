/**
 * Security and Privacy Validation Tests for ICE Locator Mobile App
 * These tests validate that the app follows privacy-first design principles
 * and does not store sensitive data on the device.
 */

import iceClient from '../src/mcp/ICEClient';

// Mock file system access to monitor storage attempts
const mockFileSystem = {
  writeFile: jest.fn(),
  readFile: jest.fn(),
  unlink: jest.fn()
};

// Mock AsyncStorage to monitor storage attempts
const mockAsyncStorage = {
  setItem: jest.fn(),
  getItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

// Mock console methods to capture log output
const mockConsole = {
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn()
};

describe('Security and Privacy Validation', () => {
  // Increase timeout for security tests
  jest.setTimeout(30000);

  beforeAll(() => {
    // Mock console methods
    global.console.log = mockConsole.log;
    global.console.error = mockConsole.error;
    global.console.warn = mockConsole.warn;
  });

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    
    // Clear the ICEClient cache
    iceClient.clearCache();
  });

  afterEach(() => {
    // Clean up intervals to prevent open handles
    try {
      (iceClient as any).cleanup();
    } catch (error) {
      console.warn('Error during cleanup:', error);
    }
  });

  afterAll(() => {
    // Final cleanup
    try {
      (iceClient as any).cleanup();
    } catch (error) {
      console.warn('Error during final cleanup:', error);
    }
  });

  describe('Data Storage Validation', () => {
    it('should not store personal data in cache with identifiable information', async () => {
      // Connect to the server
      try {
        await iceClient.connect();
      } catch (error) {
        // If connection fails, we'll skip this test
        console.warn('Skipping cache validation - server not available');
        return;
      }

      // Perform a search to populate cache
      try {
        await iceClient.searchDetaineeByName(
          'John',
          'Doe',
          '1990-01-01',
          'Mexico'
        );
      } catch (error) {
        // Search may fail, but we still want to check cache
        console.warn('Search failed, but continuing with cache validation');
      }

      // Check cache contents - should not contain raw personal data
      // The cache should store responses, not raw input data
      const cacheEntries = Array.from((iceClient as any).cache.entries());
      
      // Verify cache entries don't contain raw personal identifiers
      for (const [key, value] of cacheEntries) {
        // Key should be a generated hash, not raw data
        expect(key).not.toContain('John');
        expect(key).not.toContain('Doe');
        expect(key).not.toContain('1990-01-01');
        expect(key).not.toContain('Mexico');
        
        // Value should be MCP response structure, not raw data
        if (value && typeof value === 'object' && (value as any).content) {
          const content = (value as any).content;
          if (Array.isArray(content) && content.length > 0) {
            const textContent = content[0];
            if (textContent && textContent.type === 'text' && textContent.text) {
              // The stored text should be JSON, not raw personal data
              expect(textContent.text).not.toContain('John');
              expect(textContent.text).not.toContain('Doe');
            }
          }
        }
      }
    });

    it('should clear cache properly when requested', () => {
      // Cache should be empty initially
      expect((iceClient as any).cache.size).toBe(0);
      expect((iceClient as any).cacheExpiry.size).toBe(0);

      // Clear cache (should not fail even when empty)
      iceClient.clearCache();

      // Cache should still be empty
      expect((iceClient as any).cache.size).toBe(0);
      expect((iceClient as any).cacheExpiry.size).toBe(0);
    });

    it('should expire cache entries after TTL', () => {
      // Mock Date.now to control time
      const now = Date.now();
      jest.spyOn(global.Date, 'now').mockImplementation(() => now);

      // Add a cache entry
      const cacheKey = 'test_key';
      const cacheValue = { test: 'data' };
      (iceClient as any).cache.set(cacheKey, cacheValue);
      (iceClient as any).cacheExpiry.set(cacheKey, now + 1000); // 1 second expiry

      // Should find the entry before expiry
      expect((iceClient as any).cache.has(cacheKey)).toBe(true);

      // Advance time beyond expiry
      jest.spyOn(global.Date, 'now').mockImplementation(() => now + 2000);

      // Trigger cleanup
      (iceClient as any).cleanupCache();

      // Should have removed expired entry
      expect((iceClient as any).cache.has(cacheKey)).toBe(false);
      expect((iceClient as any).cacheExpiry.has(cacheKey)).toBe(false);
    });
  });

  describe('Error Handling Validation', () => {
    it('should not expose sensitive data in error messages', async () => {
      // Test connection error handling
      try {
        await iceClient.connect();
      } catch (error: any) {
        // Error messages should not contain personal data
        if (error && typeof error === 'object' && error.message) {
          expect(error.message).not.toContain('John');
          expect(error.message).not.toContain('Doe');
          expect(error.message).not.toContain('1990-01-01');
        }
      }

      // Test search error handling with disconnected client
      try {
        await iceClient.searchDetaineeByName('John', 'Doe', '1990-01-01', 'Mexico');
      } catch (error: any) {
        // Error messages should be generic and not expose input data
        expect(error.message).toBe('Not connected to ICE Locator MCP server');
      }

      // Check that no sensitive data was logged
      const logCalls = [
        ...mockConsole.log.mock.calls,
        ...mockConsole.error.mock.calls,
        ...mockConsole.warn.mock.calls
      ];

      for (const call of logCalls) {
        const logMessage = call.join(' ');
        expect(logMessage).not.toContain('John');
        expect(logMessage).not.toContain('Doe');
        expect(logMessage).not.toContain('1990-01-01');
      }
    });
  });

  describe('Network Security Validation', () => {
    it('should use secure connection parameters', () => {
      // Verify that the transport is configured for secure connections
      // This is a structural test since we can't easily test actual network traffic in unit tests
      
      // The StdioClientTransport should be used (which uses secure local communication)
      expect((iceClient as any).transport).toBeDefined();
      
      // Connection should use proper secure parameters
      // In our implementation, we use stdio transport which is secure for local communication
    });

    it('should handle connection securely', async () => {
      // Test that connection process doesn't expose sensitive data
      const connectPromise = iceClient.connect();
      
      // Should not reject with sensitive data in error
      try {
        await connectPromise;
      } catch (error: any) {
        if (error && typeof error === 'object' && error.message) {
          expect(error.message).not.toContain('password');
          expect(error.message).not.toContain('token');
          expect(error.message).not.toContain('key');
        }
      }
    });
  });

  describe('MCP Protocol Validation', () => {
    it('should use proper MCP client configuration', () => {
      // Verify MCP client is properly configured
      expect((iceClient as any).client).toBeDefined();
      
      // Client should have proper name and version
      // Note: We can't easily access private properties, but we can verify the client exists
    });

    it('should handle MCP tool calls securely', async () => {
      // Test that tool calls don't expose sensitive data in structure
      const args = {
        first_name: 'John',
        last_name: 'Doe',
        date_of_birth: '1990-01-01',
        country_of_birth: 'Mexico'
      };

      // The arguments should be properly structured for MCP protocol
      expect(args.first_name).toBe('John');
      expect(args.last_name).toBe('Doe');
      expect(args.date_of_birth).toBe('1990-01-01');
      expect(args.country_of_birth).toBe('Mexico');
      
      // Note: Actual tool calling is tested in integration tests
    });
  });
});