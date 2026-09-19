import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def calculate_cancellation_probabilities(sensor_df):
    """
    Analyzes behavioral metrics across the fleet and calculates 
    an anomaly score translated into a 'Cancellation Probability'.
    """
    # Features representing behavioral trends and current state
    features = [
        "vibration_level",
        "engine_temp_c",
        "oil_quality_index",
        "vibration_7d_trend",
        "temp_volatility",
        "oil_degradation_rate",
        "past_cancellations"
    ]
    
    # Ensure features exist in dataframe
    available_features = [f for f in features if f in sensor_df.columns]
    
    if not available_features:
        # Fallback if no valid columns exist
        sensor_df["cancellation_probability"] = 0.0
        return sensor_df
        
    X = sensor_df[available_features].copy()
    
    # Train Isolation Forest on the fleet's behavioral data
    # Contamination is the expected proportion of outliers (set to 0.15 to flag high-risk anomalies)
    iso_forest = IsolationForest(contamination=0.15, random_state=42)
    iso_forest.fit(X)
    
    # The anomaly_score typically ranges from -0.5 to 0.5. 
    # Negative values indicate anomalies.
    anomaly_scores = iso_forest.decision_function(X)
    
    # Translate anomaly score to a 0-100 Cancellation Probability
    # A highly negative score -> High probability of cancellation
    # We will invert and scale it. Min score ~ -0.3, Max score ~ 0.2
    
    # Invert scores so higher means more anomalous
    inverted_scores = -anomaly_scores
    
    # Normalize to 0-100 scale using empirical bounds
    min_score = np.min(inverted_scores)
    max_score = np.max(inverted_scores)
    
    # Handle edge case where all scores are identical
    if max_score == min_score:
        probs = np.zeros(len(inverted_scores))
    else:
        probs = ((inverted_scores - min_score) / (max_score - min_score)) * 100
        
    # Cap and floor
    probs = np.clip(probs, 0.0, 100.0)
    
    # Assign back to dataframe
    sensor_df["cancellation_probability"] = np.round(probs, 1)
    
    return sensor_df
