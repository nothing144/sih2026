import os

import pandas as pd
import joblib
from django.conf import settings


# Path to the trained SOH model.
# Deployment-safe: derived from BASE_DIR (works on any OS/host layout).
# The artifact must ship with the deployment (backend/ml_models/soh_model_original.pkl).
MODEL_PATH = os.path.join(
    settings.BASE_DIR,
    "ml_models",
    "soh_model_demo_trained.pkl"
)

# Lazy singleton: the model is loaded on first prediction instead of at
# import time, so a missing/corrupt artifact cannot crash the whole server
# during startup (migrations, collectstatic, health checks, etc.).
final_gb_model = None


def _get_model():
    global final_gb_model
    if final_gb_model is None:
        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(
                f"ML model artifact not found at {MODEL_PATH}. "
                "Include backend/ml_models/ in the deployment."
            )
        loaded = joblib.load(MODEL_PATH)
        if isinstance(loaded, dict) and 'model' in loaded:
            final_gb_model = loaded['model']
        else:
            final_gb_model = loaded
    return final_gb_model

def predict_battery_status(
    cycle,
    voltage_mean,
    current_mean,
    temperature_mean,
    voltage_load_mean,
    current_load_mean,
    discharge_duration
):

    features = pd.DataFrame([{
        "cycle": cycle,
        "voltage_mean": voltage_mean,
        "current_mean": current_mean,
        "temperature_mean": temperature_mean,
        "voltage_load_mean": voltage_load_mean,
        "current_load_mean": current_load_mean,
        "discharge_duration": discharge_duration
    }])

    soh_prediction = _get_model().predict(features)[0]

    soh_prediction = max(0, min(100, soh_prediction))

    threshold = getattr(settings, 'SECOND_LIFE_SOH_THRESHOLD', 80)
    
    if soh_prediction >= threshold:
        risk = "LOW"
    elif soh_prediction >= (threshold - 20):
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    if risk == "LOW":
        recommendation = (
            "Battery health is currently good. "
            "Follow manufacturer charging guidance, "
            "avoid prolonged extreme temperatures, "
            "and continue regular monitoring."
        )
    elif risk == "MEDIUM":
        recommendation = (
            "Battery shows moderate degradation. "
            "Follow manufacturer charging guidance, "
            "avoid prolonged high-temperature charging, "
            "and monitor battery health regularly."
        )
    else:
        recommendation = (
            "Battery shows significant degradation. "
            "Avoid stressing the battery, follow manufacturer "
            "safety guidance, and consider professional inspection "
            "or replacement."
        )

    if soh_prediction >= threshold:
        second_life = (
            "Potential candidate for second-life — "
            "certified testing required."
        )
    elif soh_prediction >= (threshold - 20):
        second_life = (
            "Possible second-life candidate — "
            "detailed diagnostic and certified testing required."
        )
    else:
        second_life = (
            "Not recommended for second-life based on estimated SOH — "
            "professional assessment required."
        )

    return {
        "cycle": cycle,
        "soh_prediction": float(round(soh_prediction, 2)),
        "risk": risk,
        "recommendation": recommendation,
        "second_life": second_life
    }


def get_degradation_factors():

    feature_names = [
        "cycle",
        "voltage_mean",
        "current_mean",
        "temperature_mean",
        "voltage_load_mean",
        "current_load_mean",
        "discharge_duration"
    ]

    importances = _get_model().feature_importances_

    factors = list(zip(feature_names, importances))
    factors.sort(key=lambda x: x[1], reverse=True)

    readable_names = {
        "cycle": "Cycle count",
        "voltage_mean": "Voltage characteristics",
        "current_mean": "Current behavior",
        "temperature_mean": "Temperature",
        "voltage_load_mean": "Voltage under load",
        "current_load_mean": "Current under load",
        "discharge_duration": "Discharge behavior"
    }

    degradation_factors = []

    for feature, importance in factors[:3]:

        percentage = importance * 100

        if percentage >= 30:
            impact = "High impact"
        elif percentage >= 15:
            impact = "Medium impact"
        else:
            impact = "Low impact"

        degradation_factors.append({
            "factor": readable_names[feature],
            "impact": impact,
            "importance": float(round(percentage, 2))
        })

    return degradation_factors


def complete_battery_assessment(
    cycle,
    voltage_mean,
    current_mean,
    temperature_mean,
    voltage_load_mean,
    current_load_mean,
    discharge_duration
):

    result = predict_battery_status(
        cycle,
        voltage_mean,
        current_mean,
        temperature_mean,
        voltage_load_mean,
        current_load_mean,
        discharge_duration
    )

    degradation_factors = get_degradation_factors()

    result["degradation_factors"] = degradation_factors

    return result
