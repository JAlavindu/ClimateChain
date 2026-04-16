import pandas as pd
from src.config import SPATIAL_GRANULARITY, TEMPORAL_GRANULARITY

class TransactionBuilder:
    def build_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Groups data by Location and Time. 
        Each row becomes a 'Transaction ID' with a set of 'Items'.
        """
        # Explode the list of items so we can group them
        df_exploded = df.explode('ITEMS').dropna(subset=['ITEMS'])
        
        # Create a unique transaction ID (e.g., "TEXAS_2005_JANUARY")
        df_exploded['TRANSACTION_ID'] = (
            df_exploded[SPATIAL_GRANULARITY].astype(str) + "_" + 
            df_exploded['YEAR'].astype(str) + "_" + 
            df_exploded[TEMPORAL_GRANULARITY].astype(str)
        )
        
        # Group by Transaction ID and get unique items in that bucket
        transactions = df_exploded.groupby('TRANSACTION_ID')['ITEMS'].unique().reset_index()
        
        # Optional metadata for later NoSQL insertion
        transactions['STATE'] = transactions['TRANSACTION_ID'].apply(lambda x: x.split('_')[0])
        transactions['YEAR'] = transactions['TRANSACTION_ID'].apply(lambda x: x.split('_')[1])
        transactions['MONTH'] = transactions['TRANSACTION_ID'].apply(lambda x: x.split('_')[2])
        
        return transactions