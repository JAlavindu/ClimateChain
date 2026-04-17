import pandas as pd
import requests
import time
import os
from src.config import RAW_DATA_PATH

class NastFetcher:
    def __init__(self, start_year=2005, end_year=2020):
        self.start_year = start_year
        self.end_year = end_year
        # Central coordinates for a sample of US states to avoid massive API payloads
        self.states_coords = {
            "TEXAS": {"lat": 31.9686, "lon": -99.9018},
            "CALIFORNIA": {"lat": 36.7783, "lon": -119.4179},
            "FLORIDA": {"lat": 27.9944, "lon": -81.7603},
            "NEW_YORK": {"lat": 43.2994, "lon": -74.2179},
            "ILLINOIS": {"lat": 40.6331, "lon": -89.3985},
            "OHIO": {"lat": 40.4173, "lon": -82.9071},
            "GEORGIA": {"lat": 32.1656, "lon": -82.9001},
            "NORTH_CAROLINA": {"lat": 32.5093, "lon": -83.4412},
            "MICHIGAN": {"lat": 44.3148, "lon": -85.6024},
            "PENNSYLVANIA": {"lat": 41.2033, "lon": -77.1945},
            # Add more states as needed for your scope
        }

    def fetch_climate_data(self) -> pd.DataFrame:
        """
        Calls NASA POWER API for Temperature (T2M) and Precipitation (PRECTOTCORR)
        Resolves to a monthly temporal average.
        """
        all_data = []
        base_url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
        
        print("Fetching continuous climate data from NASA POWER...")
        
        for state, coords in self.states_coords.items():
            print(f"Requesting data for {state}...")
            params = {
                "parameters": "T2M,PRECTOTCORR",
                "community": "RE",
                "longitude": coords["lon"],
                "latitude": coords["lat"],
                "start": self.start_year,
                "end": self.end_year,
                "format": "JSON"
            }
            
            response = requests.get(base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get("properties", {}).get("parameter", {})
                
                # NASA returns data with keys like "200501" (Year+Month)
                for param, timeseries in features.items():
                    for yyyymm, value in timeseries.items():
                        # The API returns '13' (annual avg) as an extra month. Ignore it.
                        if len(yyyymm) == 6 and not yyyymm.endswith("13"):
                            all_data.append({
                                "STATE": state,
                                "YEAR": int(yyyymm[:4]),
                                "MONTH_NUM": int(yyyymm[4:]),
                                "METRIC": param,
                                "VALUE": value
                            })
            else:
                print(f"Failed to fetch {state}: HTTP {response.status_code}")
                
            # Respect NASA's API rate limits
            time.sleep(1)
            
        print("NASA Data fetching complete.")
        df = pd.DataFrame(all_data)
        
        # Pivot the dataframe so T2M and PRECTOTCORR are columns
        df_pivoted = df.pivot_table(
            index=["STATE", "YEAR", "MONTH_NUM"], 
            columns="METRIC", 
            values="VALUE"
        ).reset_index()
        
        # Map month numbers back to names to match NOAA data
        month_map = {
            1: "JANUARY", 2: "FEBRUARY", 3: "MARCH", 4: "APRIL",
            5: "MAY", 6: "JUNE", 7: "JULY", 8: "AUGUST",
            9: "SEPTEMBER", 10: "OCTOBER", 11: "NOVEMBER", 12: "DECEMBER"
        }
        df_pivoted['MONTH_NAME'] = df_pivoted['MONTH_NUM'].map(month_map)
        
        return df_pivoted

    def save_data(self, df: pd.DataFrame):
        os.makedirs(RAW_DATA_PATH, exist_ok=True)
        out_path = os.path.join(RAW_DATA_PATH, "nasa_climate_baseline.csv")
        df.to_csv(out_path, index=False)
        print(f"Saved {len(df)} NASA records to {out_path}")