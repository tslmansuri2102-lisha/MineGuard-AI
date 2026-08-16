"""
MineGuard AI — Sensor Reading Validation
Validates generated readings against API_CONTRACT.md specifications and physical constraints.
"""

from datetime import datetime
import math
import re
from typing import Any, Dict, List, Tuple


REQUIRED_TOP_LEVEL_FIELDS = ("mine_id", "zone_id", "sensor_id", "timestamp", "sensors")

REQUIRED_SENSOR_FIELDS = (
    "displacement_mm",
    "strain",
    "pore_pressure_kpa",
    "rainfall_mm",
    "temperature_c",
    "vibration_g",
)

NON_NEGATIVE_SENSOR_FIELDS = (
    "displacement_mm",
    "strain",
    "pore_pressure_kpa",
    "rainfall_mm",
    "vibration_g",
)


class ValidationError(ValueError):
    """Raised when a sensor reading fails contract schema or physics validation."""
    pass


def parse_iso8601_utc(timestamp_str: str) -> datetime:
    """
    Parses an ISO 8601 timestamp string and verifies that it is UTC.
    Accepts standard 'Z' suffix (e.g., '2026-08-14T10:30:00Z') or '+00:00'.
    Raises ValidationError if invalid.
    """
    if not isinstance(timestamp_str, str):
        raise ValidationError(f"timestamp must be a string, got {type(timestamp_str).__name__}")
    
    # Check ISO-8601 format
    # Replace trailing 'Z' with '+00:00' for standard fromisoformat parsing
    normalized = timestamp_str.strip()
    if normalized.endswith("Z"):
        iso_parsed = normalized[:-1] + "+00:00"
    else:
        iso_parsed = normalized

    try:
        dt = datetime.fromisoformat(iso_parsed)
    except Exception as e:
        raise ValidationError(f"Invalid ISO 8601 timestamp '{timestamp_str}': {e}") from e

    if dt.tzinfo is None:
        raise ValidationError(f"Timestamp '{timestamp_str}' must include timezone offset or 'Z' (UTC).")
    
    # Check that offset is UTC (0 seconds)
    if dt.utcoffset().total_seconds() != 0:
        raise ValidationError(f"Timestamp '{timestamp_str}' must be in UTC timezone (offset +00:00 or 'Z').")

    return dt


def validate_reading(data: Dict[str, Any]) -> None:
    """
    Validates a complete sensor reading dictionary according to API_CONTRACT.md.
    
    Raises:
        ValidationError: If any contract, typing, or physics rule is violated.
    """
    if not isinstance(data, dict):
        raise ValidationError(f"Reading must be a dictionary, got {type(data).__name__}")

    # 1. Top level required fields check
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in data:
            raise ValidationError(f"Missing required top-level field: '{field}'")

    # 2. Identifiers check
    for id_field in ("mine_id", "zone_id", "sensor_id"):
        val = data[id_field]
        if not isinstance(val, str) or not val.strip():
            raise ValidationError(f"Field '{id_field}' must be a non-empty string, got {repr(val)}")

    # 3. Timestamp check
    parse_iso8601_utc(data["timestamp"])

    # 4. Sensors sub-dictionary check
    sensors = data["sensors"]
    if not isinstance(sensors, dict):
        raise ValidationError(f"'sensors' must be a dictionary, got {type(sensors).__name__}")

    for field in REQUIRED_SENSOR_FIELDS:
        if field not in sensors:
            raise ValidationError(f"Missing required sensor field: '{field}'")
        
        val = sensors[field]
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            raise ValidationError(
                f"Sensor field '{field}' must be numeric (float/int), got {type(val).__name__} ({repr(val)})"
            )
        
        if not math.isfinite(val):
            raise ValidationError(
                f"Sensor field '{field}' must be a finite number, got {val}"
            )
        
        if field in NON_NEGATIVE_SENSOR_FIELDS and val < 0:
            raise ValidationError(
                f"Sensor field '{field}' cannot be negative (got {val})"
            )

    # Check for unexpected extra keys in sensors to guarantee contract precision
    extra_keys = set(sensors.keys()) - set(REQUIRED_SENSOR_FIELDS)
    if extra_keys:
        raise ValidationError(f"Unexpected extra fields in 'sensors': {', '.join(sorted(extra_keys))}")


def is_valid_reading(data: Dict[str, Any]) -> bool:
    """
    Helper function returning True if reading is valid, False otherwise.
    """
    try:
        validate_reading(data)
        return True
    except (ValidationError, Exception):
        return False
