import hashlib
import pandas as pd
from typing import Dict, Any, List
from app.schemas.schemas import DataQualityReportSchema

class DataValidator:
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calculates SHA256 hash of a dataset file for provenance tracking."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def validate_dataset(df: pd.DataFrame, dataset_name: str, file_path: str) -> DataQualityReportSchema:
        """Validates raw Pandas dataframe against logistics domain data rules."""
        issues: List[str] = []
        total_rows = len(df)
        
        # Calculate missing values
        missing_values: Dict[str, int] = df.isnull().sum().to_dict()
        
        # Duplicate records
        duplicate_records = int(df.duplicated().sum())
        if duplicate_records > 0:
            issues.append(f"Found {duplicate_records} duplicate records in dataset.")
            
        # Count invalid durations if column present
        invalid_durations = 0
        duration_cols = [c for c in df.columns if 'duration' in c.lower() or 'time' in c.lower()]
        for col in duration_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                invalid = int((df[col] < 0).sum())
                invalid_durations += invalid
        if invalid_durations > 0:
            issues.append(f"Found {invalid_durations} invalid (negative) duration values.")

        # Count invalid distances if column present
        invalid_distances = 0
        distance_cols = [c for c in df.columns if 'distance' in c.lower() or 'km' in c.lower()]
        for col in distance_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                invalid = int((df[col] < 0).sum())
                invalid_distances += invalid
        if invalid_distances > 0:
            issues.append(f"Found {invalid_distances} invalid (negative) distance values.")

        # Count invalid coordinates if column present
        invalid_coordinates = 0
        if 'lat' in df.columns and 'lng' in df.columns:
            invalid_lat = (df['lat'] < -90) | (df['lat'] > 90)
            invalid_lng = (df['lng'] < -180) | (df['lng'] > 180)
            invalid_coordinates = int((invalid_lat | invalid_lng).sum())
            if invalid_coordinates > 0:
                issues.append(f"Found {invalid_coordinates} invalid lat/lng coordinates out of range.")

        # Route, stop, driver counts
        route_col = [c for c in df.columns if 'route' in c.lower()]
        route_count = int(df[route_col[0]].nunique()) if route_col else total_rows
        
        stop_col = [c for c in df.columns if 'stop' in c.lower()]
        stop_count = int(df[stop_col[0]].nunique()) if stop_col else total_rows
        
        driver_col = [c for c in df.columns if 'driver' in c.lower()]
        driver_count = int(df[driver_col[0]].nunique()) if driver_col else 0

        # Status determination
        validation_status = "SUCCESS"
        if len(issues) > 0:
            validation_status = "WARNING" if len(issues) < 3 else "CRITICAL"

        file_hash = DataValidator.calculate_file_hash(file_path) if file_path and pd.io.common.file_exists(file_path) else "N/A"

        return DataQualityReportSchema(
            dataset_name=dataset_name,
            total_rows=total_rows,
            route_count=route_count,
            stop_count=stop_count,
            driver_count=driver_count,
            missing_values=missing_values,
            duplicate_records=duplicate_records,
            invalid_durations=invalid_durations,
            invalid_distances=invalid_distances,
            invalid_coordinates=invalid_coordinates,
            validation_status=validation_status,
            issues=issues,
            provenance_hash=file_hash
        )
