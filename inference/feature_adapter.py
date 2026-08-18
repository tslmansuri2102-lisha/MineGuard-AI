"""
MineGuard AI — Real-Time Telemetry Feature Adapter
"""

import pandas as pd
from datetime import datetime, timezone
from ml.utils import logger


class FeatureAdapter:
    """
    Adapts canonical real-time telemetry payloads into the exact 16-feature dataframe
    expected by the Phase 2 Random Forest ML model artifact.
    """
    def adapt_telemetry_to_ml_features(self, telemetry: dict, rolling_features: dict = None) -> pd.DataFrame:
        """
        Map canonical telemetry + rolling window features to ML feature schema.
        
        Args:
            telemetry (dict): Canonical TelemetrySchema dictionary.
            rolling_features (dict, optional): Computed rolling window statistics.
            
        Returns:
            pd.DataFrame: Single-row dataframe ready for preprocessing pipeline.
        """
        rolling = rolling_features or {}
        
        # Parse timestamp
        dt = datetime.fromisoformat(telemetry["timestamp"].replace("Z", "+00:00"))
        
        # Map trigger category based on real-time drivers
        rain = telemetry.get("rainfall_mm", 0.0)
        vib = telemetry.get("vibration_g", 0.0)
        
        if rain > 50.0:
            trigger = "downpour"
        elif rain > 15.0:
            trigger = "rain"
        elif vib > 2.0:
            trigger = "mining"
        else:
            trigger = "unknown"
            
        disp = telemetry.get("displacement_mm", 0.0)
        size = "large" if disp > 50.0 else ("medium" if disp > 10.0 else "small")
        
            # Keep velocity in mm/s to match the real-time telemetry scale.
            # The training pipeline currently does not learn meaningful velocity
            # values, so avoid artificially multiplying the sensor value by 3600.
        velocity_mm_h = rolling.get(
            "displacement_change_rate",
            telemetry.get("slope_velocity_mm_s", 0.0)
        )
        accel_mm_h2 = rolling.get("vibration_acceleration", 0.0)
        
        feature_dict = {
            # 1. Spatial & Geomechanical Features (Real-Time Telemetry)
            "latitude": float(telemetry.get("latitude", 23.7954)),
            "longitude": float(telemetry.get("longitude", 86.4304)),
            
            # 2. Temporal Features (Derived from Telemetry Timestamp)
            "year": int(dt.year),
            "month": int(dt.month),
            "day_of_year": int(dt.timetuple().tm_yday),
            
            # 3. Meteorological Features (Real-Time + Rolling Window)
            "rainfall_mm": float(rain),
            "rainfall_3h_sum": float(rolling.get("rainfall_1h", telemetry.get("rainfall_1h", 0.0)) * 2.5),
            "rainfall_24h_sum": float(rolling.get("rainfall_6h", telemetry.get("rainfall_6h", 0.0)) * 3.0),
            
            # 4. GIS Terrain Features (Static Zone Metadata)
            "slope_deg": float(rolling.get("slope_deg", 38.0)),
            "elevation_m": float(rolling.get("elevation_m", 250.0)),
            
            # 5. Geomechanical Movement Derivatives (Derived Temporal Features)
            "displacement_velocity": float(velocity_mm_h),
            "displacement_acceleration": float(accel_mm_h2),
            
            # 6. Categorical Context Features
            "landslide_trigger": str(trigger),
            "landslide_size": str(size),
            "landslide_setting": "mine_slope",
            "country_code": "ind"
        }
        
        return pd.DataFrame([feature_dict])
