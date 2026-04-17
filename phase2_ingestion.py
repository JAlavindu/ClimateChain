import json
import os
from src.database.mongo_schema import MongoManager
from src.config import PROCESSED_DATA_PATH, MONGO_URI

def run_phase_2():
    print("1. Initializing MongoDB Connection...")
    # Using the secure URI loaded from .env via config.py
    mongo = MongoManager(uri=MONGO_URI) 
    
    # Optional: Clear old data for a fresh run
    mongo.clear_database()
    
    # Establish performance rules (indexing)
    mongo.setup_indexes()

    print("2. Loading formatted JSON transactions...")
    json_path = os.path.join(PROCESSED_DATA_PATH, "climate_transactions.json")
    
    transactions_list = []
    with open(json_path, 'r') as f:
        for line in f:
            if line.strip():
                transactions_list.append(json.loads(line))

    print(f"3. Ingesting {len(transactions_list)} records into MongoDB...")
    mongo.insert_transactions(transactions_list)
    print("Phase 2 complete! Data is ready for Association Rule Mining.")

if __name__ == "__main__":
    run_phase_2()