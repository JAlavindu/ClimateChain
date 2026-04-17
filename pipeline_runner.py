import os
from src.data_pipeline.loader import NOAALoader
from src.data_pipeline.cleaner import DataCleaner
from src.data_pipeline.discretizer import FeatureDiscretizer
from src.data_pipeline.transaction import TransactionBuilder
from src.config import PROCESSED_DATA_PATH

def run_phase_1():
    print("1. Loading raw data...")
    loader = NOAALoader()
    df_raw = loader.load_all_years()
    
    print("2. Cleaning data...")
    cleaner = DataCleaner()
    df_clean = cleaner.clean(df_raw)
    
    print("3. Discretizing features...")
    discretizer = FeatureDiscretizer()
    df_discrete = discretizer.discretize(df_clean)
    
    print("4. Building transactions...")
    builder = TransactionBuilder()
    transactions = builder.build_transactions(df_discrete)
    
    # Save output for Phase 2
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    out_path = os.path.join(PROCESSED_DATA_PATH, "climate_transactions.json")
    
    # Saving as records/JSON is perfect preparation for MongoDB (Phase 2)
    transactions.to_json(out_path, orient="records", lines=True)
    print(f"Phase 1 complete! Wrote {len(transactions)} transactions to {out_path}")

if __name__ == "__main__":
    run_phase_1()