"""
MineGuard AI — Data Validation Module
"""

import pandas as pd
import numpy as np
from ml.utils import logger, save_json
from ml.config import VALIDATED_DATA_FILE


def validate_dataset(df: pd.DataFrame) -> tuple[bool, dict]:
    """
    Perform rigorous validation checks on input dataset.
    
    Args:
        df (pd.DataFrame): Dataframe to validate.
        
    Returns:
        tuple[bool, dict]: (is_valid, validation_report_dict)
    """
    logger.info("Starting dataset validation...")
    report = {
        "passed": True,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "errors": [],
        "warnings": [],
        "checks": {}
    }
    
    # 1. Required Columns Check
    required_cols = ["event_id", "event_date", "latitude", "longitude", "landslide_category"]
    missing_req = [col for col in required_cols if col not in df.columns]
    if missing_req:
        err = f"Missing required columns: {missing_req}"
        report["errors"].append(err)
        report["passed"] = False
        report["checks"]["required_columns"] = False
    else:
        report["checks"]["required_columns"] = True
        
    # 2. Duplicate Rows Check
    dup_count = df.duplicated().sum()
    report["checks"]["duplicate_rows_count"] = int(dup_count)
    if dup_count > 0:
        report["warnings"].append(f"Found {dup_count} exact duplicate rows.")
        
    # 3. Coordinate Bounds Validation (WGS84)
    if "latitude" in df.columns and "longitude" in df.columns:
        invalid_lat = df[(df["latitude"] < -90.0) | (df["latitude"] > 90.0)]
        invalid_lon = df[(df["longitude"] < -180.0) | (df["longitude"] > 180.0)]
        
        lat_err_cnt = len(invalid_lat)
        lon_err_cnt = len(invalid_lon)
        
        report["checks"]["invalid_latitude_count"] = lat_err_cnt
        report["checks"]["invalid_longitude_count"] = lon_err_cnt
        
        if lat_err_cnt > 0 or lon_err_cnt > 0:
            err = f"Invalid coordinates detected: {lat_err_cnt} invalid latitudes, {lon_err_cnt} invalid longitudes."
            report["errors"].append(err)
            report["passed"] = False
            
    # 4. Timestamp Parsability Check
    if "event_date" in df.columns:
        parsed_dates = pd.to_datetime(df["event_date"], errors="coerce")
        null_dates = parsed_dates.isna().sum()
        report["checks"]["unparseable_dates_count"] = int(null_dates)
        if null_dates > 0:
            report["errors"].append(f"Found {null_dates} unparseable timestamps in event_date.")
            report["passed"] = False
            
    # 5. Target Label Validity Check
    if "landslide_category" in df.columns:
        known_categories = [
            "rock_fall", "landslide", "mudslide", "complex",
            "debris_flow", "other", "unknown", "riverbank_collapse",
            "snow_avalanche", "translational_slide"
        ]
        unrecognized = df[~df["landslide_category"].fillna("unknown").isin(known_categories)]
        if len(unrecognized) > 0:
            report["warnings"].append(f"Found {len(unrecognized)} unrecognized category values.")
            
    # 6. Physical Numerical Boundaries Validation (Rainfall & Displacement)
    if "rainfall_mm" in df.columns:
        neg_rain = (df["rainfall_mm"] < 0.0).sum()
        if neg_rain > 0:
            report["errors"].append(f"Found {neg_rain} negative rainfall values.")
            report["passed"] = False
            
    if "displacement_mm" in df.columns:
        neg_disp = (df["displacement_mm"] < 0.0).sum()
        if neg_disp > 0:
            report["errors"].append(f"Found {neg_disp} negative displacement values.")
            report["passed"] = False
            
    # 7. Summary Missing Values Report
    missing_summary = df.isna().sum().to_dict()
    report["missing_values_per_column"] = {k: int(v) for k, v in missing_summary.items()}
    
    logger.info("Validation complete. Status: %s. Errors: %d, Warnings: %d", 
                "PASSED" if report["passed"] else "FAILED", 
                len(report["errors"]), len(report["warnings"]))
                
    return report["passed"], report


if __name__ == "__main__":
    from ml.data_loader import load_raw_dataset
    raw_df = load_raw_dataset()
    is_valid, rep = validate_dataset(raw_df)
    print("Is Valid:", is_valid)
    print("Report Summary:", rep["checks"])
