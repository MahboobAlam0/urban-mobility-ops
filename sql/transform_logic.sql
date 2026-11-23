-- Transformation Script: Staging -> Warehouse
USE citibike;
-- 1. Populate Stations Dimension
INSERT IGNORE INTO dim_station (station_id, station_name, latitude, longitude)
SELECT DISTINCT start_station_id,
    start_station_name,
    start_lat,
    start_lng
FROM staging_trips
WHERE start_station_id IS NOT NULL;
INSERT IGNORE INTO dim_station (station_id, station_name, latitude, longitude)
SELECT DISTINCT end_station_id,
    end_station_name,
    end_lat,
    end_lng
FROM staging_trips
WHERE end_station_id IS NOT NULL;
-- 2. Populate Fact Trips
INSERT IGNORE INTO fact_trips (
        trip_id,
        rideable_type,
        started_at,
        ended_at,
        start_station_id,
        end_station_id,
        duration_seconds,
        member_casual
    )
SELECT ride_id,
    rideable_type,
    CAST(started_at AS DATETIME),
    CAST(ended_at AS DATETIME),
    start_station_id,
    end_station_id,
    TIMESTAMPDIFF(
        SECOND,
        CAST(started_at AS DATETIME),
        CAST(ended_at AS DATETIME)
    ),
    member_casual
FROM staging_trips
WHERE start_station_id IS NOT NULL
    AND end_station_id IS NOT NULL
    AND TIMESTAMPDIFF(
        SECOND,
        CAST(started_at AS DATETIME),
        CAST(ended_at AS DATETIME)
    ) > 60;
-- 3. Populate Time Dimension (one row per date and hour that has trips).
-- NOT EXISTS keeps re-runs from adding duplicate rows.
INSERT INTO dim_time (full_date, year, month, day, day_of_week, hour, is_weekend)
SELECT d.full_date,
    YEAR(d.full_date),
    MONTH(d.full_date),
    DAY(d.full_date),
    DAYNAME(d.full_date),
    d.hr,
    DAYOFWEEK(d.full_date) IN (1, 7)
FROM (
        SELECT DISTINCT DATE(started_at) AS full_date,
            HOUR(started_at) AS hr
        FROM fact_trips
    ) d
WHERE NOT EXISTS (
        SELECT 1
        FROM dim_time t
        WHERE t.full_date = d.full_date
            AND t.hour = d.hr
    );