/**
 * ICE Locator Mobile App
 * https://github.com/trose/ice-locator-mcp
 *
 * @format
 */

import React, { useState, useEffect } from 'react';
import { 
  ScrollView, 
  StyleSheet, 
  Text, 
  TextInput, 
  View, 
  Button, 
  Alert,
  ActivityIndicator,
  SafeAreaView,
  TouchableOpacity,
  Platform,
  Dimensions,
  StatusBar,
  Linking,
  ToastAndroid,
  AccessibilityInfo,
  findNodeHandle
} from 'react-native';
import iceClient from './src/mcp/ICEClient';
import HeatmapAPI from './src/heatmap/HeatmapAPI';
import HeatmapView from './src/heatmap/HeatmapView'; // Add this import

// Get screen dimensions for responsive design
const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');
const isTablet = SCREEN_WIDTH >= 768;

// Type definitions
interface Detainee {
  detainee_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  country_of_birth: string;
  location: string;
  status: string;
  booking_date: string;
}

interface SearchForm {
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  countryOfBirth: string;
  alienNumber: string;
}

const App = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [searchForm, setSearchForm] = useState<SearchForm>({
    firstName: '',
    lastName: '',
    dateOfBirth: '',
    countryOfBirth: '',
    alienNumber: ''
  });
  const [searchResult, setSearchResult] = useState<Detainee | null>(null);
  const [searchType, setSearchType] = useState<'name' | 'alien'>('name');
  const [error, setError] = useState<string | null>(null);
  const [cacheCleared, setCacheCleared] = useState(false);
  const [isFocused, setIsFocused] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'search' | 'heatmap'>('search');

  // Connect to MCP server on app start
  useEffect(() => {
    const connectToServer = async () => {
      try {
        await iceClient.connect();
        setIsConnected(true);
        
        // Announce to screen readers that the app is ready
        AccessibilityInfo.announceForAccessibility('ICE Detainee Locator app is ready');
      } catch (error) {
        Alert.alert('Connection Error', 'Failed to connect to ICE Locator server');
        console.error('Connection error:', error);
      }
    };

    connectToServer();

    // Cleanup on unmount
    return () => {
      iceClient.disconnect();
    };
  }, []);

  // Validate date format (YYYY-MM-DD)
  const isValidDate = (dateString: string): boolean => {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    if (!regex.test(dateString)) return false;
    
    const date = new Date(dateString);
    const [year, month, day] = dateString.split('-').map(Number);
    
    return date.getFullYear() === year && 
           date.getMonth() === month - 1 && 
           date.getDate() === day;
  };

  // Validate alien number format (A followed by 8-9 digits)
  const isValidAlienNumber = (alienNumber: string): boolean => {
    const regex = /^A\d{8,9}$/;
    return regex.test(alienNumber.toUpperCase());
  };

  // Handle search form changes
  const handleInputChange = (name: keyof SearchForm, value: string) => {
    // Auto-format alien number to uppercase
    if (name === 'alienNumber') {
      value = value.toUpperCase();
    }
    
    setSearchForm(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (error) {
      setError(null);
    }
  };

  // Clear cache
  const handleClearCache = () => {
    iceClient.clearCache();
    setCacheCleared(true);
    
    // Provide user feedback
    if (Platform.OS === 'android') {
      ToastAndroid.show('Cache cleared successfully', ToastAndroid.SHORT);
    } else {
      Alert.alert('Success', 'Cache cleared successfully');
    }
    
    AccessibilityInfo.announceForAccessibility('Cache cleared successfully');
    
    setTimeout(() => setCacheCleared(false), 2000); // Reset after 2 seconds
  };

  // Handle search submission
  const handleSearch = async () => {
    if (!isConnected) {
      setError('Not connected to server. Please wait for connection.');
      AccessibilityInfo.announceForAccessibility('Not connected to server');
      return;
    }

    setIsLoading(true);
    setSearchResult(null);
    setError(null);
    
    // Announce search start
    AccessibilityInfo.announceForAccessibility('Searching for detainee information');

    try {
      let response: any;
      
      if (searchType === 'name') {
        // Validate name search fields
        if (!searchForm.firstName.trim()) {
          throw new Error('First name is required');
        }
        if (!searchForm.lastName.trim()) {
          throw new Error('Last name is required');
        }
        if (!searchForm.dateOfBirth.trim()) {
          throw new Error('Date of birth is required');
        }
        if (!isValidDate(searchForm.dateOfBirth)) {
          throw new Error('Invalid date format. Use YYYY-MM-DD');
        }
        if (!searchForm.countryOfBirth.trim()) {
          throw new Error('Country of birth is required');
        }
        
        response = await iceClient.searchDetaineeByName(
          searchForm.firstName.trim(),
          searchForm.lastName.trim(),
          searchForm.dateOfBirth,
          searchForm.countryOfBirth.trim()
        );
      } else {
        // Validate alien number
        if (!searchForm.alienNumber.trim()) {
          throw new Error('Alien number is required');
        }
        if (!isValidAlienNumber(searchForm.alienNumber.trim())) {
          throw new Error('Invalid alien number format. Use A followed by 8-9 digits');
        }
        
        response = await iceClient.searchDetaineeByAlienNumber(searchForm.alienNumber.trim());
      }
      
      // Parse the response
      if (response && response.content && response.content.length > 0) {
        const content = response.content[0];
        if (content.type === 'text') {
          try {
            const result = JSON.parse(content.text);
            if (result.status === 'success' && result.data) {
              setSearchResult(result.data);
              AccessibilityInfo.announceForAccessibility('Search completed successfully');
            } else {
              throw new Error(result.error_message || 'Failed to search for detainee');
            }
          } catch (parseError) {
            // If it's not JSON, treat it as plain text
            throw new Error(content.text);
          }
        } else {
          throw new Error('Unexpected response format');
        }
      } else {
        throw new Error('No response from server');
      }
    } catch (err: any) {
      const errorMessage = err.message || 'An error occurred while searching';
      setError(errorMessage);
      AccessibilityInfo.announceForAccessibility(`Search error: ${errorMessage}`);
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Load heatmap data when the heatmap tab is selected
  useEffect(() => {
    if (activeTab === 'heatmap' && isConnected) {
      loadHeatmapData();
    }
  }, [activeTab, isConnected]);

  // Handle focus for accessibility
  const handleFocus = (fieldName: string) => {
    setIsFocused(fieldName);
    AccessibilityInfo.announceForAccessibility(`${fieldName} field focused`);
  };

  // Handle blur for accessibility
  const handleBlur = () => {
    setIsFocused(null);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      <ScrollView 
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        <Text 
          style={styles.title}
          accessibilityRole="header"
          accessible={true}
        >
          ICE Detainee Locator
        </Text>
        
        {/* Connection Status */}
        <View 
          style={styles.statusContainer}
          accessibilityLabel={`Server status: ${isConnected ? 'Connected' : 'Connecting'}`}
        >
          <Text style={styles.statusLabel}>Server Status:</Text>
          <Text 
            style={[styles.statusValue, isConnected ? styles.connected : styles.disconnected]}
            accessibilityLiveRegion="polite"
          >
            {isConnected ? 'Connected' : 'Connecting...'}
          </Text>
        </View>

        {/* Cache Clear Button */}
        <View style={styles.cacheContainer}>
          <TouchableOpacity 
            style={[styles.cacheButton, cacheCleared && styles.cacheButtonSuccess]}
            onPress={handleClearCache}
            disabled={cacheCleared}
            accessibilityRole="button"
            accessibilityLabel="Clear search cache"
            accessibilityHint="Clears cached search results"
          >
            <Text style={styles.cacheButtonText}>
              {cacheCleared ? 'Cache Cleared!' : 'Clear Cache'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Main Tab Selector */}
        <View style={styles.formContainer}>
          <Text 
            style={styles.formTitle}
            accessibilityRole="header"
          >
            View Mode
          </Text>
          <View style={styles.buttonGroup}>
            <TouchableOpacity
              style={[
                styles.tabButton, 
                activeTab === 'search' && styles.tabButtonActive
              ]}
              onPress={() => setActiveTab('search')}
              accessibilityRole="button"
              accessibilityState={{ selected: activeTab === 'search' }}
              accessibilityLabel="Search view"
            >
              <Text 
                style={[
                  styles.tabButtonText,
                  activeTab === 'search' && styles.tabButtonTextActive
                ]}
              >
                Search
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.tabButton, 
                activeTab === 'heatmap' && styles.tabButtonActive
              ]}
              onPress={() => setActiveTab('heatmap')}
              accessibilityRole="button"
              accessibilityState={{ selected: activeTab === 'heatmap' }}
              accessibilityLabel="Heatmap view"
            >
              <Text 
                style={[
                  styles.tabButtonText,
                  activeTab === 'heatmap' && styles.tabButtonTextActive
                ]}
              >
                Heatmap
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Search View */}
        {activeTab === 'search' && (
          <>
            {/* Search Type Selector */}
            <View style={styles.formContainer}>
              <Text 
                style={styles.formTitle}
                accessibilityRole="header"
              >
                Search Type
              </Text>
              <View style={styles.buttonGroup}>
                <TouchableOpacity
                  style={[
                    styles.tabButton, 
                    searchType === 'name' && styles.tabButtonActive
                  ]}
                  onPress={() => setSearchType('name')}
                  accessibilityRole="button"
                  accessibilityState={{ selected: searchType === 'name' }}
                  accessibilityLabel="Search by name"
                >
                  <Text 
                    style={[
                      styles.tabButtonText,
                      searchType === 'name' && styles.tabButtonTextActive
                    ]}
                  >
                    By Name
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[
                    styles.tabButton, 
                    searchType === 'alien' && styles.tabButtonActive
                  ]}
                  onPress={() => setSearchType('alien')}
                  accessibilityRole="button"
                  accessibilityState={{ selected: searchType === 'alien' }}
                  accessibilityLabel="Search by alien number"
                >
                  <Text 
                    style={[
                      styles.tabButtonText,
                      searchType === 'alien' && styles.tabButtonTextActive
                    ]}
                  >
                    By Alien #
                  </Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Search Form */}
            <View style={styles.formContainer}>
              <Text 
                style={styles.formTitle}
                accessibilityRole="header"
              >
                {searchType === 'name' ? 'Search by Name' : 'Search by Alien Number'}
              </Text>
              
              {searchType === 'name' ? (
                <>
                  <TextInput
                    style={[
                      styles.input, 
                      isFocused === 'firstName' && styles.inputFocused
                    ]}
                    placeholder="First Name"
                    value={searchForm.firstName}
                    onChangeText={(value) => handleInputChange('firstName', value)}
                    onFocus={() => handleFocus('First Name')}
                    onBlur={handleBlur}
                    accessibilityLabel="First name"
                    accessibilityHint="Enter the detainee's first name"
                  />
                  
                  <TextInput
                    style={[
                      styles.input, 
                      isFocused === 'lastName' && styles.inputFocused
                    ]}
                    placeholder="Last Name"
                    value={searchForm.lastName}
                    onChangeText={(value) => handleInputChange('lastName', value)}
                    onFocus={() => handleFocus('Last Name')}
                    onBlur={handleBlur}
                    accessibilityLabel="Last name"
                    accessibilityHint="Enter the detainee's last name"
                  />
                  
                  <TextInput
                    style={[
                      styles.input, 
                      isFocused === 'dateOfBirth' && styles.inputFocused
                    ]}
                    placeholder="Date of Birth (YYYY-MM-DD)"
                    value={searchForm.dateOfBirth}
                    onChangeText={(value) => handleInputChange('dateOfBirth', value)}
                    keyboardType="numeric"
                    onFocus={() => handleFocus('Date of Birth')}
                    onBlur={handleBlur}
                    accessibilityLabel="Date of birth"
                    accessibilityHint="Enter the detainee's date of birth in YYYY-MM-DD format"
                  />
                  
                  <TextInput
                    style={[
                      styles.input, 
                      isFocused === 'countryOfBirth' && styles.inputFocused
                    ]}
                    placeholder="Country of Birth"
                    value={searchForm.countryOfBirth}
                    onChangeText={(value) => handleInputChange('countryOfBirth', value)}
                    onFocus={() => handleFocus('Country of Birth')}
                    onBlur={handleBlur}
                    accessibilityLabel="Country of birth"
                    accessibilityHint="Enter the detainee's country of birth"
                  />
                </>
              ) : (
                <TextInput
                  style={[
                    styles.input, 
                    isFocused === 'alienNumber' && styles.inputFocused
                  ]}
                  placeholder="Alien Number (A000000000)"
                  value={searchForm.alienNumber}
                  onChangeText={(value) => handleInputChange('alienNumber', value)}
                  autoCapitalize="characters"
                  onFocus={() => handleFocus('Alien Number')}
                  onBlur={handleBlur}
                  accessibilityLabel="Alien number"
                  accessibilityHint="Enter the detainee's alien registration number starting with A"
                />
              )}
              
              <TouchableOpacity
                style={[styles.searchButton, (!isConnected || isLoading) && styles.searchButtonDisabled]}
                onPress={handleSearch}
                disabled={!isConnected || isLoading}
                accessibilityRole="button"
                accessibilityLabel={isLoading ? "Searching" : "Search for detainee"}
                accessibilityState={{ disabled: !isConnected || isLoading }}
              >
                <Text style={styles.searchButtonText}>
                  {isLoading ? "Searching..." : "Search"}
                </Text>
              </TouchableOpacity>
            </View>

            {/* Error Message */}
            {error && (
              <View 
                style={styles.errorContainer}
                accessibilityRole="alert"
                accessible={true}
              >
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}

            {/* Loading Indicator */}
            {isLoading && (
              <View style={styles.loadingContainer}>
                <ActivityIndicator 
                  size="large" 
                  color="#0000ff" 
                  accessibilityLabel="Searching for detainee information"
                />
                <Text style={styles.loadingText}>Searching database...</Text>
              </View>
            )}

            {/* Search Results */}
            {searchResult && (
              <View 
                style={styles.resultContainer}
                accessibilityRole="summary"
                accessible={true}
              >
                <Text 
                  style={styles.resultTitle}
                  accessibilityRole="header"
                >
                  Search Results
                </Text>
                <View style={styles.resultItem}>
                  <Text style={styles.resultLabel}>Name:</Text>
                  <Text 
                    style={styles.resultValue}
                    accessibilityLabel={`Name: ${searchResult.first_name} ${searchResult.last_name}`}
                  >
                    {searchResult.first_name} {searchResult.last_name}
                  </Text>
                </View>
                <View style={styles.resultItem}>
                  <Text style={styles.resultLabel}>Date of Birth:</Text>
                  <Text 
                    style={styles.resultValue}
                    accessibilityLabel={`Date of birth: ${searchResult.date_of_birth}`}
                  >
                    {searchResult.date_of_birth}
                  </Text>
                </View>
                <View style={styles.resultItem}>
                  <Text style={styles.resultLabel}>Country of Birth:</Text>
                  <Text 
                    style={styles.resultValue}
                    accessibilityLabel={`Country of birth: ${searchResult.country_of_birth}`}
                  >
                    {searchResult.country_of_birth}
                  </Text>
                </View>
                <View style={styles.resultItem}>
                  <Text style={styles.resultLabel}>Location:</Text>
                  <Text 
                    style={styles.resultValue}
                    accessibilityLabel={`Location: ${searchResult.location}`}
                  >
                    {searchResult.location}
                  </Text>
                </View>
                <View style={styles.resultItem}>
                  <Text style={styles.resultLabel}>Status:</Text>
                  <Text 
                    style={[styles.resultValue, styles.statusText]}
                    accessibilityLabel={`Status: ${searchResult.status}`}
                  >
                    {searchResult.status}
                  </Text>
                </View>
                <View style={styles.resultItem}>
                  <Text style={styles.resultLabel}>Booking Date:</Text>
                  <Text 
                    style={styles.resultValue}
                    accessibilityLabel={`Booking date: ${searchResult.booking_date}`}
                  >
                    {searchResult.booking_date}
                  </Text>
                </View>
                <View style={styles.resultItem}>
                  <Text style={styles.resultLabel}>Detainee ID:</Text>
                  <Text 
                    style={styles.resultValue}
                    accessibilityLabel={`Detainee ID: ${searchResult.detainee_id}`}
                  >
                    {searchResult.detainee_id}
                  </Text>
                </View>
              </View>
            )}
          </>
        )}

        {/* Heatmap View */}
        {activeTab === 'heatmap' && (
          <HeatmapView isConnected={isConnected} />
        )}
        
        {/* Footer with help information */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            This tool helps locate detained individuals in ICE custody.
          </Text>
          <TouchableOpacity 
            onPress={() => Linking.openURL('https://www.ice.gov/contact')}
            accessibilityRole="link"
            accessibilityLabel="Visit ICE website for more information"
          >
            <Text style={styles.footerLink}>
              Visit ICE.gov for official information
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: isTablet ? 40 : 20,
  },
  title: {
    fontSize: isTablet ? 32 : 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: isTablet ? 30 : 20,
    color: '#333',
  },
  statusContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: isTablet ? 20 : 15,
    borderRadius: 8,
    marginBottom: isTablet ? 20 : 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  cacheContainer: {
    alignItems: 'center',
    marginBottom: isTablet ? 20 : 10,
  },
  cacheButton: {
    backgroundColor: '#ff9500',
    paddingHorizontal: isTablet ? 30 : 20,
    paddingVertical: isTablet ? 15 : 10,
    borderRadius: 8,
    minWidth: isTablet ? 150 : 120,
  },
  cacheButtonSuccess: {
    backgroundColor: '#4CAF50',
  },
  cacheButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    textAlign: 'center',
    fontSize: isTablet ? 18 : 16,
  },
  statusLabel: {
    fontSize: isTablet ? 18 : 16,
    fontWeight: '600',
    color: '#333',
  },
  statusValue: {
    fontSize: isTablet ? 18 : 16,
    fontWeight: '600',
  },
  connected: {
    color: '#4CAF50',
  },
  disconnected: {
    color: '#F44336',
  },
  formContainer: {
    backgroundColor: '#fff',
    padding: isTablet ? 30 : 20,
    borderRadius: 8,
    marginBottom: isTablet ? 30 : 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  formTitle: {
    fontSize: isTablet ? 24 : 20,
    fontWeight: 'bold',
    marginBottom: isTablet ? 20 : 15,
    color: '#333',
  },
  buttonGroup: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: isTablet ? 20 : 15,
  },
  tabButton: {
    flex: 1,
    paddingVertical: isTablet ? 12 : 8,
    paddingHorizontal: isTablet ? 20 : 10,
    marginHorizontal: 5,
    borderRadius: 6,
    backgroundColor: '#e0e0e0',
    alignItems: 'center',
  },
  tabButtonActive: {
    backgroundColor: '#007AFF',
  },
  tabButtonText: {
    fontSize: isTablet ? 16 : 14,
    fontWeight: '600',
    color: '#666',
  },
  tabButtonTextActive: {
    color: '#fff',
  },
  input: {
    height: isTablet ? 50 : 40,
    borderColor: '#ddd',
    borderWidth: 1,
    borderRadius: 4,
    marginBottom: isTablet ? 20 : 15,
    paddingHorizontal: isTablet ? 15 : 10,
    backgroundColor: '#fafafa',
    fontSize: isTablet ? 18 : 16,
  },
  inputFocused: {
    borderColor: '#007AFF',
    borderWidth: 2,
  },
  searchButton: {
    backgroundColor: '#007AFF',
    paddingVertical: isTablet ? 15 : 12,
    borderRadius: 6,
    alignItems: 'center',
    marginTop: 10,
  },
  searchButtonDisabled: {
    backgroundColor: '#ccc',
  },
  searchButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: isTablet ? 18 : 16,
  },
  errorContainer: {
    backgroundColor: '#ffebee',
    padding: isTablet ? 20 : 15,
    borderRadius: 8,
    marginBottom: isTablet ? 30 : 20,
  },
  errorText: {
    color: '#c62828',
    textAlign: 'center',
    fontSize: isTablet ? 18 : 16,
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: isTablet ? 40 : 20,
  },
  loadingText: {
    marginTop: isTablet ? 15 : 10,
    fontSize: isTablet ? 18 : 16,
    color: '#666',
  },
  resultContainer: {
    backgroundColor: '#fff',
    padding: isTablet ? 30 : 20,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    marginBottom: isTablet ? 30 : 20,
  },
  resultTitle: {
    fontSize: isTablet ? 24 : 20,
    fontWeight: 'bold',
    marginBottom: isTablet ? 20 : 15,
    color: '#333',
  },
  resultItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: isTablet ? 15 : 10,
    paddingVertical: isTablet ? 10 : 5,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  resultLabel: {
    fontSize: isTablet ? 18 : 16,
    fontWeight: '600',
    color: '#555',
    flex: 1,
  },
  resultValue: {
    fontSize: isTablet ? 18 : 16,
    color: '#333',
    textAlign: 'right',
    flex: 2,
    marginLeft: 10,
  },
  statusText: {
    fontWeight: 'bold',
    color: '#F44336',
  },
  footer: {
    marginTop: isTablet ? 40 : 20,
    padding: isTablet ? 20 : 15,
    backgroundColor: '#e3f2fd',
    borderRadius: 8,
  },
  footerText: {
    fontSize: isTablet ? 16 : 14,
    color: '#1976d2',
    textAlign: 'center',
    marginBottom: 10,
  },
  footerLink: {
    fontSize: isTablet ? 16 : 14,
    color: '#007AFF',
    textAlign: 'center',
    textDecorationLine: 'underline',
  },
});

export default App;