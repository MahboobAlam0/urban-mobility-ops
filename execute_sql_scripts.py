import argparse
import sys
from sqlalchemy import create_engine, text
import os

def run_sql_file(filename, engine):
    """Run every statement in a file. Returns the number of statements that failed."""
    print(f"Deploying logic from {filename}...")
    with open(filename, 'r') as f:
      
        content = f.read()
        
        commands = content.split(';')
        failures = 0
        
        with engine.connect() as conn:
            for command in commands:
                command = command.strip()
                if command:
                    try:
                        conn.execute(text(command))
                        conn.commit()
                    except Exception as e:
                        failures += 1
                        print(f"Error executing command: {command[:50]}... \nError: {e}")
                        
    print(f"Finished {filename} ({failures} failed statement(s))")
    return failures

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SQL Scripts")
    parser.add_argument("--db", type=str, default=os.environ.get("CITIBIKE_DB_URL", "mysql+pymysql://root:toor@localhost:3306/citibike"),
                        help="DB connection string (default: $CITIBIKE_DB_URL)")
    args = parser.parse_args()
    
    engine = create_engine(args.db)
    
    # 1. Run DDL. Stop here if it failed: the transformations need the tables.
    if run_sql_file("sql/ddl_schema.sql", engine):
        print("DDL failed; not running the transformations.")
        sys.exit(1)
    
    # 2. Run Transformations
    if run_sql_file("sql/transform_logic.sql", engine):
        print("Some transformation statements failed; see the errors above.")
        sys.exit(1)
    
    print("All SQL scripts executed successfully.")
