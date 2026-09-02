import os
import json
from google import genai
from google.genai import types
from django.conf import settings

GEMINI_RECOMMENDATION_API_KEY = getattr(settings, "GEMINI_RECOMMENDATION_API_KEY", getattr(settings, "GEMINI_API_KEY", ""))
GEMINI_MODEL = getattr(settings, "GEMINI_MODEL", "gemini-3.6-flash")

def generate_health_recommendation(battery, analysis, bms_metrics=None) -> dict:
    """
    Generate actionable battery health maintenance recommendations using Gemini.
    """
    if not GEMINI_RECOMMENDATION_API_KEY:
        return {
            "error": "AI recommendation is temporarily unavailable. (Missing API Key)"
        }
        
    try:
        client = genai.Client(api_key=GEMINI_RECOMMENDATION_API_KEY)
    except Exception as e:
        return {
            "error": "AI recommendation is temporarily unavailable."
        }

    # Prepare context data
    soh_val = analysis.soh if analysis and analysis.soh is not None else "Unknown"
    risk_level = analysis.safety_risk if analysis and analysis.safety_risk else "Unknown"
    
    cycle_count = bms_metrics.cycle_count if bms_metrics and bms_metrics.cycle_count is not None else "Unknown"
    avg_temp = bms_metrics.avg_temperature if bms_metrics and bms_metrics.avg_temperature is not None else "Unknown"
    avg_voltage = bms_metrics.avg_voltage if bms_metrics and bms_metrics.avg_voltage is not None else "Unknown"
    
    chemistry = battery.chemistry if battery.chemistry else "Unknown"
    capacity = float(battery.battery_capacity_kwh) if battery.battery_capacity_kwh else "Unknown"
    
    prompt = f"""
    You are a battery health advisory assistant. Your job is to provide practical, actionable maintenance measures for an EV battery owner based on the battery's current condition.

    Battery Information:
    - ID: {battery.battery_id}
    - Model: {battery.vehicle_model}
    - Chemistry: {chemistry}
    - Capacity: {capacity} kWh
    - State of Health (SoH): {soh_val}%
    - Safety Risk Level: {risk_level}
    - Cycle Count: {cycle_count}
    - Average Temperature: {avg_temp} C
    - Average Voltage: {avg_voltage} V

    Your task:
    1. Understand the current battery condition.
    2. Recommend 2 to 4 practical, actionable measures the owner can take to maintain or manage their battery.
    3. Briefly explain the reason for each action.
    
    Constraints:
    - Do NOT calculate SoH yourself. Use the provided SoH.
    - Do NOT invent battery measurements or faults.
    - Do NOT claim safety certification, regulatory compliance, or definitive safety/unsafety.
    - Do NOT provide "second-life" or "reuse" recommendations. This is only about maintaining the current battery.
    - Keep it concise, helpful, and professional.
    """

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "summary": {"type": "string"},
                        "recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string"},
                                    "reason": {"type": "string"}
                                },
                                "required": ["action", "reason"]
                            }
                        }
                    },
                    "required": ["title", "summary", "recommendations"]
                },
                temperature=0.2,
            ),
        )
        
        result_json = json.loads(response.text)
        return result_json
        
    except Exception as e:
        print(f"Error in Gemini GenAI: {e}")
        return {
            "error": f"AI recommendation is temporarily unavailable. Details: {str(e)}"
        }
