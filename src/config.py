import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed"

MONGO_URI = os.getenv("ATLAS_URI", "mongodb://localhost:27017/")

# Thresholds for discretizing continuous variables
THRESHOLDS = {
    "wind_speed": {"high": 50, "extreme": 80},  # Knots
    "damage_property": {"moderate": 50000, "severe": 500000} # Dollars
}

# Transaction grouping boundaries
SPATIAL_GRANULARITY = "STATE" # or "CZ_NAME" for county
TEMPORAL_GRANULARITY = "MONTH_NAME"