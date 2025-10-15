"""
Validation service: compares instrument-predicted readings vs ephemeris truth
"""
from datetime import datetime
from typing import Dict
from .ephemeris import EphemerisService

class ValidationService:
    def __init__(self, eph: EphemerisService | None = None):
        self.eph = eph or EphemerisService()

    def compare_shadow(self, generator, latitude: float, longitude: float, elevation: float, when: datetime) -> Dict[str, float]:
        truth = self.eph.get_sun_position(latitude, longitude, when, elevation=elevation)

        # Let instrument predict its own "reading" from truth’s sun pos
        pred = generator.get_shadow_prediction(truth["altitude"], truth["azimuth"])
        alt_pred = pred.get("altitude_reading", truth["altitude"])
        az_pred = pred.get("azimuth_reading", truth["azimuth"])

        alt_err = abs(alt_pred - truth["altitude"])
        # Smallest angular difference for azimuth
        az_diff = abs((az_pred - truth["azimuth"] + 540) % 360 - 180)
        rms = (alt_err**2 + az_diff**2) ** 0.5
        return {
            "altitude_error": alt_err,
            "azimuth_error": az_diff,
            "rms_error": rms,
            "predicted_altitude": alt_pred,
            "predicted_azimuth": az_pred,
            "declination": truth["declination"],
            "hour_angle": truth["hour_angle"],
        }
