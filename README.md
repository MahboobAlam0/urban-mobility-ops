# 🚲 Urban Mobility Operations Center
*> A modular Data Engineering pipeline for fleet optimization, featuring a Strategy Pattern for multi-city support.*

![CI Status](https://github.com/MahboobAlam0/urban-mobility-ops/actions/workflows/ci.yml/badge.svg)
![Tests](https://img.shields.io/badge/tests-passing-green)

---

## 🏗️ Architecture & Engineering
This project is built to "Senior Engineer" standards, featuring:
*   **Modular Architecture**: Uses a **Star Schema** for data warehousing.
*   **Design Patterns**: Implements the **Strategy Pattern** in the ETL pipeline (`CityConfig`) to allow easy expansion to other cities (London/Chicago) without rewriting logic.
*   **Automated Testing**: Includes a Unit Test suite (`tests/`) running on **GitHub Actions**.
*   **Hybrid Deployment**: Runs locally on MySQL and deploys cloud-natively using SQLite migration.

---

## 📖 The Business Problem
By 9:00 AM, suburban stations are empty while downtown docks are full. 
*   **The Mission**: Build a decision-support system to predict rebalancing needs.
*   **The Tech**: A robust Python/SQL pipeline that ingests raw trip data, validates it (Ghost Ride filtering), and visualizes Net Flow.

---

## 🛠️ Components

### 1. Collector (ETL Pipeline)
*   **Tech**: Python, Pandas, SQLAlchemy.
*   **Features**: Auto-retry logic, Chunk processing for large files, and dynamic Config injection.

### 2. Warehouse (SQL)
*   **Tech**: MySQL 8.0 / SQLite (Cloud).
*   **Schema**: Star Schema (Fact Trips, Dim Station, Dim Time).

### 3. Dashboard (Streamlit)
*   **Tech**: Streamlit, Plotly.
*   **Analysis**: Real-time "Net Flow" and Historical "Demand Curves".

---

## 🚀 How to Run

### Quick Start
1.  **Install**: `pip install -r requirements.txt`
2.  **Test**: `python -m unittest discover tests` (Verify system integrity)
3.  **Run**: `python -m streamlit run dashboard/app.py`

*Note: The system automatically switches between MySQL (Local) and SQLite (Cloud) modes.*

---
*Created by Mahboob Alam*