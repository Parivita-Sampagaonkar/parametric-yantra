"""
Rama Yantra (Alt-Azimuth Instrument) Parametric Generator
Cylindrical pillar pair for measuring altitude and azimuth
"""
import math
from typing import Dict, List, Tuple, Any
import numpy as np
from dataclasses import dataclass

@dataclass
class RamaGeometry:
    """Geometric parameters for Rama Yantra"""
    pillar_radius: float  # Radius of cylindrical pillars
    pillar_height: float  # Height of pillars
    pillar_separation: float  # Distance between pillar centers
    wall_thickness: float  # Thickness of pillar walls
    azimuth_divisions: int  # Number of azimuth markings
    altitude_scale_height: float  # Height of altitude scale
    central_platform_radius: float  # Central gnomon platform
    gnomon_height: float  # Central gnomon height
    base_diameter: float
    base_height: float

class RamaYantraGenerator:
    """
    Rama Yantra - Altitude-Azimuth Instrument
    
    Consists of two complementary cylindrical structures (sectors):
    - Sector A: Open toward N-S, closed E-W
    - Sector B: Open toward E-W, closed N-S
    
    Central gnomon casts shadow on graduated walls and floor.
    Measures both altitude (height on wall) and azimuth (direction on floor).
    """
    
    def __init__(self, latitude: float, longitude: float, scale: float = 1.0):
        """
        Args:
            latitude: Site latitude in degrees (N positive)
            longitude: Site longitude in degrees (E positive)
            scale: Scale factor in meters (1.0 = 1 meter pillar radius)
        """
        self.latitude = math.radians(latitude)
        self.longitude = math.radians(longitude)
        self.scale = scale
        self.geometry = None
    
    def generate(self, material_thickness: float = 0.15,
                 kerf: float = 0.0,
                 include_base: bool = True) -> RamaGeometry:
        """
        Generate complete Rama Yantra geometry
        
        Args:
            material_thickness: Thickness of walls (m)
            kerf: Kerf compensation (m)
            include_base: Include base platform
            
        Returns:
            RamaGeometry object with all dimensions
        """
        # Main cylinder dimensions
        pillar_radius = self.scale
        
        # Height typically equals diameter for good altitude coverage
        pillar_height = pillar_radius * 2.0
        
        # Two pillars are separate cylinders, spaced apart
        # Spacing allows access to central gnomon
        pillar_separation = pillar_radius * 0.5
        
        # Wall thickness (masonry structures)
        wall_thickness = max(material_thickness, pillar_radius * 0.1)
        
        # Azimuth markings on floor (360° divided)
        azimuth_divisions = 360  # 1° resolution
        
        # Altitude scale on inner walls
        # Range: 0° (horizon) to 90° (zenith)
        altitude_scale_height = pillar_height
        
        # Central gnomon platform
        central_platform_radius = pillar_separation * 0.4
        
        # Central gnomon (vertical rod)
        # Height should be significant fraction of pillar height
        gnomon_height = pillar_height * 0.3
        
        # Base platform
        if include_base:
            # Base encompasses both pillars plus working space
            base_diameter = (pillar_radius * 2 + pillar_separation) * 1.3
            base_height = pillar_height * 0.03
        else:
            base_diameter = base_height = 0.0
        
        # Apply kerf
        if kerf > 0:
            pillar_radius += kerf
            wall_thickness += kerf
        
        self.geometry = RamaGeometry(
            pillar_radius=pillar_radius,
            pillar_height=pillar_height,
            pillar_separation=pillar_separation,
            wall_thickness=wall_thickness,
            azimuth_divisions=azimuth_divisions,
            altitude_scale_height=altitude_scale_height,
            central_platform_radius=central_platform_radius,
            gnomon_height=gnomon_height,
            base_diameter=base_diameter,
            base_height=base_height
        )
        
        return self.geometry
    
    def get_pillar_vertices(self, sector: str = 'A') -> np.ndarray:
        """
        Get vertices for cylindrical pillar sector
        
        Args:
            sector: 'A' (N-S open) or 'B' (E-W open)
            
        Returns:
            Nx3 array of vertices
        """
        if not self.geometry:
            raise ValueError("Must call generate() first")
        
        g = self.geometry
        
        # Generate cylinder vertices
        # Sector A: semicircle facing E-W (open N-S)
        # Sector B: semicircle facing N-S (open E-W)
        
        num_segments = 60
        vertices = []
        
        if sector == 'A':
            # Open toward N-S (0° and 180°)
            # Closed E-W (90° and 270°)
            angle_start = -math.pi / 2  # -90° (E)
            angle_end = math.pi / 2      # +90° (W)
            x_offset = -g.pillar_separation / 2
        else:  # sector == 'B'
            # Open toward E-W (90° and 270°)
            # Closed N-S (0° and 180°)
            angle_start = 0  # 0° (N)
            angle_end = math.pi  # 180° (S)
            x_offset = g.pillar_separation / 2
        
        # Generate outer wall vertices (bottom and top)
        for i in range(num_segments + 1):
            t = i / num_segments
            angle = angle_start + t * (angle_end - angle_start)
            
            x = x_offset + g.pillar_radius * math.cos(angle)
            y = g.pillar_radius * math.sin(angle)
            
            # Bottom ring
            vertices.append([x, y, 0])
            # Top ring
            vertices.append([x, y, g.pillar_height])
        
        # Inner wall (for thickness)
        inner_radius = g.pillar_radius - g.wall_thickness
        for i in range(num_segments + 1):
            t = i / num_segments
            angle = angle_start + t * (angle_end - angle_start)
            
            x = x_offset + inner_radius * math.cos(angle)
            y = inner_radius * math.sin(angle)
            
            vertices.append([x, y, 0])
            vertices.append([x, y, g.pillar_height])
        
        return np.array(vertices)
    
    def get_azimuth_markings(self) -> List[Dict[str, Any]]:
        """
        Calculate azimuth markings on floor
        
        Returns:
            List of azimuth line definitions
        """
        if not self.geometry:
            raise ValueError("Must call generate() first")
        
        g = self.geometry
        markings = []
        
        # Radial lines from center to pillar walls
        for azimuth in range(0, 360, 1):  # Every 1 degree
            angle_rad = math.radians(azimuth)
            
            # Line from central platform to pillar inner wall
            start_radius = g.central_platform_radius
            end_radius = g.pillar_radius - g.wall_thickness
            
            start_x = start_radius * math.sin(angle_rad)
            start_y = start_radius * math.cos(angle_rad)
            
            end_x = end_radius * math.sin(angle_rad)
            end_y = end_radius * math.cos(angle_rad)
            
            # Determine which sector this line falls in
            # Sector A: E-W closed (azimuth ≈ 90° or 270°)
            # Sector B: N-S closed (azimuth ≈ 0° or 180°)
            
            in_sector_A = (45 <= azimuth <= 135) or (225 <= azimuth <= 315)
            in_sector_B = not in_sector_A
            
            markings.append({
                'azimuth': azimuth,
                'cardinal': self._azimuth_to_cardinal(azimuth),
                'start': (start_x, start_y, 0),
                'end': (end_x, end_y, 0),
                'sector': 'A' if in_sector_A else 'B',
                'major': azimuth % 10 == 0  # Major markings every 10°
            })
        
        return markings
    
    def get_altitude_scale(self, sector: str = 'A') -> List[Dict[str, Any]]:
        """
        Calculate altitude scale markings on inner wall
        
        Args:
            sector: 'A' or 'B'
            
        Returns:
            List of altitude marking definitions
        """
        if not self.geometry:
            raise ValueError("Must call generate() first")
        
        g = self.geometry
        scale_marks = []
        
        # Altitude scale: 0° (floor) to 90° (zenith, top of wall)
        # Height on wall = R * tan(altitude)
        # But for practical reading, use linear scale based on wall height
        
        for altitude in range(0, 91, 1):  # 0° to 90°, every 1°
            # Height on wall proportional to altitude angle
            # h = gnomon_height * tan(altitude)
            # But we need to fit within pillar_height
            
            # Use linear interpolation for simplicity
            height_ratio = altitude / 90.0
            wall_height = height_ratio * g.altitude_scale_height
            
            # Also calculate the theoretical height for a gnomon
            if altitude < 89:
                theoretical_height = g.gnomon_height * math.tan(math.radians(altitude))
            else:
                theoretical_height = g.altitude_scale_height
            
            scale_marks.append({
                'altitude': altitude,
                'wall_height': min(wall_height, g.pillar_height),
                'theoretical_height': min(theoretical_height, g.pillar_height),
                'sector': sector,
                'major': altitude % 5 == 0  # Major marks every 5°
            })
        
        return scale_marks
    
    def get_shadow_prediction(self, sun_altitude: float, sun_azimuth: float) -> Dict[str, Any]:
        """
        Predict shadow position for given sun position
        
        Args:
            sun_altitude: Solar altitude in degrees (0-90)
            sun_azimuth: Solar azimuth in degrees (0=N, 90=E)
            
        Returns:
            Shadow information for Rama Yantra reading
        """
        if not self.geometry:
            raise ValueError("Must call generate() first")
        
        g = self.geometry
        
        # Shadow is cast opposite to sun direction
        shadow_azimuth = (sun_azimuth + 180) % 360
        
        # Shadow length on floor (from central gnomon)
        if sun_altitude > 0:
            shadow_length_floor = g.gnomon_height / math.tan(math.radians(sun_altitude))
        else:
            shadow_length_floor = float('inf')
        
        # Shadow tip coordinates on floor
        shadow_tip_x = shadow_length_floor * math.sin(math.radians(shadow_azimuth))
        shadow_tip_y = shadow_length_floor * math.cos(math.radians(shadow_azimuth))
        
        # Height on wall where shadow would mark (if it reaches wall)
        wall_shadow_height = g.gnomon_height * math.tan(math.radians(sun_altitude))
        
        # Determine which sector the shadow falls in
        in_sector_A = (45 <= shadow_azimuth <= 135) or (225 <= shadow_azimuth <= 315)
        sector = 'A' if in_sector_A else 'B'
        
        # Check if shadow reaches wall
        max_floor_radius = g.pillar_radius - g.wall_thickness
        reaches_wall = shadow_length_floor <= max_floor_radius
        
        return {
            'sun_altitude': sun_altitude,
            'sun_azimuth': sun_azimuth,
            'shadow_azimuth': shadow_azimuth,
            'shadow_length': min(shadow_length_floor, max_floor_radius),
            'shadow_tip': (shadow_tip_x, shadow_tip_y, 0),
            'wall_height': min(wall_shadow_height, g.pillar_height),
            'sector': sector,
            'readable': 0 < sun_altitude < 85 and reaches_wall,
            'azimuth_reading': shadow_azimuth,
            'altitude_reading': sun_altitude
        }
    
    def _azimuth_to_cardinal(self, azimuth: float) -> str:
        """Convert azimuth to cardinal direction"""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = round(azimuth / 22.5) % 16
        return directions[index]
    
    def get_dimensions_dict(self) -> Dict[str, Any]:
        """Get all dimensions as dictionary - FIXED"""
        if not self.geometry:
            raise ValueError("Must call generate() first")
        
        g = self.geometry
        
        return {
            'yantra_type': 'rama',
            'latitude': math.degrees(self.latitude),
            'scale': self.scale,
            'pillars': {
                'radius': g.pillar_radius,
                'height': g.pillar_height,
                'separation': g.pillar_separation,
                'wall_thickness': g.wall_thickness,
                'sectors': ['A (N-S open)', 'B (E-W open)']
            },
            'scales': {
                'azimuth_divisions': g.azimuth_divisions,
                'azimuth_range': '0° to 360°',
                'altitude_range': '0° to 90°',
                'altitude_scale_height': g.altitude_scale_height
            },
            'central_gnomon': {
                'platform_radius': g.central_platform_radius,
                'gnomon_height': g.gnomon_height
            },
            'base': {
                'diameter': g.base_diameter,
                'height': g.base_height
            },
            'overall': {
                'diameter': g.base_diameter,
                'height': g.pillar_height + g.base_height
            }
        }


    
    def get_bill_of_materials(self) -> List[Dict[str, Any]]:
        """Generate bill of materials"""
        if not self.geometry:
            raise ValueError("Must call generate() first")
        
        g = self.geometry
        
        # Calculate material volumes
        # Each pillar is a semicircular shell
        outer_volume = math.pi * g.pillar_radius**2 * g.pillar_height / 2
        inner_volume = math.pi * (g.pillar_radius - g.wall_thickness)**2 * g.pillar_height / 2
        wall_volume_per_pillar = outer_volume - inner_volume
        
        floor_area = math.pi * (g.pillar_radius - g.wall_thickness)**2
        base_volume = math.pi * (g.base_diameter / 2)**2 * g.base_height
        
        bom = [
            {
                'item': 'Cylindrical pillar walls (Sector A)',
                'material': 'Masonry/Concrete',
                'quantity': 1,
                'dimensions': f'R={g.pillar_radius:.3f}m, H={g.pillar_height:.3f}m, t={g.wall_thickness:.3f}m',
                'volume_m3': wall_volume_per_pillar,
                'notes': 'Semicircular, open N-S, closed E-W'
            },
            {
                'item': 'Cylindrical pillar walls (Sector B)',
                'material': 'Masonry/Concrete',
                'quantity': 1,
                'dimensions': f'R={g.pillar_radius:.3f}m, H={g.pillar_height:.3f}m, t={g.wall_thickness:.3f}m',
                'volume_m3': wall_volume_per_pillar,
                'notes': 'Semicircular, open E-W, closed N-S'
            },
            {
                'item': 'Floor surface with graduations',
                'material': 'Polished marble/stone',
                'quantity': 1,
                'dimensions': f'Diameter {g.pillar_radius * 2:.3f}m',
                'area_m2': floor_area,
                'notes': 'Azimuth lines engraved (360° markings)'
            },
            {
                'item': 'Central gnomon (vertical rod)',
                'material': 'Metal/Stone',
                'quantity': 1,
                'dimensions': f'Height {g.gnomon_height:.3f}m, Ø 50mm',
                'notes': 'Must be perfectly vertical'
            },
            {
                'item': 'Central platform',
                'material': 'Stone/Concrete',
                'quantity': 1,
                'dimensions': f'Radius {g.central_platform_radius:.3f}m',
                'notes': 'Raised platform for gnomon base'
            },
            {
                'item': 'Base platform',
                'material': 'Concrete',
                'quantity': 1,
                'dimensions': f'Diameter {g.base_diameter:.3f}m, H={g.base_height:.3f}m',
                'volume_m3': base_volume,
                'notes': 'Foundation must be perfectly level'
            },
            {
                'item': 'Altitude scale markings',
                'material': 'Engraved/Painted graduations',
                'quantity': 2,
                'dimensions': f'Height 0 to {g.pillar_height:.3f}m',
                'notes': 'One set per sector, 0° to 90° scale'
            }
        ]
        
        return bom