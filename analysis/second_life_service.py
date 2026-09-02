import os
import json
from google import genai
from google.genai import types
from django.conf import settings

# Load configuration from settings
GEMINI_API_KEY = getattr(settings, "GEMINI_API_KEY", "")
GEMINI_MODEL = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")

def generate_reuse_recommendation(battery, bms_metrics=None, analysis=None) -> dict:
    """
    Generate a structured second-life recommendation using the official google-genai SDK.
    """
    threshold = getattr(settings, "SECOND_LIFE_SOH_THRESHOLD", 80)
    soh_val = analysis.soh if analysis and analysis.soh is not None else None
    
    # Healthy battery check (or missing SoH)
    if soh_val is None or soh_val > threshold:
        return {
            "status": "EV_CONTINUE",
            "eligible_for_reuse_recommendation": False,
            "soh": soh_val,
            "message": "Your battery is currently in good health and remains suitable for its primary EV application.",
            "recommendations": []
        }

    if not GEMINI_API_KEY:
        return {
            "error": "Second-life recommendation service is temporarily unavailable. (Missing API Key)"
        }
        
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        return {
            "error": "Second-life recommendation service is temporarily unavailable."
        }

    # Prepare context data
    cycle_count = bms_metrics.cycle_count if bms_metrics and bms_metrics.cycle_count is not None else "Unknown"
    avg_temp = bms_metrics.avg_temperature if bms_metrics and bms_metrics.avg_temperature is not None else "Unknown"
    avg_voltage = bms_metrics.avg_voltage if bms_metrics and bms_metrics.avg_voltage is not None else "Unknown"
    
    chemistry = battery.chemistry if battery.chemistry else "Unknown"
    capacity = float(battery.battery_capacity_kwh) if battery.battery_capacity_kwh else "Unknown"

    prompt = f"""
    You are providing a second-life application assessment for a previously used EV battery.
    
    Your job is NOT to certify the battery as safe.
    Do NOT claim that the battery is definitely safe for home or grid use.
    
    Use the supplied battery health information to suggest potentially suitable lower-demand second-life applications.
    
    Battery Information:
    - ID: {battery.battery_id}
    - Model: {battery.vehicle_model}
    - Chemistry: {chemistry}
    - Capacity: {capacity} kWh
    - SoH: {soh_val}%
    - Cycle Count: {cycle_count}
    - Average Temperature: {avg_temp} C
    - Average Voltage: {avg_voltage} V

    Possible application categories include:
    1. Solar Energy Storage
    2. Home Backup Power
    3. Stationary Energy Storage
    4. Energy Load Shifting
    5. Other suitable lower-demand applications
    6. Recycling / material recovery when reuse is not appropriate

    Explain WHY each recommendation may be suitable.
    If the available battery data is insufficient, explicitly say that the recommendation is limited by missing information.
    Do not invent battery measurements.
    Do not invent safety certifications.
    Do not invent manufacturer specifications.
    Do not claim regulatory compliance.
    Treat the recommendation as an informational second-life suggestion, not an engineering safety certification.
    """

    # Enforce structured output via Pydantic schema in the Gemini API
    # google-genai supports response_schema directly
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "battery_id": {"type": "string"},
                        "soh": {"type": "number"},
                        "overall_assessment": {"type": "string"},
                        "recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "application": {"type": "string"},
                                    "suitability": {"type": "string"},
                                    "reason": {"type": "string"},
                                    "how_it_can_be_used": {"type": "string"}
                                },
                                "required": ["application", "suitability", "reason", "how_it_can_be_used"]
                            }
                        },
                        "limitations": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "safety_note": {"type": "string"}
                    },
                    "required": ["battery_id", "soh", "overall_assessment", "recommendations", "limitations", "safety_note"]
                },
                temperature=0.2,
            ),
        )
        
        result_json = json.loads(response.text)
        result_json["status"] = "SECOND_LIFE_ELIGIBLE"
        result_json["eligible_for_reuse_recommendation"] = True
        return result_json
        
    except Exception as e:
        # Avoid leaking stack trace
        print(f"Error in Gemini GenAI: {e}")
        return {
            "error": f"Second-life recommendation service is temporarily unavailable. Details: {str(e)}"
        }

def generate_readiness_assessment(battery, bms_metrics=None, analysis=None) -> dict:
    """
    Generate a structured second-life readiness score using Gemini.
    """
    threshold = getattr(settings, "SECOND_LIFE_SOH_THRESHOLD", 80)
    
    if not analysis or analysis.soh is None:
        return {
            "error": "Battery health assessment is required to determine second-life readiness."
        }
        
    soh_val = analysis.soh
    
    if soh_val > threshold:
        return {
             "status": "EV_CONTINUE",
             "eligible_for_second_life": False,
             "soh": soh_val,
             "readiness_score": None,
             "readiness_level": None,
             "summary": "This battery remains suitable for its primary EV application.",
             "applications": [],
             "message": "Second-life readiness is not currently applicable."
        }

    if not GEMINI_API_KEY:
        return {
            "error": "Second-life readiness assessment is temporarily unavailable. (Missing API Key)"
        }
        
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        return {
            "error": "Second-life readiness assessment is temporarily unavailable."
        }

    cycle_count = bms_metrics.cycle_count if bms_metrics and bms_metrics.cycle_count is not None else "Unknown"
    avg_temp = bms_metrics.avg_temperature if bms_metrics and bms_metrics.avg_temperature is not None else "Unknown"
    avg_voltage = bms_metrics.avg_voltage if bms_metrics and bms_metrics.avg_voltage is not None else "Unknown"
    
    chemistry = battery.chemistry if battery.chemistry else "Unknown"
    
    prompt = f"""
    You are assessing the potential second-life readiness of a previously used EV battery.
    
    The battery has already reached the configured second-life eligibility threshold based on the existing battery health assessment.
    
    Use the supplied battery health and BMS information to provide an informational assessment of its potential for lower-demand second-life applications.
    
    Do NOT calculate or replace the existing SoH.
    Do NOT claim that the battery is safe for deployment.
    Do NOT provide safety certification.
    Do NOT invent measurements.
    Do NOT invent manufacturer specifications.
    Do NOT claim regulatory compliance.
    
    Consider:
    - SoH: {soh_val}%
    - Cycle Count: {cycle_count}
    - Average Voltage: {avg_voltage} V
    - Average Temperature: {avg_temp} C
    - Chemistry: {chemistry}
    
    Generate:
    1. A readiness score from 0 to 100.
    2. A readiness level.
    3. A short explanation.
    4. The main factors supporting the assessment.
    5. Potential second-life applications.
    6. Limitations and required further assessment.
    
    The score represents potential second-life suitability/readiness, NOT safety.
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
                        "readiness_score": {"type": "integer", "description": "Score from 0 to 100"},
                        "readiness_level": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                        "summary": {"type": "string"},
                        "factors": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "applications": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "application": {"type": "string"},
                                    "suitability": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                                    "how_it_can_be_used": {"type": "string"}
                                },
                                "required": ["application", "suitability", "how_it_can_be_used"]
                            }
                        },
                        "limitations": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "safety_note": {"type": "string"}
                    },
                    "required": ["readiness_score", "readiness_level", "summary", "factors", "applications", "limitations", "safety_note"]
                },
                temperature=0.2,
            ),
        )
        
        result_json = json.loads(response.text)
        
        # Validation
        score = result_json.get("readiness_score", 0)
        if not (0 <= score <= 100):
            result_json["readiness_score"] = max(0, min(100, score))
            
        level = result_json.get("readiness_level")
        if level not in ["HIGH", "MEDIUM", "LOW"]:
            result_json["readiness_level"] = "MEDIUM"
            
        result_json["status"] = "SECOND_LIFE_ELIGIBLE"
        result_json["eligible_for_second_life"] = True
        result_json["soh"] = soh_val
        
        return result_json
        
    except Exception as e:
        print(f"Error in Gemini GenAI Readiness: {e}")
        return {
            "error": f"Second-life readiness assessment is temporarily unavailable. Details: {str(e)}"
        }
