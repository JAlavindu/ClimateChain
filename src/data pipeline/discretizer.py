import pandas as pd
from src.config import THRESHOLDS

class FeatureDiscretizer:
    def discretize(self, df: pd.DataFrame) -> pd.DataFrame:
        df_disc = df.copy()
        
        # Discretize Events with Magnitude (e.g. Wind)
        df_disc['WIND_ITEM'] = df_disc['MAGNITUDE'].apply(self._discretize_wind)
        
        # Discretize Damage
        df_disc['DAMAGE_ITEM'] = df_disc['DAMAGE_PROPERTY'].apply(self._discretize_damage)
        
        # Combine the actual event type with discretized attributes into a single list of items
        df_disc['ITEMS'] = df_disc.apply(
            lambda row: [x for x in [row['EVENT_TYPE'], row['WIND_ITEM'], row['DAMAGE_ITEM']] if x is not None], 
            axis=1
        )
        return df_disc

    def _discretize_wind(self, magnitude):
        if magnitude > THRESHOLDS['wind_speed']['extreme']: return 'EXTREME_WIND'
        if magnitude > THRESHOLDS['wind_speed']['high']: return 'HIGH_WIND'
        return None

    def _discretize_damage(self, damage):
        if damage > THRESHOLDS['damage_property']['severe']: return 'SEVERE_DAMAGE'
        if damage > THRESHOLDS['damage_property']['moderate']: return 'MODERATE_DAMAGE'
        return None