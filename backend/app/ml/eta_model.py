import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

class ETAPredictionModel:
    """
    Supervised Machine Learning model for predicting delivery delay (in minutes).
    Includes Baselines and Candidate Gradient Boosting Regressor.
    """
    def __init__(self):
        self.model_version = "v1.2.0"
        self.algorithm = "GradientBoostingRegressor"
        self.feature_names = [
            "stop_count", "planned_distance_km", "planned_duration_min",
            "avg_stop_distance_km", "avg_stop_duration_min", "driver_adherence_rate",
            "driver_historical_delay_min", "time_window_pressure", "route_complexity_score"
        ]

        # Initialize fit baseline models
        self.candidate_model = GradientBoostingRegressor(n_estimators=50, random_state=42)
        self.baseline_model = LinearRegression()

        # Seed with benchmark historical weights
        X_benchmark = np.array([
            [10, 30.0, 180.0, 3.0, 18.0, 0.95, 2.0, 10.0, 15.0],
            [15, 45.0, 270.0, 3.0, 18.0, 0.85, 8.0, 25.0, 26.0],
            [20, 60.0, 360.0, 3.0, 18.0, 0.90, 4.0, 15.0, 31.0],
            [8,  20.0, 120.0, 2.5, 15.0, 0.98, 1.0, 5.0,  11.0],
            [25, 75.0, 450.0, 3.0, 18.0, 0.80, 12.0, 40.0, 41.0]
        ])
        y_benchmark = np.array([5.2, 22.4, 11.0, 1.5, 38.0])

        self.candidate_model.fit(X_benchmark, y_benchmark)
        self.baseline_model.fit(X_benchmark, y_benchmark)

    def predict_delay(self, features: Dict[str, Any]) -> Tuple[float, float]:
        """
        Returns (predicted_delay_min, late_probability)
        """
        feature_vector = np.array([[features.get(k, 0.0) for k in self.feature_names]])
        
        pred_delay = float(self.candidate_model.predict(feature_vector)[0])
        pred_delay = max(0.0, round(pred_delay, 1))

        # Sigmoid map delay minutes to late delivery probability [0..1]
        late_prob = 1.0 / (1.0 + np.exp(-(pred_delay - 15.0) / 5.0))
        late_prob = float(round(late_prob, 3))

        return pred_delay, late_prob

    def evaluate_performance(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluates model using metrics specified in Section 36."""
        preds = self.candidate_model.predict(X_test)
        
        mae = float(mean_absolute_error(y_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        errors = np.abs(y_test - preds)
        median_ae = float(np.median(errors))
        p90_error = float(np.percentile(errors, 90))
        bias = float(np.mean(preds - y_test))

        return {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "median_ae": round(median_ae, 2),
            "p90_error": round(p90_error, 2),
            "bias": round(bias, 2)
        }
