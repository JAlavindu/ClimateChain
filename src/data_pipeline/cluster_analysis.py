import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class ClimateClusterer:
    def __init__(self, n_clusters=4, random_state=42):
        """
        Initializes the K-Means clustering model.
        n_clusters: The number of distinct climate profiles to discover.
        """
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        self.scaler = StandardScaler()

    def cluster_states(self, nasa_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregates historical continuous data by state and assigns each state to a climate cluster.
        Returns a DataFrame mapping STATE -> CLIMATE_CLUSTER.
        """
        print(f"Running Cluster Analysis to find {self.n_clusters} climate profiles...")
        
        # 1. Aggregate continuous features to get the historical baseline for each state
        # We use T2M (Temperature) and PRECTOTCORR (Precipitation) as seen in your phase 6
        state_profiles = nasa_df.groupby('STATE')[['T2M', 'PRECTOTCORR']].mean().reset_index()
        
        # 2. Scale the data (K-Means is distance-based, so scaling is mandatory)
        X_scaled = self.scaler.fit_transform(state_profiles[['T2M', 'PRECTOTCORR']])
        
        # 3. Fit K-Means and predict cluster IDs
        state_profiles['CLUSTER_ID'] = self.model.fit_predict(X_scaled)
        
        # Format the cluster label as a categorical item for FP-Growth (e.g., "PROFILE_0")
        state_profiles['CLIMATE_CLUSTER'] = "PROFILE_" + state_profiles['CLUSTER_ID'].astype(str)
        
        print("Cluster Analysis Complete: States have been grouped into data-driven profiles.")
        
        # Return just the mapping of State to Cluster
        return state_profiles[['STATE', 'CLIMATE_CLUSTER']]