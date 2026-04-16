import pandas as pd
import glob
import os
from src.config import RAW_DATA_PATH

class NOAALoader:
    def __init__(self, data_dir=RAW_DATA_PATH):
        self.data_dir = data_dir

    def load_all_years(self) -> pd.DataFrame:
        """Loads all NOAA storm events CSV files from 2005 to 2020."""
        # Assuming files are named like 'StormEvents_details-ftp_v1.0_d2005_*.csv'
        file_pattern = os.path.join(self.data_dir, "StormEvents_details*.csv")
        files = glob.glob(file_pattern)
        
        if not files:
            raise FileNotFoundError(f"No CSV files found in {self.data_dir}")
            
        dfs = []
        for file in files:
            print(f"Loading {file}...")
            # Use specific columns to save memory
            df = pd.read_csv(file, usecols=[
                'YEAR', 'MONTH_NAME', 'STATE', 'CZ_NAME', 
                'EVENT_TYPE', 'MAGNITUDE', 'DAMAGE_PROPERTY'
            ], low_memory=False)
            dfs.append(df)
            
        return pd.concat(dfs, ignore_index=True)