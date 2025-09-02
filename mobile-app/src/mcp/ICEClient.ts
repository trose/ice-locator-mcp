import { Client } from '@modelcontextprotocol/sdk/client';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

/**
 * ICE Locator MCP Client
 * 
 * This client connects to the ICE Locator MCP server and provides
 * methods to search for detainees.
 */
class ICEClient {
  private client: Client | null = null;
  private isConnected: boolean = false;
  private transport: StdioClientTransport | null = null;
  private cache: Map<string, any> = new Map();
  private cacheExpiry: Map<string, number> = new Map();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes
  private cleanupInterval: NodeJS.Timeout | null = null;

  constructor() {
    // Initialize MCP client
    // Note: We don't start the cleanup interval here anymore to avoid open handles
    // The interval will be started when needed
  }

  /**
   * Connect to the ICE Locator MCP server
   */
  async connect(): Promise<void> {
    try {
      console.log('Connecting to ICE Locator MCP server...');
      
      // Create MCP client
      this.client = new Client({
        name: "ice-locator-mobile",
        version: "1.0.0"
      });
      
      // Create transport to connect to the MCP server
      // The server is started with: python -m ice_locator_mcp
      this.transport = new StdioClientTransport({
        command: "/Users/trose/src/locator-mcp/.venv/bin/python",
        args: ["-m", "ice_locator_mcp"],
        cwd: "/Users/trose/src/locator-mcp"
      });
      
      // Connect the client to the transport
      await this.client.connect(this.transport);
      
      // Start cleanup interval only after successful connection
      if (!this.cleanupInterval) {
        this.cleanupInterval = setInterval(() => this.cleanupCache(), 60 * 1000); // Every minute
        // Make sure the interval doesn't prevent Node.js from exiting
        if (this.cleanupInterval.unref) {
          this.cleanupInterval.unref();
        }
      }
      
      this.isConnected = true;
      console.log('Connected to ICE Locator MCP server');
    } catch (error) {
      console.error('Failed to connect to ICE Locator MCP server:', error);
      throw error;
    }
  }

  /**
   * Disconnect from the ICE Locator MCP server
   */
  async disconnect(): Promise<void> {
    // Clean up the interval before disconnecting
    this.cleanup();
    
    if (this.isConnected && this.client && this.transport) {
      console.log('Disconnecting from ICE Locator MCP server...');
      
      try {
        await this.client.close();
        await this.transport.close();
      } catch (error) {
        console.error('Error during disconnect:', error);
      }
      
      this.isConnected = false;
      console.log('Disconnected from ICE Locator MCP server');
    }
  }

  /**
   * Clean up resources and intervals
   */
  cleanup(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
    this.clearCache();
  }

  /**
   * Clean up expired cache entries
   */
  private cleanupCache(): void {
    const now = Date.now();
    for (const [key, expiry] of this.cacheExpiry.entries()) {
      if (now > expiry) {
        this.cache.delete(key);
        this.cacheExpiry.delete(key);
      }
    }
  }

  /**
   * Generate a cache key for a search request
   */
  private generateCacheKey(method: string, params: any): string {
    return `${method}_${JSON.stringify(params)}`;
  }

  /**
   * Search for a detainee by name
   * 
   * @param firstName First name of the detainee
   * @param lastName Last name of the detainee
   * @param dateOfBirth Date of birth in YYYY-MM-DD format
   * @param countryOfBirth Country of birth
   */
  async searchDetaineeByName(
    firstName: string,
    lastName: string,
    dateOfBirth: string,
    countryOfBirth: string
  ): Promise<any> {
    if (!this.isConnected || !this.client) {
      throw new Error('Not connected to ICE Locator MCP server');
    }

    // Generate cache key
    const params = { firstName, lastName, dateOfBirth, countryOfBirth };
    const cacheKey = this.generateCacheKey('searchDetaineeByName', params);

    // Check cache first
    const now = Date.now();
    if (this.cache.has(cacheKey) && this.cacheExpiry.has(cacheKey)) {
      const expiry = this.cacheExpiry.get(cacheKey);
      if (expiry && now < expiry) {
        console.log('Returning cached result for name search');
        return this.cache.get(cacheKey);
      } else {
        // Remove expired entry
        this.cache.delete(cacheKey);
        this.cacheExpiry.delete(cacheKey);
      }
    }

    try {
      console.log('Searching for detainee:', { firstName, lastName, dateOfBirth, countryOfBirth });
      
      // Call the MCP tool for searching by name
      const response = await this.client.callTool({
        name: "search_detainee_by_name",
        arguments: {
          first_name: firstName,
          last_name: lastName,
          date_of_birth: dateOfBirth,
          country_of_birth: countryOfBirth
        }
      });
      
      // Cache the result
      this.cache.set(cacheKey, response);
      this.cacheExpiry.set(cacheKey, now + this.CACHE_TTL);
      
      console.log('Search completed:', response);
      return response;
    } catch (error) {
      console.error('Search failed:', error);
      throw error;
    }
  }

  /**
   * Search for a detainee by alien number
   * 
   * @param alienNumber Alien registration number (A-number)
   */
  async searchDetaineeByAlienNumber(alienNumber: string): Promise<any> {
    if (!this.isConnected || !this.client) {
      throw new Error('Not connected to ICE Locator MCP server');
    }

    // Generate cache key
    const cacheKey = this.generateCacheKey('searchDetaineeByAlienNumber', { alienNumber });

    // Check cache first
    const now = Date.now();
    if (this.cache.has(cacheKey) && this.cacheExpiry.has(cacheKey)) {
      const expiry = this.cacheExpiry.get(cacheKey);
      if (expiry && now < expiry) {
        console.log('Returning cached result for alien number search');
        return this.cache.get(cacheKey);
      } else {
        // Remove expired entry
        this.cache.delete(cacheKey);
        this.cacheExpiry.delete(cacheKey);
      }
    }

    try {
      console.log('Searching for detainee by alien number:', alienNumber);
      
      // Call the MCP tool for searching by alien number
      const response = await this.client.callTool({
        name: "search_detainee_by_alien_number",
        arguments: {
          alien_number: alienNumber
        }
      });
      
      // Cache the result
      this.cache.set(cacheKey, response);
      this.cacheExpiry.set(cacheKey, now + this.CACHE_TTL);
      
      console.log('Search completed:', response);
      return response;
    } catch (error) {
      console.error('Search failed:', error);
      throw error;
    }
  }

  /**
   * Clear all cached entries
   */
  clearCache(): void {
    this.cache.clear();
    this.cacheExpiry.clear();
  }

  /**
   * Check if the client is connected to the MCP server
   */
  isConnectedToServer(): boolean {
    return this.isConnected;
  }
}

// Export singleton instance
const iceClient = new ICEClient();

// Ensure cleanup on process exit (only in Node.js environment)
if (typeof process !== 'undefined' && process.on) {
  const cleanupHandler = () => {
    iceClient.cleanup();
  };
  
  process.on('exit', cleanupHandler);
  process.on('SIGINT', cleanupHandler);
  process.on('SIGTERM', cleanupHandler);
  process.on('SIGUSR1', cleanupHandler);
  process.on('SIGUSR2', cleanupHandler);
  process.on('uncaughtException', cleanupHandler);
}

export default iceClient;