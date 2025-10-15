"""
Astronomy endpoints: sun path for a day, (stub) magnetic declination
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from services.ephemeris import EphemerisService

router = APIRouter()
_ephem = EphemerisService()

class SunPathReq(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    date: datetime
    elevation: float = 0.0
    num_points: int = Field(default=96, ge=24, le=288)

@router.post("/sunpath")
def sun_path(req: SunPathReq):
    date_utc = req.date if req.date.tzinfo else req.date.replace(tzinfo=timezone.utc)
    pts = _ephem.day_sun_path(req.latitude, req.longitude, date_utc, elevation=req.elevation, num_points=req.num_points)
    # Summaries (sunrise/sunset est: just first/last visible for prototype)
    visible_idx = [i for i, p in enumerate(pts) if p["is_visible"]]
    sunrise = pts[visible_idx[0]]["time"] if visible_idx else None
    sunset = pts[visible_idx[-1]]["time"] if visible_idx else None
    solar_noon = max(pts, key=lambda p: p["altitude"])["time"] if pts else None
    day_len = len(visible_idx) * (24.0 / req.num_points) if visible_idx else 0.0
    return {
        "location": {"latitude": req.latitude, "longitude": req.longitude, "elevation": req.elevation},
        "date": date_utc.isoformat(),
        "points": pts,
        "sunrise": sunrise,
        "sunset": sunset,
        "solar_noon": solar_noon,
        "day_length_hours": round(day_len, 2),
    }

class DeclReq(BaseModel):
    latitude: float
    longitude: float
    date: datetime

@router.post("/magnetic-declination")
def magnetic_declination(_: DeclReq):
    # Stubbed value; WMM integration can be added later
    return {"declination_degrees": 0.0, "annual_change": 0.0, "model_used": "WMM (stub)"}
