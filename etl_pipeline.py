import argparse
import os
import requests
import zipfile
import logging
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
import pymysql

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("CitiBike_ETL")

# --- CONFIGURATION (STRATEGY PATTERN) ---
class CityConfig:
    """Strategy for Multi-City Support (NYC, London, etc.)"""
    def __init__(self, city_code, base_url, chunk_size, default_db):
        self.CITY_CODE = city_code
        self.BASE_URL = base_url
        self.CHUNK_SIZE = chunk_size
        self.DEFAULT_DB = default_db

# Configuration for NYC CitiBike
NYC_CONFIG = CityConfig(
    city_code="NYC",
    base_url="https://s3.amazonaws.com/tripdata",
    chunk_size=100000,
    default_db="mysql+pymysql://root:toor@localhost:3306/citibike"
)

# Active Strategy (Switch this to change target city)
Config = NYC_CONFIG

class ETLException(Exception):
    pass

def get_db_engine(connection_string):
    return create_engine(connection_string, pool_recycle=3600)

def ensure_database_exists(db_conn_str):
    if "mysql" not in db_conn_str:
        return

    try:
        url = make_url(db_conn_str)
        db_name = url.database
        
        logger.info(f"Safety Check: Verifying database '{db_name}' exists...")
        
        # Connect to server root (no DB) to perform admin task
        conn = pymysql.connect(
            host=url.host, 
            user=url.username, 
            password=url.password, 
            port=url.port
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        conn.commit()
        conn.close()
        logger.info("Database check passed. We are good to go.")
        
    except Exception as e:
        logger.warning(f"Could not verify database: {e}. Attempting to proceed anyway.")

def fetch_dataset(yyyymm, output_dir="data"):
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    target_zip = os.path.join(output_dir, f"{yyyymm}_data.zip")
    
    # Check if we already have the raw csv
    # (Simple check, could be improved with checksums)
    for f in os.listdir(output_dir):
        if f.endswith(".csv") and yyyymm in f:
            logger.info(f"Found existing data: {f}")
            return os.path.join(output_dir, f)

    patterns = [
        f"JC-{yyyymm}-citibike-tripdata.csv.zip", # Jersey City (often more reliable URL)
        f"{yyyymm}-citibike-tripdata.csv.zip",
        f"{yyyymm}-citibike-tripdata.zip"
    ]

    downloaded = False
    for filename in patterns:
        url = f"{Config.BASE_URL}/{filename}"
        logger.info(f"Attempting download: {url}")
        
        try:
            with requests.get(url, stream=True) as r:
                if r.status_code == 200:
                    with open(target_zip, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    downloaded = True
                    break
        except requests.RequestException as e:
            logger.error(f"Network error: {e}")
            continue

    if not downloaded:
        raise ETLException(f"Could not download data for {yyyymm} from any known bucket.")

    logger.info("Extracting archive...")
    extracted_path = None
    with zipfile.ZipFile(target_zip, 'r') as z:
        z.extractall(output_dir)
        # Find the actual CSV
        csvs = [f for f in z.namelist() if f.endswith('.csv') and '__MACOSX' not in f]
        if csvs:
            extracted_path = os.path.join(output_dir, csvs[0])

    if not extracted_path:
        raise ETLException("Zip archive contained no valid CSV files.")
        
    return extracted_path

def ingestion_pipeline(csv_file, db_string, limit=None):
    engine = get_db_engine(db_string)
    
    logger.info(f"Starting ingestion for {csv_file}")
    
    try:
        # Using iterator to handle memory constraints
        with pd.read_csv(csv_file, chunksize=Config.CHUNK_SIZE) as reader:
            for i, chunk in enumerate(reader):
                if limit and i * Config.CHUNK_SIZE >= limit:
                    logger.info("Hit safeguard limit. Stopping ingestion.")
                    break

                # Snake_case normalization
                chunk.columns = [c.lower().replace(' ', '_') for c in chunk.columns]
                
                chunk.to_sql(
                    'staging_trips', 
                    engine, 
                    if_exists='replace' if i == 0 else 'append', 
                    index=False
                )
                logger.info(f"Committed chunk {i+1} ({len(chunk)} rows)")
                
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", type=str, default="202306", help="YYYYMM format")
    parser.add_argument("--db", type=str, default=Config.DEFAULT_DB)
    parser.add_argument("--limit", type=int, default=500000, help="Row limit for dev env")
    
    args = parser.parse_args()
    
    try:
        ensure_database_exists(args.db)
        raw_file = fetch_dataset(args.month)
        ingestion_pipeline(raw_file, args.db, limit=args.limit)
        logger.info("Pipeline finished successfully.")
    except Exception as e:
        logger.critical(f"Pipeline crashed: {e}")
        exit(1)
