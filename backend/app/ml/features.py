import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from app.models.models import Route, Stop, Driver

class FeatureEngineer:
    """
    Constructs ML feature vectors for ETA prediction and route deviation prediction.
    Strictly enforces Temporal Leakage Rules (Information <= T only).
    """
    @staticmethod
    def extract_route_features(route: Route, driver: Driver, stops: List[Stop]) -> Dict[str, Any]:
        """Extracts features available at route dispatch time T_0."""
        stop_count = len(stops)
        planned_dist = route.planned_distance_km or 35.0
        planned_dur = route.planned_duration_min or 240.0
        
        avg_stop_dist = planned_dist / max(1, stop_count)
        avg_stop_dur = planned_dur / max(1, stop_count)

        driver_adherence = driver.historical_adherence_rate if driver else 0.9
        driver_avg_delay = driver.historical_avg_delay_min if driver else 5.0

        # Time-window pressure calculation
        tw_pressures = []
        for s in stops:
            if s.time_window_start and s.time_window_end:
                window_mins = (s.time_window_end - s.time_window_start).total_seconds() / 60.0
                tw_pressures.append(max(0.0, 120.0 - window_mins))
        tw_pressure_avg = float(np.mean(tw_pressures)) if tw_pressures else 0.0

        return {
            "stop_count": float(stop_count),
            "planned_distance_km": float(planned_dist),
            "planned_duration_min": float(planned_dur),
            "avg_stop_distance_km": float(avg_stop_dist),
            "avg_stop_duration_min": float(avg_stop_dur),
            "driver_adherence_rate": float(driver_adherence),
            "driver_historical_delay_min": float(driver_avg_delay),
            "time_window_pressure": float(tw_pressure_avg),
            "route_complexity_score": float(round((stop_count * 0.5) + (planned_dist * 0.3) + (tw_pressure_avg * 0.2), 2))
        }

    @staticmethod
    def extract_stop_features(stop: Stop, route_features: Dict[str, Any], current_sequence: int) -> Dict[str, Any]:
        """Extracts stop-level features for ETA prediction at sequence position k <= current_sequence."""
        remaining_stops = max(0, int(route_features["stop_count"]) - current_sequence)
        pct_completed = float(current_sequence) / max(1.0, route_features["stop_count"])

        return {
            **route_features,
            "stop_sequence": float(current_sequence),
            "remaining_stops": float(remaining_stops),
            "route_completion_pct": float(pct_completed),
            "service_time_min": float(stop.service_time_min or 5.0),
            "cumulative_distance_est_km": float(route_features["avg_stop_distance_km"] * current_sequence)
        }
