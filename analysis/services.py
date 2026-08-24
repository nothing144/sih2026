import pandas as pd

from .battery_assessment import complete_battery_assessment


REQUIRED_COLUMNS = [
    "cycle",
    "voltage_mean",
    "current_mean",
    "temperature_mean",
    "voltage_load_mean",
    "current_load_mean",
    "discharge_duration",
]

# Columns surfaced as "Latest BMS Reading" by the status endpoint.
# Values come straight from the stored CSV file — nothing is generated.
TELEMETRY_COLUMNS = [
    "cycle",
    "voltage_mean",
    "current_mean",
    "temperature_mean",
]


def extract_latest_telemetry(bms_file):
    """
    Read a stored BMS CSV file and return the latest row's real readings.

    Returns a dict of the telemetry columns present in the file
    (missing columns are omitted), or None when no usable data exists.
    This is the same "latest row" logic used by the ML assessment — it is
    data as of the upload, NOT real-time telemetry.
    """

    df = pd.read_csv(bms_file)

    available = [column for column in TELEMETRY_COLUMNS if column in df.columns]

    if not available:
        return None

    df = df[available].dropna()

    if df.empty:
        return None

    latest = df.iloc[-1]

    return {
        column: float(latest[column])
        for column in available
    }


def run_battery_analysis(bms_file):
    """
    Read an uploaded BMS CSV file and run the ML assessment.

    Returns the assessment result for the latest BMS record.
    """

    # Read uploaded CSV
    df = pd.read_csv(bms_file)

    # Check required columns
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required BMS columns: {', '.join(missing_columns)}"
        )

    # Remove rows with missing required values
    df = df[REQUIRED_COLUMNS].dropna()

    if df.empty:
        raise ValueError(
            "BMS file contains no valid data."
        )

    # Use the latest row from the uploaded BMS data
    latest = df.iloc[-1]

    # Convert values to normal Python numbers
    result = complete_battery_assessment(
        cycle=float(latest["cycle"]),
        voltage_mean=float(latest["voltage_mean"]),
        current_mean=float(latest["current_mean"]),
        temperature_mean=float(latest["temperature_mean"]),
        voltage_load_mean=float(latest["voltage_load_mean"]),
        current_load_mean=float(latest["current_load_mean"]),
        discharge_duration=float(latest["discharge_duration"]),
    )

    return result