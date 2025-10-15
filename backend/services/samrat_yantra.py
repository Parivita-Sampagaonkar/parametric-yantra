"""
Samrat Yantra (Equatorial Sundial) Parametric Generator
Based on authentic Jantar Mantar dimensions and formulas
"""
import math
from typing import Dict, List, Tuple, Any
import numpy as np
from dataclasses import dataclass

@dataclass
class SamratGeometry:
    """Geometric parameters for Samrat Yantra"""
    gnomon_height: float  # Height of triangular gnomon
    gnomon_base_width: float
    gnomon_thickness: float
    quadrant_radius: float  # Radius of hour scales
    hour_line_angles: List[float]  # Angles for each hour marking
    scale_divisions: int  # Number of subdivisions
    base_length: float
    base_width: float
    base_height: float

class SamratYantraGenerator:
    """
    Samrat Yantra (Supreme Instrument) - Equatorial Sundial
    
    The gnomon is aligned parallel to Earth's axis, pointing toward the celestial pole.
    Hour lines radiate at 15° intervals (24 hours = 360°).
    Scale is read on two quadrants (E and W faces).
    """
    
    def __init__(self, latitude: float, longitude: float, scale: float = 1.0):
        """
        Args:
            latitude: Site latitude in degrees (N positive)
            longitude: Site longitude in degrees (E positive)
            scale: Scale factor in meters (1.0 = 1 meter gnomon height)
        """
        self.latitude = math.radians(latitude)
        self.longitude = math.radians(longitude)
        self.scale = scale
        self.geometry = None
    
    def generate(self, material_thickness: float = 0.01, 
                 kerf: float = 0.0,
                 include_base: bool = True) -> SamratGeometry:
        """
        Generate complete Samrat Yantra geometry
        
        Args:
            material_thickness: Thickness of construction material (m)
            kerf: Kerf compensation for cutting (m)
            include_base: Include mounting base
            
        Returns:
            SamratGeometry object with all dimensions
        """
        # Gnomon (triangular wedge aligned to polar axis)
        gnomon_height = self.scale
        
        # Gnomon angle = latitude (points to celestial pole)
        # Base width calculated for structural stability
        gnomon_base_width = gnomon_height * 0.15  # Typically 15% of height
        gnomon_thickness = material_thickness
        
        # Quadrant scales
        # Traditional: radius ≈ 0.7 * height for readability
        quadrant_radius = gnomon_height * 0.7
        
        # Hour lines: 15° per hour (360° / 24 hours)
        # Range: -90° to +90° (covers full day on both quadrants)
        hour_angles = []
        for hour in range(-6, 7):  # -6h to +6h from noon
            angle = hour * 15.0  # degrees
            hour_angles.append(angle)
        
        # Scale divisions (minutes/seconds)
        scale_divisions = 60  # 1-minute resolution
        
        # Base platform
        if include_base:
            # Base should extend beyond quadrants
            base_length = quadrant_radius * 2.5
            base_width = quadrant_radius * 2.5
            base_height = gnomon_height * 0.05  # 5% of gnomon
        else:
            base_length = base_width = base_height = 0.0
        
        # Apply kerf compensation (expand all dimensions slightly)
        if kerf > 0:
            gnomon_base_width += kerf
            quadrant_radius += kerf
        
        self.geometry = SamratGeometry(
            gnomon_height=gnomon_height,
            gnomon_base_width=gnomon_base_width,
            gnomon_thickness=gnomon_thickness,
            quadrant_radius=quadrant_radius,
            hour_line_angles=hour_angles,
            scale_divisions=scale_divisions,
            base_length=base_length,
            base_width=base_width,
            base_height=base_height
        )
        
        return self.geometry
    
    def get_hour_line_coordinates(self) -> List[Dict[str, Any]]:
        """
        Calculate 3D coordinates for all hour lines on quadrants
        
        Returns:
            List of hour line definitions with start/end points
        """
        if not self.geometry:
            raise ValueError("Must call generate() first")
        
        hour_lines = []
        
        for angle_deg in self.geometry.hour_line_angles:
            angle_rad = math.radians(angle_deg)
            
            # Hour lines are marked on the quadrant surfaces
            # East quadrant (morning): positive x
            # West quadrant (afternoon): negative x
            
            # Start from gnomon edge
            start_radius = self.geometry.gnomon_base_width / 2
            end_radius = self.geometry.quadrant_radius
            
            # Coordinates in local frame (gnomon base at origin)
            # x: E-W, y: N-S, z: up
            for quadrant in ['east', 'west']:
                multiplier = 1 if quadrant == 'east' else -1
                
                start_x = multiplier * start_radius * math.cos(angle_rad)
                start_y = start_radius * math.sin(angle_rad)
                
                end_x = multiplier * end_radius * math.cos(angle_rad)
                end_y = end_radius * math.sin(angle_rad)
                
                # Lines are on the inclined quadrant surface
                # Surface angle = 90° - latitude
                surface_angle = math.pi / 2 - self.latitude
                
                # Z-coordinate varies with surface tilt
                start_z = start_y * math.tan(surface_angle)
                end_z = end_y * math.tan(surface_angle)
                
                hour_lines.append({
                    'quadrant': quadrant,
                    'hour_angle': angle_deg,
                    'hour_label': angle_deg / 15.0,  # Convert to hours from noon
                    'start': (start_x, start_y, start_z),
                    'end': (end_x, end_y, end_z)
                })
        
        return hour_lines
    
    def get_gnomon_vertices(self) -> np.ndarray:
        """
        Get 3D vertices for gnomon triangular wedge
        
        Returns:
            Nx3 array of vertex coordinates
        """
        if not self.geometry:
            raise ValueError("Must call generate() first")
        
        g = self.geometry
        h = g.gnomon_height
        w = g.gnomon_base_width
        t = g.gnomon_thickness
        
        # Gnomon is a triangular prism inclined at latitude angle
        # Base triangle in x-z plane, extruded in y direction
        
        # Calculate apex position (points to celestial pole)
        apex_x = 0
        apex_y = h * math.cos(self.latitude)
        apex_z = h * math.sin(self.latitude)
        
        # Base vertices (on ground)
        base_vertices = [
            [-w/2, -t/2, 0],  # Bottom left front
            [w/2, -t/2, 0],   # Bottom right front
            [-w/2, t/2, 0],   # Bottom left back
            [w/2, t/2, 0],    # Bottom right back
        ]
        
        # Apex vertices (at celestial pole angle)
        apex_vertices = [
            [apex_x - t/4, apex_y - t/2, apex_z],  # Apex left
            [apex_x + t/4, apex_y - t/2, apex_z],  # Apex right
            [apex_x - t/4, apex_y + t/2, apex_z],  # Apex left back
            [apex_x + t/4, apex_y + t/2, apex_z],  # Apex right back
        ]
        
        vertices = np.array(base_vertices + apex_vertices)
        return vertices
    
    def get_shadow_prediction(self, sun_altitude: float, sun_azimuth: float) -> Dict[str, Any]:
        """
        Predict where shadow will fall for given sun position
        
        Args:
            sun_altitude: Solar altitude in degrees (0=horizon, 90=zenith)
            sun_azimuth: Solar azimuth in degrees (0=N, 90=E, 180=S, 270=W)
            
        Returns:
            Shadow information including position and hour reading
        """
        if not self.geometry:
            raise ValueError("Must call generate() first")
        
        # Convert to radians
        alt_rad = math.radians(sun_altitude)
        az_rad = math.radians(sun_azimuth)
        
        # Shadow direction is opposite to sun
        shadow_azimuth = (sun_azimuth + 180) % 360
        
        # Calculate hour angle from solar position
        # Hour angle = (Local Solar Time - 12:00) * 15°
        # From azimuth: ha ≈ atan2(sin(az), cos(az)*sin(lat) - tan(alt)*cos(lat))
        
        sin_ha = math.sin(az_rad) / math.cos(alt_rad)
        cos_ha = (math.sin(alt_rad) - math.sin(self.latitude)) / (math.cos(self.latitude) * math.cos(alt_rad))
        
        hour_angle_rad = math.atan2(sin_ha, cos_ha)
        hour_angle_deg = math.degrees(hour_angle_rad)
        
        # Local solar time
        local_solar_time = 12.0 + hour_angle_deg / 15.0
        
        # Shadow falls on east quadrant (morning) or west quadrant (afternoon)
        quadrant = 'east' if hour_angle_deg < 0 else 'west'
        
        # Shadow line crosses hour markings
        g = self.geometry
        
        # Shadow length on quadrant surface
        # Depends on gnomon height and sun altitude
        if sun_altitude > 0:
            shadow_length = g.gnomon_height / math.tan(alt_rad)
        else:
            shadow_length = float('inf')  # Sun below horizon
        
        return {
            'sun_altitude': sun_altitude,
            'sun_azimuth': sun_azimuth,
            'shadow_azimuth': shadow_azimuth,
            'hour_angle': hour_angle_deg,
            'local_solar_time': local_solar_time,
            'quadrant': quadrant,
            'shadow_length': min(shadow_length, g.quadrant_radius),
            'readable': 0 < sun_altitude < 85  # Readable range
        }
    
    def get_dimensions_dict(self) -> Dict[str, Any]:
        """Get all dimensions as dictionary for export - FIXED VERSION"""
        if not self.geometry:
            raise ValueError("Must call generate() first")
        
        g = self.geometry
        
        # Return FLAT structure that matches what the API expects
        return {
            'yantra_type': 'samrat',
            'latitude': math.degrees(self.latitude),
            'scale': self.scale,
            'gnomon': {
                'height': g.gnomon_height,
                'base_width': g.gnomon_base_width,
                'thickness': g.gnomon_thickness,
                'inclination_angle': math.degrees(self.latitude)
            },
            'quadrants': {
                'radius': g.quadrant_radius,
                'hour_lines': len(g.hour_line_angles),
                'scale_divisions': g.scale_divisions
            },
            'base': {
                'length': g.base_length,
                'width': g.base_width,
                'height': g.base_height
            },
            'overall': {
                'length': g.base_length,
                'width': g.base_width,
                'height': g.gnomon_height + g.base_height
            }
        }
    
    def get_bill_of_materials(self) -> List[Dict[str, Any]]:
        """Generate bill of materials"""
        if not self.geometry:
            raise ValueError("Must call generate() first")
        
        g = self.geometry
        
        # Calculate material quantities
        gnomon_volume = (g.gnomon_height * g.gnomon_base_width * g.gnomon_thickness) * 0.5  # Triangle
        quadrant_area = math.pi * g.quadrant_radius**2  # Two quadrants
        base_volume = g.base_length * g.base_width * g.base_height
        
        bom = [
            {
                'item': 'Gnomon plate (triangular)',
                'material': 'Steel/Stone/Concrete',
                'quantity': 1,
                'dimensions': f'{g.gnomon_height:.3f}m × {g.gnomon_base_width:.3f}m × {g.gnomon_thickness:.3f}m',
                'volume_m3': gnomon_volume,
                'notes': f'Inclined at {math.degrees(self.latitude):.1f}° to horizontal'
            },
            {
                'item': 'Quadrant scales (East & West)',
                'material': 'Marble/Metal with graduations',
                'quantity': 2,
                'dimensions': f'Radius {g.quadrant_radius:.3f}m',
                'area_m2': quadrant_area,
                'notes': 'Hour lines engraved at 15° intervals'
            },
            {
                'item': 'Base platform',
                'material': 'Concrete/Stone',
                'quantity': 1,
                'dimensions': f'{g.base_length:.3f}m × {g.base_width:.3f}m × {g.base_height:.3f}m',
                'volume_m3': base_volume,
                'notes': 'Must be precisely leveled'
            },
            {
                'item': 'Anchor bolts',
                'material': 'Stainless steel',
                'quantity': 4,
                'dimensions': 'M12 × 150mm',
                'notes': 'For mounting to foundation'
            }
        ]
        
        return bom