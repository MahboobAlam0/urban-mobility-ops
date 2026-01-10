# System Architecture

## 1. High-Level Design
The Urban Mobility Operations Center is designed as a modular **ELT (Extract, Load, Transform)** system. Unlike monolithic scripts, it separates concerns into distinct layers:

```mermaid
graph LR
    A[S3 Source] -->|Extract| B(Staging Layer - MySQL)
    B -->|Transform| C(Warehouse Layer - Stars)
    C -->|Serve| D(Streamlit Dashboard)
```

## 2. Data Model (Star Schema)
We utilize a Star Schema optimized for OLAP (Online Analytical Processing) queries.

### Fact Table: `fact_trips`
*   **Granularity**: One row per bike ride.
*   **Design Decision**: We chose this granularity because aggregations (daily, hourly, weekly) are fast enough on 1M rows, and it preserves the ability to filter by specific User Types (Member vs Casual).

### Dimensions
*   `dim_station`: Stores the Lat/Lon data. We separated this to avoid storing coordinate floats in every single trip row (Reduces storage cost).
*   `dim_time`: A standard calendar table to handle "Weekend vs Weekday" logic without complex runtime date math.

## 3. Scalability & Future Proofing
*   **Chunking Strategy**: The ETL pipeline processes data in 100k row chunks. This ensures the script runs on a laptop with 8GB RAM without crashing.
*   **Modular Config**: The `CityConfig` class allows us to deploy this for London or Chicago by simply swapping the configuration object, rather than rewriting the pipeline.
