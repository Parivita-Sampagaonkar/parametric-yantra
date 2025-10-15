"""
Pydantic models for request/response validation - FIXED VERSION
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Literal, Any
from datetime import datetime
from enum import Enum

# Enums
class YantraType(str, Enum):
    """Supported yantra types"""
    SAMRAT = "samrat"
    RAMA = "rama"
    DIGAMSA = "digamsa"
    DHRUVA_PRAKSHA = "dhruva_praksha"
    BHITTI = "bhitti"
    RASIVALAYA = "rasivalaya"
    NADI_VALAYA = "nadi_valaya"

class ExportFormat(str, Enum):
    """Export file formats"""
    DXF = "dxf"
    STL = "stl"
    GLTF = "gltf"
    STEP = "step"
    PDF = "pdf"
    SVG = "svg"

class AccuracyLevel(str, Enum):
    """Accuracy badge levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"

# Location Models
class Location(BaseModel):
    """Geographic location"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    elevation: float = Field(default=0.0, ge=-500, le=9000)
    timezone: str = Field(default="UTC")
    name: Optional[str] = Field(None, max_length=200)
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        return round(v, 6)
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        return round(v, 6)

# Generation Request Models
class YantraGenerationRequest(BaseModel):
    """Request to generate a yantra"""
    yantra_type: YantraType
    location: Location
    scale: float = Field(default=1.0, gt=0.1, le=1000)
    material_thickness: float = Field(default=0.01, gt=0, le=1)
    kerf_compensation: float = Field(default=0.0, ge=0, le=0.01)
    include_base: bool = Field(default=True)
    custom_params: Optional[Dict[str, Any]] = Field(default=None)

# Dimension Models - SIMPLIFIED
class Dimension(BaseModel):
    """A dimensional measurement"""
    value: float
    tolerance: float = 0.0
    unit: str = "m"
    description: Optional[str] = None

class YantraDimensions(BaseModel):
    """Complete dimensional specification - SIMPLIFIED"""
    overall_length: Dimension
    overall_width: Dimension
    overall_height: Dimension
    critical_dimensions: Dict[str, Any]  # Store as flexible dict
    bom_items: List[Dict[str, Any]]

# Validation Models
class SolarPosition(BaseModel):
    """Solar position at a specific time"""
    timestamp: datetime
    altitude: float
    azimuth: float
    declination: float
    hour_angle: float
    refraction_corrected: bool = True

class ValidationResult(BaseModel):
    """Truth-check validation results"""
    timestamp: datetime
    location: Location
    predicted_position: SolarPosition
    actual_position: SolarPosition
    altitude_error: float
    azimuth_error: float
    rms_error: float
    max_error: float
    accuracy_level: AccuracyLevel

# Export Models
class ExportFile(BaseModel):
    """Generated export file information"""
    format: ExportFormat
    url: str
    size_bytes: int
    checksum: str
    expires_at: datetime
    filename: str

# Generation Response
class YantraGenerationResponse(BaseModel):
    """Complete yantra generation result"""
    id: str
    yantra_type: YantraType
    location: Location
    scale: float
    dimensions: YantraDimensions
    validation: ValidationResult
    exports: List[ExportFile]
    preview_url: Optional[str] = None
    generated_at: datetime
    processing_time_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Astronomy Models
class SunPathRequest(BaseModel):
    """Request for sun path calculation"""
    location: Location
    date: datetime
    num_points: int = Field(default=96, ge=24, le=288)

class SunPathPoint(BaseModel):
    """Single point on sun path"""
    time: datetime
    altitude: float
    azimuth: float
    is_visible: bool

class SunPathResponse(BaseModel):
    """Sun path for a day"""
    location: Location
    date: datetime
    points: List[SunPathPoint]
    sunrise: Optional[datetime]
    sunset: Optional[datetime]
    solar_noon: Optional[datetime]
    day_length_hours: float

# Magnetic Declination
class MagneticDeclinationRequest(BaseModel):
    """Request magnetic declination"""
    location: Location
    date: datetime

class MagneticDeclinationResponse(BaseModel):
    """Magnetic declination result"""
    location: Location
    date: datetime
    declination_degrees: float
    annual_change: float
    model_used: str = "WMM2020"

# Error Response
class ErrorResponse(BaseModel):
    """Standard error response"""
    message: str
    detail: Optional[str] = None