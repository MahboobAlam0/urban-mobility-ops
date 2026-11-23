import pandas as pd
from sqlalchemy import create_engine
import os
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DB_Migration")

# Config
MYSQL_CONN = os.environ.get("CITIBIKE_DB_URL", "mysql+pymysql://root:toor@localhost:3306/citibike")
SQLITE_DB = "citibike.db"
SQLITE_CONN = f"sqlite:///{SQLITE_DB}"

def migrate():
        
    logger.info("Connecting to Local MySQL...")
    try:
        mysql_engine = create_engine(MYSQL_CONN)
        # Test connection
        with mysql_engine.connect() as conn:
            pass
    except Exception as e:
        logger.error(f"Could not connect to MySQL: {e}")
        return

    logger.info("Connecting to SQLite...")
    sqlite_engine = create_engine(SQLITE_CONN)

    tables_to_migrate = [
        "dim_station", 
        "fact_trips",
        "dim_time"  # not used by the dashboard queries yet
    ]

    for table in tables_to_migrate:
        logger.info(f"Migrating table: {table}...")
        try:
            # chunksize used to avoiding MemoryError on large tables
            for i, chunk in enumerate(pd.read_sql_table(table, mysql_engine, chunksize=50000)):
                chunk.to_sql(table, sqlite_engine, if_exists='replace' if i==0 else 'append', index=False)
                logger.info(f"  - Cleaned and moved chunk {i+1}")
        except ValueError:
            logger.warning(f"Table {table} not found in MySQL. Skipping.")
        except Exception as e:
            logger.error(f"Error migrating {table}: {e}")

    logger.info("Migration Complete! 🎉")
    logger.info(f"File created: {os.path.abspath(SQLITE_DB)}")
    logger.info("You can now commit 'citibike.db' to GitHub.")

if __name__ == "__main__":
    migrate()
