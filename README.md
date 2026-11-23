# Urban Mobility Operations Center
A modular Data Engineering pipeline optimizing fleet logistics for bike-share systems.

![CI Status](https://github.com/MahboobAlam0/urban-mobility-ops/actions/workflows/ci.yml/badge.svg)
![Tests](https://img.shields.io/badge/tests-passing-green)

---

## Project Overview
This project implements an end-to-end ELT (Extract, Load, Transform) pipeline for Citi Bike trip data, aimed at station imbalance (which stations gain or lose bikes). It ingests a monthly trip file, filters out invalid trips, and loads the rest into a Star Schema warehouse for analytics.

**Data:** the committed data (`data/JC-202306-citibike-tripdata.csv`) and database (`citibike.db`) cover **Jersey City and Hoboken, June 2023**, not the whole NYC system. The pipeline tries the Jersey City file (`JC-<YYYYMM>`) first when it downloads a month.

The system powers a dashboard that provides:
*   **Operational Intelligence:** Station net inflow/outflow over the loaded period (historical data, not a live feed).
*   **Strategic Planning:** Historical demand analysis for fleet rebalancing and scheduling.

## Technical Architecture
The system follows a modular architecture designed for maintainability and scalability.

*   **Extraction Layer:** Python-based ELT pipeline that tries several Citi Bike file-name patterns and loads the CSV in chunks.
*   **Storage Layer:** 
    *   **Staging:** Raw ingestion tables (MySQL).
    *   **Warehouse:** Star Schema (MySQL/SQLite) optimized for OLAP queries.
*   **Transformation:** SQL-based logic to filter data anomalies (trips without a station, and "Ghost Rides" of 60 s or less) and populate the station and time dimensions.
*   **Presentation:** Streamlit dashboard with interactive Plotly visualizations.

## Engineering Highlights
This repository demonstrates professional software engineering practices:

*   **Design Patterns:** Implements the **Strategy Pattern** (`CityConfig`) to decouple the pipeline logic from specific city configurations, allowing support for multiple cities (e.g., London, Chicago) without code duplication.
*   **Automated Testing:** two `unittest` tests check the pipeline configuration (the download base URL and the default connection string), with `sqlalchemy` and `pymysql` mocked so they run without a database. The download, ingestion, SQL and dashboard are not tested yet.
*   **Continuous Integration:** a GitHub Actions workflow runs those tests on every push and pull request to `main`.
*   **Hybrid Deployment:** Supports both local MySQL environments and cloud-native SQLite deployments via automated migration scripts.

## Installation & Usage

### Prerequisites
*   Python 3.9+
*   MySQL 8.0 (for local development). `docker compose up -d` starts one that matches the default connection string.

### Configuration
All scripts and the dashboard read the MySQL connection string from `CITIBIKE_DB_URL` (default `mysql+pymysql://root:toor@localhost:3306/citibike`, a local-development placeholder). Set it to use your own credentials:
```bash
export CITIBIKE_DB_URL="mysql+pymysql://<user>:<password>@localhost:3306/citibike"
```

### Setup
1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Tests**
    Verify the system integrity before running.
    ```bash
    python -m unittest discover tests
    ```

### Execution
To rebuild the warehouse from a monthly trip file (needs MySQL):
```bash
python etl_pipeline.py --month 202306       # download (if needed) and load staging_trips
python execute_sql_scripts.py               # create the schema and run the transformations; exits non-zero on any SQL error
python tools/migrate_to_sqlite.py           # optional: copy the warehouse into citibike.db for the cloud dashboard
```

Launch the dashboard application. The system will automatically detect the environment (Cloud vs Local) and configure the database connection accordingly.
```bash
python -m streamlit run dashboard/app.py
```

---
*Maintained by Mahboob Alam*