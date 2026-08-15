"""
MineGuard AI — Model Loader Module
"""

import os
from typing import Optional, Tuple
from ml.config import PREPROCESSOR_FILE, MODEL_FILE
from ml.preprocessing import PipelinePreprocessor
from ml.baseline_model import BaselineModel
from ml.utils import logger


class ModelLoader:
    """
    Singleton-style loader for preprocessor and baseline ML model artifacts.
    """
    _instance = None
    _preprocessor = None
    _model = None

    @classmethod
    def load_artifacts(cls, preprocessor_path: str = PREPROCESSOR_FILE, model_path: str = MODEL_FILE) -> Tuple[Optional[PipelinePreprocessor], Optional[BaselineModel]]:
        """Load preprocessor and model artifacts safely."""
        if cls._preprocessor is not None and cls._model is not None:
            return cls._preprocessor, cls._model
            
        try:
            if not os.path.exists(preprocessor_path) or not os.path.exists(model_path):
                logger.warning("Model artifacts not found at %s or %s. Operating in fallback mode.", preprocessor_path, model_path)
                return None, None
                
            cls._preprocessor = PipelinePreprocessor.load(preprocessor_path)
            cls._model = BaselineModel.load(model_path)
            logger.info("Successfully loaded preprocessor and baseline model artifacts.")
            return cls._preprocessor, cls._model
        except Exception as e:
            logger.error("Failed to load ML artifacts: %s. Operating in fallback mode.", e)
            return None, None
