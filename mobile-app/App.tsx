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
  SafeAreaView
} from 'react-native';
import iceClient from './src/mcp/ICEClient';

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
}

const App = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [searchForm, setSearchForm] = useState<SearchForm>({
    firstName: '',
    lastName: '',
    dateOfBirth: '',
    countryOfBirth: ''
  });
  const [searchResult, setSearchResult] = useState<Detainee | null>(null);

  // Connect to MCP server on app start
  useEffect(() => {
    const connectToServer = async () => {
      try {
        await iceClient.connect();
        setIsConnected(true);
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

  // Handle search form changes
  const handleInputChange = (name: keyof SearchForm, value: string) => {
    setSearchForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle search submission
  const handleSearch = async () => {
    if (!isConnected) {
      Alert.alert('Not Connected', 'Please wait for the server to connect');
      return;
    }

    if (!searchForm.firstName || !searchForm.lastName || !searchForm.dateOfBirth || !searchForm.countryOfBirth) {
      Alert.alert('Missing Information', 'Please fill in all fields');
      return;
    }

    setIsLoading(true);
    setSearchResult(null);

    try {
      const response = await iceClient.searchDetaineeByName(
        searchForm.firstName,
        searchForm.lastName,
        searchForm.dateOfBirth,
        searchForm.countryOfBirth
      );
      
      if (response.status === 'success') {
        setSearchResult(response.data);
      } else {
        Alert.alert('Search Error', response.error_message || 'Failed to search for detainee');
      }
    } catch (error) {
      Alert.alert('Search Error', 'An error occurred while searching');
      console.error('Search error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>ICE Detainee Locator</Text>
        
        {/* Connection Status */}
        <View style={styles.statusContainer}>
          <Text style={styles.statusLabel}>Server Status:</Text>
          <Text style={[styles.statusValue, isConnected ? styles.connected : styles.disconnected]}>
            {isConnected ? 'Connected' : 'Connecting...'}
          </Text>
        </View>

        {/* Search Form */}
        <View style={styles.formContainer}>
          <Text style={styles.formTitle}>Search for Detainee</Text>
          
          <TextInput
            style={styles.input}
            placeholder="First Name"
            value={searchForm.firstName}
            onChangeText={(value) => handleInputChange('firstName', value)}
          />
          
          <TextInput
            style={styles.input}
            placeholder="Last Name"
            value={searchForm.lastName}
            onChangeText={(value) => handleInputChange('lastName', value)}
          />
          
          <TextInput
            style={styles.input}
            placeholder="Date of Birth (YYYY-MM-DD)"
            value={searchForm.dateOfBirth}
            onChangeText={(value) => handleInputChange('dateOfBirth', value)}
          />
          
          <TextInput
            style={styles.input}
            placeholder="Country of Birth"
            value={searchForm.countryOfBirth}
            onChangeText={(value) => handleInputChange('countryOfBirth', value)}
          />
          
          <Button 
            title={isLoading ? "Searching..." : "Search"} 
            onPress={handleSearch}
            disabled={!isConnected || isLoading}
          />
        </View>

        {/* Loading Indicator */}
        {isLoading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#0000ff" />
            <Text style={styles.loadingText}>Searching database...</Text>
          </View>
        )}

        {/* Search Results */}
        {searchResult && (
          <View style={styles.resultContainer}>
            <Text style={styles.resultTitle}>Search Results</Text>
            <View style={styles.resultItem}>
              <Text style={styles.resultLabel}>Name:</Text>
              <Text style={styles.resultValue}>
                {searchResult.first_name} {searchResult.last_name}
              </Text>
            </View>
            <View style={styles.resultItem}>
              <Text style={styles.resultLabel}>Date of Birth:</Text>
              <Text style={styles.resultValue}>{searchResult.date_of_birth}</Text>
            </View>
            <View style={styles.resultItem}>
              <Text style={styles.resultLabel}>Country of Birth:</Text>
              <Text style={styles.resultValue}>{searchResult.country_of_birth}</Text>
            </View>
            <View style={styles.resultItem}>
              <Text style={styles.resultLabel}>Location:</Text>
              <Text style={styles.resultValue}>{searchResult.location}</Text>
            </View>
            <View style={styles.resultItem}>
              <Text style={styles.resultLabel}>Status:</Text>
              <Text style={[styles.resultValue, styles.statusText]}>
                {searchResult.status}
              </Text>
            </View>
            <View style={styles.resultItem}>
              <Text style={styles.resultLabel}>Booking Date:</Text>
              <Text style={styles.resultValue}>{searchResult.booking_date}</Text>
            </View>
          </View>
        )}
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
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  statusContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  statusLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  statusValue: {
    fontSize: 16,
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
    padding: 20,
    borderRadius: 8,
    marginBottom: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  formTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  input: {
    height: 40,
    borderColor: '#ddd',
    borderWidth: 1,
    borderRadius: 4,
    marginBottom: 15,
    paddingHorizontal: 10,
    backgroundColor: '#fafafa',
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  resultContainer: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  resultTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  resultItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
    paddingVertical: 5,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  resultLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#555',
  },
  resultValue: {
    fontSize: 16,
    color: '#333',
  },
  statusText: {
    fontWeight: 'bold',
    color: '#F44336',
  },
});

export default App;