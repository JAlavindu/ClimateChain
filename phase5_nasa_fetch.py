from src.data_pipeline.nasa_power import NastFetcher

def run_phase_5():
    fetcher = NastFetcher()
    df_nasa = fetcher.fetch_climate_data()
    fetcher.save_data(df_nasa)

if __name__ == "__main__":
    run_phase_5()