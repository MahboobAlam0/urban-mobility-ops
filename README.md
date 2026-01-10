# Urban Mobility Operations Center
A modular Data Engineering pipeline optimizing fleet logistics for bike-share systems.

![CI Status](https://github.com/MahboobAlam0/urban-mobility-ops/actions/workflows/ci.yml/badge.svg)
![Tests](https://img.shields.io/badge/tests-passing-green)

---

## Project Overview
This project implements an end-to-end ELT (Extract, Load, Transform) pipeline to solve station imbalance issues in the NYC CitiBike network. It ingests raw trip data, validates it against business rules, and loads it into a Star Schema warehouse for analytics.

The system powers a dashboard that provides:
*   **Operational Intelligence:** Real-time visibility into station flux (Net Inflow/Outflow).
*   **Strategic Planning:** Historical demand analysis for fleet rebalancing and scheduling.

## Technical Architecture
The system follows a modular architecture designed for maintainability and scalability.

*   **Extraction Layer:** Python-based ELT pipeline with automatic retry logic and chunk-based processing for large datasets.
*   **Storage Layer:** 
    *   **Staging:** Raw ingestion tables (MySQL).
    *   **Warehouse:** Star Schema (MySQL/SQLite) optimized for OLAP queries.
*   **Transformation:** SQL-based logic to filter data anomalies (e.g., "Ghost Rides" < 60s) and populate dimension tables.
*   **Presentation:** Streamlit dashboard with interactive Plotly visualizations.

## Engineering Highlights
This repository demonstrates professional software engineering practices:

*   **Design Patterns:** Implements the **Strategy Pattern** (`CityConfig`) to decouple the pipeline logic from specific city configurations, allowing support for multiple cities (e.g., London, Chicago) without code duplication.
*   **Automated Testing:** Unit test suite using `unittest` and `mock` to validate configuration and logic without requiring external dependencies options.
*   **Continuous Integration:** GitHub Actions workflow ensuring test stability on every commit.
*   **Hybrid Deployment:** Supports both local MySQL environments and cloud-native SQLite deployments via automated migration scripts.

## Installation & Usage

### Prerequisites
*   Python 3.9+
*   MySQL 8.0 (for local development)

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
Launch the dashboard application. The system will automatically detect the environment (Cloud vs Local) and configure the database connection accordingly.
```bash
python -m streamlit run dashboard/app.py
```

---
*Maintained by Mahboob Alam*