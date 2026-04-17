import pandas as pd
import numpy as np

class DataCleaner:
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df_cleaned = df.copy()
        
        # 1. Standardize text columns
        df_cleaned['STATE'] = df_cleaned['STATE'].str.upper()
        df_cleaned['EVENT_TYPE'] = df_cleaned['EVENT_TYPE'].str.upper().str.replace(' ', '_')
        
        # 2. Parse property damage strings (from "50K" to 50000)
        df_cleaned['DAMAGE_PROPERTY'] = df_cleaned['DAMAGE_PROPERTY'].apply(self._parse_damage)
        
        # 3. Handle missing values
        df_cleaned['MAGNITUDE'] = df_cleaned['MAGNITUDE'].fillna(0)
        
        return df_cleaned

    def _parse_damage(self, val):
        if pd.isna(val): return 0
        if isinstance(val, (int, float)): return val
        
        val = str(val).upper()
        multiplier = 1
        if val.endswith('K'): multiplier = 1000
        elif val.endswith('M'): multiplier = 1_000_000
        elif val.endswith('B'): multiplier = 1_000_000_000
        
        try:
            return float(val.rstrip('KMB')) * multiplier
        except ValueError:
            return 0