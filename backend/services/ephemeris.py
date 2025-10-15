"""
Ephemeris service using Skyfield + Astropy
Provides sun position (alt, az, dec, HA) for a given location & time
"""
from datetime import datetime, timezone
from skyfield.api import load, wgs84
from skyfield.almanac import find_discrete, sunrise_sunset
from math import degrees, atan2, cos, sin
from functools import lru_cache
from astropy.coordinates import get_sun, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u

class EphemerisService:
    def __init__(self, eph_path: str | None = None):
        # Use built-in downloader cache (.skyfield)
        self.ts = load.timescale()
        # Lightweight kernel (good enough for prototype). You can swap to de422/de440 later.
        self.eph = load("de421.bsp")
        self.sun = self.eph["sun"]
        self.earth = self.eph["earth"]

    def _ensure_dt(self, dt: datetime) -> datetime:
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    def get_sun_position(self, latitude, longitude, timestamp, elevation=0):
        """Return solar altitude, azimuth, declination, hour angle for given time/location."""
        time = Time(timestamp)
        loc = EarthLocation(lat=latitude*u.deg, lon=longitude*u.deg, height=elevation*u.m)

        altaz_frame = AltAz(obstime=time, location=loc)
        sun = get_sun(time).transform_to(altaz_frame)

        # Correct sidereal time usage (Astropy 6.x+)
        lst = time.sidereal_time('mean', longitude=longitude*u.deg)

        declination = get_sun(time).dec.deg
        hour_angle = (lst.hour * 15.0) - longitude  # in degrees

        return {
            "altitude": sun.alt.deg,
            "azimuth": sun.az.deg,
            "declination": declination,
            "hour_angle": hour_angle,
        }

    @lru_cache(maxsize=256)
    def day_sun_path(self, latitude: float, longitude: float, date_utc: datetime, elevation: float = 0.0, num_points: int = 96):
        """
        Compute sun path across a given UTC calendar date.
        Returns list of {time, altitude, azimuth, is_visible}
        """
        # Build times across the date (every ~15 min if 96 points)
        date_utc = date_utc.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        seconds = [int(i * 86400 / num_points) for i in range(num_points)]
        times = [date_utc.timestamp() + s for s in seconds]
        t_sf = self.ts.tt_jd([self.ts.from_datetime(datetime.fromtimestamp(ts, tz=timezone.utc)).tt for ts in times])

        observer = self.earth + wgs84.latlon(latitude, longitude, elevation_m=elevation)
        app = observer.at(t_sf).observe(self.sun).apparent()
        alt, az, _ = app.altaz()

        points = []
        for i, tt in enumerate(t_sf):
            points.append({
                "time": datetime.fromtimestamp(times[i], tz=timezone.utc).isoformat(),
                "altitude": alt.degrees[i],
                "azimuth": az.degrees[i],
                "is_visible": alt.degrees[i] > 0.0,
            })
        return points
