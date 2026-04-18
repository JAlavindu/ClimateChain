import pandas as pd
import json
import os
from src.config import PROCESSED_DATA_PATH, RAW_DATA_PATH

def run_phase_6():
    print("1. Loading NOAA Transactions and NASA Climate Data...")
    noaa_path = os.path.join(PROCESSED_DATA_PATH, "climate_transactions.json")
    noaa_df = pd.read_json(noaa_path, orient="records", lines=True)

    nasa_path = os.path.join(RAW_DATA_PATH, "nasa_climate_baseline.csv")
    nasa_df = pd.read_csv(nasa_path)

    print("2. Discretizing NASA Data (Percentile-based Anomalies)...")
    def discretize_temp(x):
        return pd.qcut(x, q=5, labels=['EXTREME_COLD', 'COLD', 'NORMAL_T', 'WARM', 'EXTREME_HEAT'], duplicates='drop')

    def discretize_rain(x):
        return pd.qcut(x, q=5, labels=['SEVERE_DROUGHT', 'DRY', 'NORMAL_R', 'WET', 'EXTREME_RAIN'], duplicates='drop')

    nasa_df['TEMP_CAT'] = nasa_df.groupby('STATE')['T2M'].transform(discretize_temp)
    nasa_df['RAIN_CAT'] = nasa_df.groupby('STATE')['PRECTOTCORR'].transform(discretize_rain)

    def extract_nasa_items(row):
        items = []
        if row['TEMP_CAT'] in ['EXTREME_HEAT', 'EXTREME_COLD']:
            items.append(str(row['TEMP_CAT']))
        if row['RAIN_CAT'] in ['SEVERE_DROUGHT', 'EXTREME_RAIN']:
            items.append(str(row['RAIN_CAT']))
        return items

    nasa_df['NASA_ITEMS'] = nasa_df.apply(extract_nasa_items, axis=1)

    print("3. Merging NOAA and NASA Data...")
    # CLEAN THE TRANSACTION IDs DIRECTLY TO AVOID DATA TYPE MISMATCH
    # Strip any decimal points like '.0' from the NOAA Transaction IDs
    noaa_df['TRANSACTION_ID'] = noaa_df['TRANSACTION_ID'].str.replace(r'\.0_', '_', regex=True)

    noaa_df['TRANSACTION_ID'] = noaa_df['TRANSACTION_ID'].str.upper()

    nasa_df['MONTH_NAME'] = nasa_df['MONTH_NAME'].str.upper()
    nasa_df['TRANSACTION_ID'] = nasa_df['STATE'] + "_" + nasa_df['YEAR'].astype(str) + "_" + nasa_df['MONTH_NAME']

    # Merge NASA items into NOAA transactions base
    merged_df = pd.merge(nasa_df, noaa_df[['TRANSACTION_ID', 'ITEMS']], on='TRANSACTION_ID', how='left')

    # Fill NaNs for months with no NOAA events with empty lists
    merged_df['ITEMS'] = merged_df['ITEMS'].apply(lambda x: x if isinstance(x, list) else [])

    # Combine items for current month
    merged_df['ALL_ITEMS'] = merged_df['NASA_ITEMS'] + merged_df['ITEMS']

    print("4. Applying Temporal Sequencing (3-Month Lags)...")
    merged_df['DATE'] = pd.to_datetime(merged_df['YEAR'].astype(str) + '-' + merged_df['MONTH_NUM'].astype(str) + '-01')
    merged_df = merged_df.sort_values(['STATE', 'DATE'])

    def list_combiner(items, prefix):
        if not isinstance(items, list): return []
        return [f"{prefix}_{item}" for item in items]

    merged_df['LAG1'] = merged_df.groupby('STATE')['ALL_ITEMS'].shift(1)
    merged_df['LAG2'] = merged_df.groupby('STATE')['ALL_ITEMS'].shift(2)
    merged_df['LAG3'] = merged_df.groupby('STATE')['ALL_ITEMS'].shift(3)

    merged_df['LAG1'] = merged_df['LAG1'].apply(lambda x: list_combiner(x, 'T-1'))
    merged_df['LAG2'] = merged_df['LAG2'].apply(lambda x: list_combiner(x, 'T-2'))
    merged_df['LAG3'] = merged_df['LAG3'].apply(lambda x: list_combiner(x, 'T-3'))

    merged_df['FINAL_TRANSACTION'] = merged_df['LAG3'] + merged_df['LAG2'] + merged_df['LAG1'] + merged_df['ALL_ITEMS']

    final_df = merged_df.dropna(subset=['LAG3']).copy()

    output_df = final_df[['TRANSACTION_ID', 'STATE', 'YEAR', 'MONTH_NAME', 'FINAL_TRANSACTION']].rename(
        columns={'FINAL_TRANSACTION': 'ITEMS', 'MONTH_NAME': 'MONTH'}
    )

    out_path = os.path.join(PROCESSED_DATA_PATH, "sequenced_transactions.json")
    output_df.to_json(out_path, orient="records", lines=True)
    print(f"Phase 6 Complete! Dataset is now fused properly.")

if __name__ == "__main__":
    run_phase_6()