import argparse
from sqlalchemy import create_engine, text
import os

def run_sql_file(filename, engine):
   
    print(f"Deploying logic from {filename}...")
    with open(filename, 'r') as f:
      
        content = f.read()
        
        commands = content.split(';')
        
        with engine.connect() as conn:
            for command in commands:
                command = command.strip()
                if command:
                    try:
                        conn.execute(text(command))
                        conn.commit()
                    except Exception as e:
                        print(f"Error executing command: {command[:50]}... \nError: {e}")
                        
    print(f"Finished {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SQL Scripts")
    parser.add_argument("--db", type=str, default="mysql+pymysql://root:password@localhost:3306/citibike", help="DB Connection String")
    args = parser.parse_args()
    
    engine = create_engine(args.db)
    
    # 1. Run DDL
    run_sql_file("sql/ddl_schema.sql", engine)
    
    # 2. Run Transformations
    run_sql_file("sql/transform_logic.sql", engine)
    
    print("All SQL scripts executed successfully.")
