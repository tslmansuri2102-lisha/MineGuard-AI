"""
MineGuard AI — Target Construction Module
"""

import pandas as pd
from ml.config import TARGET_COL, POSITIVE_CLASS_VALUE
from ml.utils import logger


def build_target(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Construct a scientifically valid binary target from Phase 1 ground truth data.
    
    Positive Class (1): Verified Rockfall events ('rock_fall')
    Negative Class (0): Other slope failure events ('landslide', 'mudslide', 'debris_flow', 'complex')
    Excluded: Non-slope failures / Unknown categories ('snow_avalanche', 'unknown', NaN)
    
    Returns:
        tuple[pd.DataFrame, dict]: (DataFrame with target_rockfall column, target_distribution_stats)
    """
    logger.info("Constructing binary ML target column '%s'...", TARGET_COL)
    df_clean = df.copy()
    
    # Standardize category strings
    cat_series = df_clean["landslide_category"].astype(str).str.strip().str.lower()
    
    # Exclude non-slope failure or unknown records
    excluded_mask = cat_series.isin(["snow_avalanche", "unknown", "nan", "other"])
    df_valid = df_clean[~excluded_mask].copy()
    cat_valid = cat_series[~excluded_mask]
    
    # Assign binary target: 1 for rock_fall, 0 for all other slope failures
    df_valid[TARGET_COL] = (cat_valid == POSITIVE_CLASS_VALUE).astype(int)
    
    pos_count = (df_valid[TARGET_COL] == 1).sum()
    neg_count = (df_valid[TARGET_COL] == 0).sum()
    total_count = len(df_valid)
    pos_ratio = (pos_count / total_count) if total_count > 0 else 0.0
    
    target_stats = {
        "target_column": TARGET_COL,
        "positive_class": "1 (Rockfall Event)",
        "negative_class": "0 (Non-Rockfall Slope Failure)",
        "total_samples": total_count,
        "positive_samples": int(pos_count),
        "negative_samples": int(neg_count),
        "positive_ratio": float(pos_ratio),
        "excluded_samples": int(len(df) - total_count),
        "class_imbalance_ratio": float(neg_count / pos_count) if pos_count > 0 else 0.0
    }
    
    logger.info("Target constructed successfully. Total: %d | Positive (Rockfall): %d (%.2f%%) | Negative: %d (%.2f%%)",
                total_count, pos_count, pos_ratio * 100, neg_count, (1 - pos_ratio) * 100)
                
    return df_valid, target_stats


if __name__ == "__main__":
    from ml.data_loader import load_raw_dataset
    raw = load_raw_dataset()
    df_t, stats = build_target(raw)
    print("Target Stats:", stats)
