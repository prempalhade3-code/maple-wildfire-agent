import re
import asyncio
from datetime import datetime, timedelta
import logging
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from weather_client import WeatherClient
from mireye_client import MireyeClient
from models import RiskScore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Coordinates lookup mapping line ID to coordinates
LINE_COORDINATES = {
    1: (36.2704, -121.8081),
    2: (38.4404, -122.6801),
    3: (38.5804, -122.5801),
    4: (37.7749, -122.4194),
}

def parse_mireye_response(text: str, defaults: dict) -> dict:
    """
    Extracts key numeric parameters from Mireye's natural language response using regex.
    """
    parsed = {}

    # 1. Soil Moisture (e.g., "12%", "9.5%")
    soil_match = re.search(r'(?:soil moisture|moisture|soil).*?\b(\d+(?:\.\d+)?)\s*%', text, re.IGNORECASE)
    parsed["soil_moisture"] = float(soil_match.group(1)) if soil_match else defaults.get("soil_moisture", 20.0)

    # 2. Canopy Density (e.g., "canopy density of 65%")
    canopy_match = re.search(r'(?:canopy|vegetation|density).*?\b(\d+(?:\.\d+)?)\s*%', text, re.IGNORECASE)
    parsed["canopy_density"] = float(canopy_match.group(1)) if canopy_match else defaults.get("canopy_density", 30.0)

    # 3. Slope (e.g., "slope is 15 degrees", "15°", "4.07 degrees")
    slope_match = re.search(r'(?:slope|incline).*?\b(\d+(?:\.\d+)?)\s*(?:degree|°|\b)', text, re.IGNORECASE)
    parsed["slope"] = float(slope_match.group(1)) if slope_match else defaults.get("slope", 10.0)

    # 4. Transmission Line Distance (e.g., "80 feet", "120 feet")
    dist_match = re.search(r'(?:distance|line|transmission).*?\b(\d+(?:\.\d+)?)\s*(feet|ft|miles|mi|meters|m)\b', text, re.IGNORECASE)
    if dist_match:
        val = float(dist_match.group(1))
        unit = dist_match.group(2).lower()
        if unit in ["miles", "mi"]:
            parsed["distance"] = val * 5280
        elif unit in ["meters", "m"]:
            parsed["distance"] = val * 3.28084
        else:
            parsed["distance"] = val
    else:
        parsed["distance"] = defaults.get("distance", 150.0)

    # 5. Building Count (e.g., "2 residential buildings")
    build_match = re.search(r'\b(\d+)\s*(?:building|structure|residence|home)', text, re.IGNORECASE)
    parsed["building_count"] = int(build_match.group(1)) if build_match else defaults.get("building_count", 0)

    return parsed

def calculate_risk_metrics(weather: dict, mireye_data: dict) -> dict:
    """
    Runs the risk model calculation.
    Computes Probability of Ignition, Consequence Score, and feature contributions.
    """
    wind = weather.get("wind_speed", 10.0)
    humidity = weather.get("humidity", 50.0)
    
    soil = mireye_data.get("soil_moisture", 20.0)
    canopy = mireye_data.get("canopy_density", 30.0)
    slope = mireye_data.get("slope", 10.0)
    distance = mireye_data.get("distance", 150.0)
    buildings = mireye_data.get("building_count", 0)

    # ---- 1. PROBABILITY OF IGNITION (P_ignition) ----
    if wind > 30:
        wind_score = 95.0
    elif wind > 15:
        wind_score = 60.0
    else:
        wind_score = 20.0

    if soil < 12:
        soil_score = 95.0
    elif soil < 25:
        soil_score = 50.0
    else:
        soil_score = 15.0

    if humidity < 30:
        humidity_score = 90.0
    elif humidity < 60:
        humidity_score = 50.0
    else:
        humidity_score = 15.0

    if canopy > 60:
        canopy_score = 90.0
    elif canopy > 20:
        canopy_score = 50.0
    else:
        canopy_score = 10.0

    p_ignition = (wind_score * 0.35) + (soil_score * 0.30) + (humidity_score * 0.20) + (canopy_score * 0.15)

    # ---- 2. CONSEQUENCE SCORE (C_consequence) ----
    if slope > 25:
        slope_score = 95.0
    elif slope > 10:
        slope_score = 50.0
    else:
        slope_score = 15.0

    if distance < 200:
        dist_score = 90.0
    elif distance < 1000:
        dist_score = 45.0
    else:
        dist_score = 10.0

    if buildings > 5:
        build_score = 95.0
    elif buildings > 0:
        build_score = 60.0
    else:
        build_score = 10.0

    c_consequence = (slope_score * 0.30) + (dist_score * 0.30) + (build_score * 0.40)

    # ---- 3. FINAL INTEGRATED RISK SCORE ----
    final_risk = (p_ignition * 0.55) + (c_consequence * 0.45)

    # ---- 4. FEATURE CONTRIBUTION ATTRIBUTION ----
    contributions = {
        "Wind Speed (Weather)": round((wind_score * 0.35 * 0.55 / final_risk) * 100, 1) if final_risk > 0 else 0.0,
        "Soil Dryness (Mireye)": round((soil_score * 0.30 * 0.55 / final_risk) * 100, 1) if final_risk > 0 else 0.0,
        "Air Dryness (Weather)": round((humidity_score * 0.20 * 0.55 / final_risk) * 100, 1) if final_risk > 0 else 0.0,
        "Vegetation Canopy (Mireye)": round((canopy_score * 0.15 * 0.55 / final_risk) * 100, 1) if final_risk > 0 else 0.0,
        "Terrain Slope (Mireye)": round((slope_score * 0.30 * 0.45 / final_risk) * 100, 1) if final_risk > 0 else 0.0,
        "Grid Proximity (Mireye)": round((dist_score * 0.30 * 0.45 / final_risk) * 100, 1) if final_risk > 0 else 0.0,
        "Human Exposures (Mireye)": round((build_score * 0.40 * 0.45 / final_risk) * 100, 1) if final_risk > 0 else 0.0
    }

    # Normalize contributions
    total_attrib = sum(contributions.values())
    if total_attrib > 0:
        for k in contributions:
            contributions[k] = round((contributions[k] / total_attrib) * 100, 1)

    return {
        "risk_score": round(final_risk, 1),
        "ignition_probability": round(p_ignition / 100.0, 3), # as a ratio 0-1
        "consequence_score": round(c_consequence / 100.0, 3),   # as a ratio 0-1
        "contributions": contributions
    }

DEMO_SEVERE_WEATHER = {
    "wind_speed": 38.0,
    "wind_direction": 55,
    "humidity": 18.0,
    "temperature": 96.0,
    "timestamp": "demo scenario",
    "source": "Maple severe-weather demo scenario",
    "success": True,
}

DEMO_SEVERE_PHYSICAL = {
    "soil_moisture": 5.0,
    "canopy_density": 80.0,
    "slope": 30.0,
    "distance": 80.0,
    "building_count": 8,
}


def normalize_citations(citations: list) -> list[dict]:
    """Return a consistent, UI-safe citation shape for live and demo data."""
    normalized = []
    for citation in citations:
        if isinstance(citation, str):
            normalized.append({"source": citation})
        elif isinstance(citation, dict) and citation.get("source"):
            normalized.append({
                "source": citation["source"],
                "source_url": citation.get("source_url"),
                "fields": citation.get("fields", []),
                "fetched_at": citation.get("fetched_at"),
                "confidence": citation.get("confidence"),
            })
    return normalized


async def compute_risk_for_line(db: AsyncSession, line, scenario: str | None = None, persist: bool = True) -> dict:
    """
    Computes wildfire risk for a given transmission line by calling weather and Mireye APIs,
    running calculations, storing the score in the database, and returning the dashboard payload.
    """
    # 1. Fetch coords
    lat, lng = LINE_COORDINATES.get(line.id, (36.2704, -121.8081))

    # 2. Async API fetches
    weather_client = WeatherClient()
    mireye_client = MireyeClient()

    mireye_task = mireye_client.query_grid_node_safety(lat, lng)
    # This is an explicit, labelled demo control so a reviewer can always see
    # the protective-action branch regardless of the weather on demo day.
    if scenario == "severe":
        weather_res = DEMO_SEVERE_WEATHER.copy()
        mireye_res = await mireye_task
    else:
        weather_task = weather_client.get_current_weather(lat, lng)
        weather_res, mireye_res = await asyncio.gather(weather_task, mireye_task)

    # Fallback default weather if it fails
    if not weather_res.get("success"):
        weather_res = {
            "wind_speed": 10.0,
            "wind_direction": 180,
            "humidity": 50.0,
            "temperature": 70.0
        }

    # Extract mireye data parameters
    mireye_defaults = {
        "soil_moisture": 20.0,
        "canopy_density": 30.0,
        "slope": 10.0,
        "distance": 150.0,
        "building_count": 0
    }
    mireye_data = parse_mireye_response(mireye_res.get("answer", ""), mireye_defaults)
    if scenario == "severe":
        # Keep the normal mode entirely live. This mode intentionally models a
        # severe dry-fuel event so the protective workflow is always demonstrable.
        mireye_data = DEMO_SEVERE_PHYSICAL.copy()

    # 3. Calculate Risk
    metrics = calculate_risk_metrics(weather_res, mireye_data)

    # 4. Build an inspectable evidence and decision record.
    timestamp = datetime.utcnow().isoformat() + "Z"
    mireye_live = bool(mireye_res.get("live", False))
    citations = normalize_citations(mireye_res.get("citations", []))
    if scenario == "severe":
        data_mode = "severe-weather demo scenario; live Mireye citations attached"
        mireye_source = "Maple severe-weather demo scenario"
    else:
        data_mode = "live Mireye response" if mireye_live else "demo fallback (Mireye unavailable)"
        mireye_source = "Mireye physical-world intelligence" if mireye_live else "Local demo fallback — not live Mireye"
    weather_source = weather_res.get("source", "Open-Meteo")
    weather_timestamp = weather_res.get("timestamp") or timestamp
    evidence = [
        {"label": "Wind speed", "value": f"{weather_res.get('wind_speed', 0):.1f} mph", "source": weather_source, "timestamp": weather_timestamp, "category": "weather"},
        {"label": "Relative humidity", "value": f"{weather_res.get('humidity', 0):.1f}%", "source": weather_source, "timestamp": weather_timestamp, "category": "weather"},
        {"label": "Air temperature", "value": f"{weather_res.get('temperature', 0):.1f}°F", "source": weather_source, "timestamp": weather_timestamp, "category": "weather"},
        {"label": "Soil moisture", "value": f"{mireye_data.get('soil_moisture', 0):.1f}%", "source": mireye_source, "timestamp": timestamp, "category": "physical"},
        {"label": "Vegetation canopy", "value": f"{mireye_data.get('canopy_density', 0):.1f}%", "source": mireye_source, "timestamp": timestamp, "category": "physical"},
        {"label": "Terrain slope", "value": f"{mireye_data.get('slope', 0):.1f}°", "source": mireye_source, "timestamp": timestamp, "category": "physical"},
        {"label": "Line proximity", "value": f"{mireye_data.get('distance', 0):.0f} ft", "source": mireye_source, "timestamp": timestamp, "category": "physical"},
        {"label": "Nearby structures", "value": str(mireye_data.get('building_count', 0)), "source": mireye_source, "timestamp": timestamp, "category": "physical"},
    ]
    confidence = min(96, round(66 + (12 if weather_res.get("success") else 0) + (12 if mireye_live else 4) + (6 if citations else 0), 1))
    should_isolate = metrics["risk_score"] > 70.0
    decision = {
        "recommendation": "Isolate this line segment" if should_isolate else "Continue heightened monitoring",
        "confidence": confidence,
        "action_mode": "simulated SCADA protective action",
        "reason": "Wind, fuel dryness, terrain exposure, and nearby structures exceed the intervention threshold." if should_isolate else "The current evidence remains below Maple's simulated isolation threshold."
    }
    weather_detail = (
        "Severe-weather demo scenario"
        if scenario == "severe"
        else "Open-Meteo returned wind, humidity, and temperature."
    )
    decision_timeline = [
        {"stage": "Weather ingested", "detail": weather_detail, "timestamp": weather_timestamp, "status": "complete"},
        {"stage": "Physical evidence resolved", "detail": f"{data_mode}; {len(citations)} cited datasets attached.", "timestamp": timestamp, "status": "complete"},
        {"stage": "Risk reasoned", "detail": f"Wildfire risk calculated at {metrics['risk_score']}% with {confidence}% confidence.", "timestamp": timestamp, "status": "complete"},
        {"stage": "Protective recommendation", "detail": decision["recommendation"] + " — " + decision["action_mode"] + ".", "timestamp": timestamp, "status": "ready"},
    ]
    # 5. Save to DB
    if persist:
        db_risk = RiskScore(
            line_id=line.id,
            score=metrics["risk_score"],
            probability=metrics["ignition_probability"],
            consequence=metrics["consequence_score"],
            timestamp=timestamp
        )
        db.add(db_risk)
        # Keep the audit database bounded. ISO timestamps sort correctly as text.
        cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
        await db.execute(delete(RiskScore).where(RiskScore.timestamp < cutoff))
        await db.commit()

    # 6. Return complete, inspectable payload
    return {
        "line_id": line.id,
        "score": metrics["risk_score"],
        "probability": metrics["ignition_probability"],
        "consequence": metrics["consequence_score"],
        "timestamp": timestamp,
        "wind_speed": weather_res.get("wind_speed"),
        "wind_direction": weather_res.get("wind_direction"),
        "humidity": weather_res.get("humidity"),
        "temperature": weather_res.get("temperature"),
        "soil_moisture": mireye_data.get("soil_moisture"),
        "canopy_density": mireye_data.get("canopy_density"),
        "slope": mireye_data.get("slope"),
        "distance": mireye_data.get("distance"),
        "building_count": mireye_data.get("building_count"),
        "contributions": metrics["contributions"],
        "citations": citations,
        "evidence": evidence,
        "decision": decision,
        "decision_timeline": decision_timeline,
        "data_mode": data_mode
    }
