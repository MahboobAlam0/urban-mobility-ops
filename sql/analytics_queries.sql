-- Analytics Queries
USE citibike;
WITH inbound AS (
    SELECT end_station_id,
        COUNT(*) as bike_in
    FROM fact_trips
    GROUP BY end_station_id
),
outbound AS (
    SELECT start_station_id,
        COUNT(*) as bike_out
    FROM fact_trips
    GROUP BY start_station_id
)
SELECT s.station_name,
    COALESCE(i.bike_in, 0) as total_in,
    COALESCE(o.bike_out, 0) as total_out,
    (COALESCE(i.bike_in, 0) - COALESCE(o.bike_out, 0)) as net_flow
FROM dim_station s
    LEFT JOIN inbound i ON s.station_id = i.end_station_id
    LEFT JOIN outbound o ON s.station_id = o.start_station_id
ORDER BY net_flow DESC
LIMIT 10;
WITH hourly_stats AS (
    SELECT DATE_FORMAT(started_at, '%Y-%m-%d %H:00:00') as trip_hour,
        COUNT(*) as num_trips
    FROM fact_trips
    GROUP BY 1
)
SELECT trip_hour,
    num_trips,
    -- Calculate average of the last 3 hours + current hour
    AVG(num_trips) OVER (
        ORDER BY trip_hour ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) as moving_avg_4hr
FROM hourly_stats
ORDER BY trip_hour;