"""
Telemetry extraction for uploaded BMS CSV files.

The ML pipeline consumes 7 aggregated columns per cycle row:
    cycle, voltage_mean, current_mean, temperature_mean,
    voltage_load_mean, current_load_mean, discharge_duration

This module derives human-readable summary metrics from those same
rows so the dashboard can display real telemetry (charge cycles,
temperature/voltage stats, discharge totals) instead of placeholders.
"""

import pandas as pd


REQUIRED_COLUMNS = [
    "cycle",
    "voltage_mean",
    "current_mean",
    "temperature_mean",
    "voltage_load_mean",
    "current_load_mean",
    "discharge_duration",
]


def compute_bms_metrics(file) -> dict:
    """
    Read a BMS CSV (Django FieldFile) and return telemetry aggregates.

    Returns a dict with None values for anything that cannot be derived,
    so callers can always persist a metrics row safely.
    """
    empty = {
        "row_count": None,
        "cycle_count": None,
        "avg_temperature": None,
        "min_temperature": None,
        "max_temperature": None,
        "avg_voltage": None,
        "min_voltage": None,
        "max_voltage": None,
        "avg_current": None,
        "total_discharge_duration": None,
    }

    try:
        file.seek(0)
        df = pd.read_csv(file)
        file.seek(0)
    except Exception:
        return empty

    if df.empty:
        return empty

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return empty

    def num(series):
        s = pd.to_numeric(series, errors="coerce").dropna()
        return s

    voltage = num(df["voltage_mean"])
    temperature = num(df["temperature_mean"])
    current = num(df["current_mean"])
    duration = num(df["discharge_duration"])
    cycles = num(df["cycle"])

    return {
        "row_count": int(len(df)),
        "cycle_count": int(cycles.max()) if not cycles.empty else None,
        "avg_temperature": round(float(temperature.mean()), 2) if not temperature.empty else None,
        "min_temperature": round(float(temperature.min()), 2) if not temperature.empty else None,
        "max_temperature": round(float(temperature.max()), 2) if not temperature.empty else None,
        "avg_voltage": round(float(voltage.mean()), 2) if not voltage.empty else None,
        "min_voltage": round(float(voltage.min()), 2) if not voltage.empty else None,
        "max_voltage": round(float(voltage.max()), 2) if not voltage.empty else None,
        "avg_current": round(float(current.mean()), 2) if not current.empty else None,
        "total_discharge_duration": round(float(duration.sum()), 2) if not duration.empty else None,
    }
