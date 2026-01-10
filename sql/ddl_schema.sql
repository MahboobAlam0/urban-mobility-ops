-- 1. Create Database (Schema in MySQL terms)
CREATE DATABASE IF NOT EXISTS citibike;
USE citibike;
-- STAR SCHEMA DESIGN
CREATE TABLE IF NOT EXISTS dim_station (
    station_id VARCHAR(50) PRIMARY KEY,
    station_name VARCHAR(255),
    latitude DOUBLE,
    longitude DOUBLE
);
-- 3. Dimension: Date/Time (The "When")
CREATE TABLE IF NOT EXISTS dim_time (
    time_key INT AUTO_INCREMENT PRIMARY KEY,
    full_date DATE,
    year INT,
    month INT,
    day INT,
    day_of_week VARCHAR(10),
    hour INT,
    is_weekend BOOLEAN
);
-- 4. Fact Table: Trips (The "Action")
CREATE TABLE IF NOT EXISTS fact_trips (
    trip_id VARCHAR(50) PRIMARY KEY,
    rideable_type VARCHAR(50),
    started_at DATETIME,
    ended_at DATETIME,
    start_station_id VARCHAR(50),
    end_station_id VARCHAR(50),
    duration_seconds DOUBLE,
    member_casual VARCHAR(20),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Indexes
CREATE INDEX idx_fact_start_time ON fact_trips(started_at);
CREATE INDEX idx_fact_start_station ON fact_trips(start_station_id);