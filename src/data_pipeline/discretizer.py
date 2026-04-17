import pandas as pd
import numpy as np
from src.config import THRESHOLDS

class FeatureDiscretizer:
    def discretize(self, df: pd.DataFrame) -> pd.DataFrame:
        # Avoid df.copy() to save memory. We operate directly on the passed df.
        
        # 1. Vectorized conditional logic using np.select
        wind_conds = [
            df['MAGNITUDE'] > THRESHOLDS['wind_speed']['extreme'],
            df['MAGNITUDE'] > THRESHOLDS['wind_speed']['high']
        ]
        wind_choices = ['EXTREME_WIND', 'HIGH_WIND']
        df['WIND_ITEM'] = np.select(wind_conds, wind_choices, default=None)
        
        # 2. Vectorized logic for damage
        damage_conds = [
            df['DAMAGE_PROPERTY'] > THRESHOLDS['damage_property']['severe'],
            df['DAMAGE_PROPERTY'] > THRESHOLDS['damage_property']['moderate']
        ]
        damage_choices = ['SEVERE_DAMAGE', 'MODERATE_DAMAGE']
        df['DAMAGE_ITEM'] = np.select(damage_conds, damage_choices, default=None)
        
        # 3. Fast list compression to combine non-null items 
        # (Much more memory-efficient than apply(axis=1))
        events = df['EVENT_TYPE'].values
        winds = df['WIND_ITEM'].values
        damages = df['DAMAGE_ITEM'].values
        
        # Fast zip-based comprehensions
        df['ITEMS'] = [
            [e, w, d] for e, w, d in zip(events, winds, damages)
        ]
        # Remove None values from the lists
        df['ITEMS'] = [[x for x in item_list if x is not None] for item_list in df['ITEMS']]
        
        # Clean up intermediate columns to free up RAM early
        df.drop(columns=['WIND_ITEM', 'DAMAGE_ITEM'], inplace=True)
        
        return df