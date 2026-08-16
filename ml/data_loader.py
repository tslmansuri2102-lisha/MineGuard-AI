"""
MineGuard AI — Data Loader Module
"""

import os
import pandas as pd
from ml.config import RAW_DATA_FILE
from ml.utils import logger


def load_raw_dataset(filepath: str = None) -> pd.DataFrame:
    """
    Load raw Phase 1 dataset from data/raw/ directory.
    
    Args:
        filepath (str, optional): Custom path to raw dataset. Defaults to RAW_DATA_FILE.
        
    Returns:
        pd.DataFrame: Copy of raw dataset.
    """
    target_path = filepath or RAW_DATA_FILE
    
    if not os.path.isabs(target_path):
        target_path = os.path.abspath(target_path)
        
    if not os.path.exists(target_path):
        raise FileNotFoundError(
            f"Raw dataset file not found at: '{target_path}'. "
            "Please ensure Phase 1 data acquisition step has run successfully."
        )
        
    logger.info("Loading raw dataset from: %s", target_path)
    df = pd.read_csv(target_path, encoding="utf-8", low_memory=False)
    
    logger.info("Successfully loaded dataset with shape %s (%d rows, %d columns)", 
                df.shape, len(df), len(df.columns))
    logger.debug("Columns: %s", list(df.columns))
    
    # Return a copy to ensure raw data in memory is preserved
    return df.copy()


if __name__ == "__main__":
    df_raw = load_raw_dataset()
    print("Loaded dataset shape:", df_raw.shape)
