import pandas as pd
from sklearn.ensemble import IsolationForest

class OutlierDetector:
    def __init__(self, contamination=0.01, random_state=42):
        """
        Initializes the Isolation Forest model for Outlier Analysis.
        contamination: The proportion of outliers in the data set (e.g., top 1% most extreme).
        """
        self.model = IsolationForest(
            n_estimators=100, 
            contamination=contamination, 
            random_state=random_state
        )

    def detect_anomalies(self, nasa_df: pd.DataFrame, features: list) -> pd.DataFrame:
        """
        Applies Isolation Forest to detect multivariate climate anomalies 
        based on continuous variables from NASA.
        """
        print(f"Running Outlier Analysis on {len(nasa_df)} monthly records...")
        
        # Create a copy to avoid SettingWithCopyWarning
        df_out = nasa_df.copy()
        
        # Ensure we only use rows without missing values for fitting the model
        X = df_out[features].dropna()
        
        # Fit the model and predict (-1 for outliers, 1 for inliers)
        # Default all rows to 1 (inlier) first
        df_out['anomaly_score'] = 1 
        df_out.loc[X.index, 'anomaly_score'] = self.model.fit_predict(X)
        
        # Create a clean boolean flag: True if it's an outlier
        df_out['is_anomalous_month'] = df_out['anomaly_score'] == -1
        
        anomalies_found = df_out['is_anomalous_month'].sum()
        print(f"Outlier Analysis Complete: Identified {anomalies_found} extreme climate anomalies.")
        
        # Clean up temporary columns
        df_out = df_out.drop(columns=['anomaly_score'])
        
        return df_out