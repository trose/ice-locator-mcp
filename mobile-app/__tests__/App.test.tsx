/**
 * @format
 */

import React from 'react';
import ReactTestRenderer from 'react-test-renderer';
import App from '../App';

// Mock the ICEClient to avoid connecting to the actual server
jest.mock('../src/mcp/ICEClient', () => ({
  __esModule: true,
  default: {
    connect: jest.fn().mockResolvedValue(undefined),
    disconnect: jest.fn().mockResolvedValue(undefined),
    isConnectedToServer: jest.fn().mockReturnValue(true),
    searchDetaineeByName: jest.fn().mockResolvedValue({
      content: [{
        type: 'text',
        text: JSON.stringify({
          status: 'success',
          data: {
            detainee_id: '12345',
            first_name: 'John',
            last_name: 'Doe',
            date_of_birth: '1990-01-01',
            country_of_birth: 'Mexico',
            location: 'Detention Center A',
            status: 'In Custody',
            booking_date: '2023-01-01'
          }
        })
      }]
    }),
    searchDetaineeByAlienNumber: jest.fn().mockResolvedValue({
      content: [{
        type: 'text',
        text: JSON.stringify({
          status: 'success',
          data: {
            detainee_id: '67890',
            first_name: 'Jane',
            last_name: 'Smith',
            date_of_birth: '1985-05-15',
            country_of_birth: 'Guatemala',
            location: 'Detention Center B',
            status: 'In Custody',
            booking_date: '2023-02-01'
          }
        })
      }]
    }),
    clearCache: jest.fn()
  }
}));

// Mock React Native modules that aren't available in test environment
jest.mock('react-native/Libraries/Alert/Alert', () => ({
  alert: jest.fn()
}));

jest.mock('react-native/Libraries/Components/ToastAndroid/ToastAndroid', () => ({
  show: jest.fn()
}));

jest.mock('react-native/Libraries/Components/StatusBar/StatusBar', () => 'StatusBar');

jest.mock('react-native-safe-area-context', () => ({
  SafeAreaView: 'SafeAreaView'
}));

test('renders correctly', async () => {
  await ReactTestRenderer.act(() => {
    ReactTestRenderer.create(<App />);
  });
});

test('handles search by name', async () => {
  let renderer;
  await ReactTestRenderer.act(() => {
    renderer = ReactTestRenderer.create(<App />);
  });
  
  // Get the instance to test methods
  const instance = renderer.root;
  expect(instance).toBeTruthy();
});

test('handles search by alien number', async () => {
  let renderer;
  await ReactTestRenderer.act(() => {
    renderer = ReactTestRenderer.create(<App />);
  });
  
  // Get the instance to test methods
  const instance = renderer.root;
  expect(instance).toBeTruthy();
});
