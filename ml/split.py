"""
MineGuard AI — Train / Validation / Test Splitting Module
"""

import pandas as pd
import numpy as np
from ml.config import TARGET_COL, RANDOM_SEED
from ml.utils import logger


def split_data(
    df: pd.DataFrame,
    target_col: str = TARGET_COL,
    strategy: str = "time_aware",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = RANDOM_SEED
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, dict]:
    """
    Split dataset into training, validation, and testing sets.
    
    Prefers time-aware chronological splitting to prevent temporal look-ahead leakage.
    
    Returns:
        tuple: (X_train, y_train, X_val, y_val, X_test, y_test, split_stats_dict)
    """
    logger.info("Splitting dataset using strategy: '%s' (Ratios: %.0f%% train / %.0f%% val / %.0f%% test)...",
                strategy, train_ratio * 100, val_ratio * 100, test_ratio * 100)
                
    df_sorted = df.copy()
    
    if strategy == "time_aware" and "event_date" in df_sorted.columns:
        df_sorted["parsed_date"] = pd.to_datetime(df_sorted["event_date"], errors="coerce")
        df_sorted = df_sorted.sort_values(by="parsed_date").reset_index(drop=True)
        df_sorted = df_sorted.drop(columns=["parsed_date"])
    else:
        # Fallback to reproducible random seed
        df_sorted = df_sorted.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
        
    n_total = len(df_sorted)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)
    
    train_df = df_sorted.iloc[:n_train].copy()
    val_df = df_sorted.iloc[n_train:n_train + n_val].copy()
    test_df = df_sorted.iloc[n_train + n_val:].copy()
    
    y_train = train_df[target_col]
    X_train = train_df.drop(columns=[target_col])
    
    y_val = val_df[target_col]
    X_val = val_df.drop(columns=[target_col])
    
    y_test = test_df[target_col]
    X_test = test_df.drop(columns=[target_col])
    
    split_stats = {
        "strategy": strategy,
        "total_samples": n_total,
        "train": {
            "samples": len(train_df),
            "ratio": len(train_df) / n_total,
            "positive_count": int(y_train.sum()),
            "negative_count": int((y_train == 0).sum()),
            "positive_ratio": float(y_train.mean())
        },
        "validation": {
            "samples": len(val_df),
            "ratio": len(val_df) / n_total,
            "positive_count": int(y_val.sum()),
            "negative_count": int((y_val == 0).sum()),
            "positive_ratio": float(y_val.mean())
        },
        "test": {
            "samples": len(test_df),
            "ratio": len(test_df) / n_total,
            "positive_count": int(y_test.sum()),
            "negative_count": int((y_test == 0).sum()),
            "positive_ratio": float(y_test.mean())
        }
    }
    
    logger.info("Split complete. Train: %d (Pos: %d), Val: %d (Pos: %d), Test: %d (Pos: %d)",
                len(X_train), y_train.sum(), len(X_val), y_val.sum(), len(X_test), y_test.sum())
                
    return X_train, y_train, X_val, y_val, X_test, y_test, split_stats


if __name__ == "__main__":
    from ml.data_loader import load_raw_dataset
    from ml.target_builder import build_target
    raw = load_raw_dataset()
    df_t, _ = build_target(raw)
    X_tr, y_tr, X_v, y_v, X_te, y_te, stats = split_data(df_t)
    print("Split Stats:", stats)
