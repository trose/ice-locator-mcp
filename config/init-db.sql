-- Initialize the ICE Locator database
-- This script creates the necessary tables for the heatmap feature

-- Create Detainee table
CREATE TABLE IF NOT EXISTS detainees (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Facility table
CREATE TABLE IF NOT EXISTS facilities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    address TEXT,
    population_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create DetaineeLocationHistory table
CREATE TABLE IF NOT EXISTS detainee_location_history (
    id SERIAL PRIMARY KEY,
    detainee_id INTEGER NOT NULL,
    facility_id INTEGER NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (detainee_id) REFERENCES detainees (id),
    FOREIGN KEY (facility_id) REFERENCES facilities (id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_detainee_location_detainee_id 
ON detainee_location_history (detainee_id);

CREATE INDEX IF NOT EXISTS idx_detainee_location_facility_id 
ON detainee_location_history (facility_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ice_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ice_user;

