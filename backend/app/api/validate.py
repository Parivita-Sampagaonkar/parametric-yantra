"""
Validation endpoints (lightweight): location echo & quick comparison
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from services.ephemeris import EphemerisService

router = APIRouter()
_ephem = EphemerisService()

class Location(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    elevation: float = 0.0

@router.post("/location")
def validate_location(loc: Location):
    # For now, just echo constraints OK; future: PostGIS bounds, WMM lookup, etc.
    return {
        "ok": True,
        "normalized": {
            "latitude": round(loc.latitude, 6),
            "longitude": round(loc.longitude, 6),
            "elevation": loc.elevation
        }
    }

class SunCheckRequest(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime
    elevation: float = 0.0

@router.post("/suncheck")
def validate_sun_position(req: SunCheckRequest):
    pos = _ephem.get_sun_position(req.latitude, req.longitude, req.timestamp, req.elevation)
    return {"position": pos}
