"""
MineGuard AI — Data Leakage Prevention Module
"""

import pandas as pd
from ml.utils import logger

# Outcome/Post-event fields that MUST be dropped to prevent data leakage
LEAKY_COLUMNS = [
    "fatality_count",
    "injury_count",
    "event_description",
    "notes",
    "photo_link",
    "source_link",
    "created_date",
    "last_edited_date",
    "submitted_date",
    "event_import_id",
    "event_import_source",
    "event_title",
    "location_description",
    "gazeteer_closest_point",
    "gazeteer_distance",
    "admin_division_population"
]


def prevent_leakage(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove outcome/post-event fields from feature set to eliminate data leakage.
    
    Args:
        df (pd.DataFrame): Dataframe containing features and target.
        
    Returns:
        pd.DataFrame: Cleaned dataframe free of post-event leakage fields.
    """
    logger.info("Enforcing data leakage prevention checks...")
    df_clean = df.copy()
    
    dropped_cols = []
    for col in LEAKY_COLUMNS:
        if col in df_clean.columns:
            df_clean = df_clean.drop(columns=[col])
            dropped_cols.append(col)
            
    logger.info("Dropped %d potentially leaky post-event outcome columns: %s", 
                len(dropped_cols), dropped_cols)
                
    return df_clean


def check_for_leakage(X_train: pd.DataFrame, X_val: pd.DataFrame, X_test: pd.DataFrame) -> bool:
    """
    Verify that feature columns contain no post-event leakage indicators.
    
    Returns:
        bool: True if no leaky columns present, False otherwise.
    """
    all_cols = list(X_train.columns) + list(X_val.columns) + list(X_test.columns)
    leaky_found = set(all_cols).intersection(set(LEAKY_COLUMNS))
    
    if leaky_found:
        logger.error("LEAKAGE ALERT: Leaky columns detected in feature matrix: %s", leaky_found)
        return False
        
    logger.info("Leakage check PASSED. No post-event outcome fields present in feature matrix.")
    return True
