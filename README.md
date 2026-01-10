# Urban Mobility Operations Center
*> A Data Engineering project optimizing fleet logistics for NYC CitiBike.*

---

## The Story: Why this project exists
Imagine running a bike-share system in New York City. 
Every morning, thousands of commuters ride from the suburbs into Manhattan.
*   **The Problem:** By 9:00 AM, the suburban stations are empty (lost customers), and the Manhattan stations are overflowing (no place to park).
*   **The Mission:** I wanted to build a system that tells the Operations Team **exactly where to move the bikes** before the problem happens.

This isn't just a dashboard—it's a full "Data Pipeline" that mimics the real-world infrastructure used by companies like Uber or Lyft.

---

## How it Works 
I built three main components to solve this problem:

### 1. The "Collector" (ETL Pipeline)
*   **What it is:** A Python script that connects to the web.
*   **What it does:** It automatically finds the latest trip data, downloads it, and "cleans" it (removing broken records or ghost rides shorter than 60 seconds).
*   *Think of it as the trucks collecting raw materials.*

### 2. The "Warehouse" (SQL Database)
*   **What it is:** A MySQL Database designed with a "Star Schema."
*   **What it does:** It organizes the messy data into neat folders: "Stations", "Trips", and "Timestamps".
*   *Think of it as a perfectly organized filing cabinet that makes finding answers 10x faster.*

### 3. The "Command Center" (Dashboard)
*   **What it is:** A website built with Python (Streamlit).
*   **What it does:** It answers two business questions:
    *   **Operational:** *"Which stations are empty right now?"* (Net Flow Metric)
    *   **Strategic:** *"Do we need more staff on weekends?"* (Historical Trends)

---

## How to Run this Project

### 1. Pre-requisites
You need **Python** installed on your machine.

### 2. Installation
Open your terminal (PowerShell or Command Prompt) and run:
```bash
# Install the necessary tools
pip install -r requirements.txt
```

### 3. Setup the Database (Automatic)
I wrote a helper script so you don't have to engage with complex database commands. It converts the data into a portable format automatically:
```bash
python tools/migrate_to_sqlite.py
```

### 4. Launch the App
Start the website:
```bash
python -m streamlit run dashboard/app.py
```
*The website should open automatically in your browser!*

---

## What I Learned
Building this project taught me that **Clean Data > Big Data**. 
Initially, my charts looked wrong because of "Ghost Rides" (trips lasting 3 seconds). By implementing strict logic in `transform_logic.sql`, I ensured that the decision-support metrics were actually reliable.

---
*Created by Mahboob Alam*