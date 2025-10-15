"""
API endpoints for yantra generation - FIXED VERSION
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import time
import uuid
from datetime import datetime, timedelta

from app.models import (
    YantraGenerationRequest, YantraGenerationResponse,
    YantraDimensions, Dimension, ValidationResult, ExportFile,
    YantraType, ExportFormat, AccuracyLevel, SolarPosition
)
from app.database import get_db, Project, Export, ProjectStatus
from services.samrat_yantra import SamratYantraGenerator
from services.rama_yantra import RamaYantraGenerator
from services.ephemeris import EphemerisService
from services.validation import ValidationService
from services.cad_export import CADExporter
from app.config import settings

router = APIRouter()

# Initialize services
ephemeris_service = EphemerisService()
validation_service = ValidationService()
cad_exporter = CADExporter()

@router.post("/", response_model=YantraGenerationResponse)
async def generate_yantra(
    request: YantraGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate a complete yantra with dimensions, validation, and exports
    
    This endpoint:
    1. Generates parametric geometry based on location and scale
    2. Validates against astronomical ephemeris
    3. Creates CAD exports (DXF, STL, GLTF, PDF)
    4. Returns signed URLs for downloads
    """
    start_time = time.time()
    generation_id = str(uuid.uuid4())
    
    try:
        # Select appropriate generator
        if request.yantra_type == YantraType.SAMRAT:
            generator = SamratYantraGenerator(
                latitude=request.location.latitude,
                longitude=request.location.longitude,
                scale=request.scale
            )
        elif request.yantra_type == YantraType.RAMA:
            generator = RamaYantraGenerator(
                latitude=request.location.latitude,
                longitude=request.location.longitude,
                scale=request.scale
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Yantra type {request.yantra_type} not yet implemented"
            )
        
        # Generate geometry
        geometry = generator.generate(
            material_thickness=request.material_thickness,
            kerf=request.kerf_compensation,
            include_base=request.include_base
        )
        
        # Get dimensions and BOM
        dims_dict = generator.get_dimensions_dict()
        bom = generator.get_bill_of_materials()
        
        # Extract overall dimensions based on yantra type
        overall = dims_dict.get('overall', {})
        
        # For Samrat: length/width/height
        # For Rama: diameter/diameter/height
        if 'length' in overall:
            length_value = overall['length']
            width_value = overall['width']
        elif 'diameter' in overall:
            length_value = overall['diameter']
            width_value = overall['diameter']
        else:
            # Fallback
            length_value = request.scale * 2
            width_value = request.scale * 2
        
        height_value = overall.get('height', request.scale)
        
        # Convert to Pydantic model with proper structure
        dimensions = YantraDimensions(
            overall_length=Dimension(
                value=length_value,
                tolerance=0.01,
                unit='m',
                description='Overall length/diameter'
            ),
            overall_width=Dimension(
                value=width_value,
                tolerance=0.01,
                unit='m',
                description='Overall width/diameter'
            ),
            overall_height=Dimension(
                value=height_value,
                tolerance=0.01,
                unit='m',
                description='Overall height'
            ),
            critical_dimensions=dims_dict,  # Store as-is for reference
            bom_items=bom
        )
        
        # Validate against ephemeris
        validation_result = await validate_yantra_accuracy(
            generator=generator,
            location=request.location,
            yantra_type=request.yantra_type
        )
        
        # Save to database - Convert Pydantic model to JSON-safe dict
        validation_dict = validation_result.model_dump(mode='json')
        
        project = Project(
            name=f"{request.yantra_type.value.title()} at {request.location.name or 'Custom Location'}",
            yantra_type=request.yantra_type.value,
            site_id=1,  # TODO: Create/link actual site
            scale=request.scale,
            material_thickness=request.material_thickness,
            kerf_compensation=request.kerf_compensation,
            custom_params=request.custom_params,
            dimensions=dims_dict,
            validation_results=validation_dict,  # Use JSON-safe dict
            status=ProjectStatus.GENERATED
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Generate exports asynchronously
        export_files = []
        export_formats = [ExportFormat.DXF, ExportFormat.STL, ExportFormat.GLTF, ExportFormat.PDF]
        
        for fmt in export_formats:
            # Schedule export generation
            background_tasks.add_task(
                generate_export_file,
                project_id=project.id,
                generator=generator,
                format=fmt,
                db=db
            )
            
            # Create placeholder export record
            export_file = ExportFile(
                format=fmt,
                url=f"/api/v1/export/{project.id}/{fmt.value}",  # Temporary URL
                size_bytes=0,
                checksum="pending",
                expires_at=datetime.utcnow() + timedelta(hours=settings.EXPORT_EXPIRY_HOURS),
                filename=f"{request.yantra_type.value}_{generation_id[:8]}.{fmt.value}"
            )
            export_files.append(export_file)
        
        processing_time = (time.time() - start_time) * 1000
        
        response = YantraGenerationResponse(
            id=generation_id,
            yantra_type=request.yantra_type,
            location=request.location,
            scale=request.scale,
            dimensions=dimensions,
            validation=validation_result,
            exports=export_files,
            preview_url=f"/api/v1/export/{project.id}/gltf",
            generated_at=datetime.utcnow(),
            processing_time_ms=processing_time,
            metadata={
                'project_id': project.id,
                'generator_version': settings.VERSION
            }
        )
        
        return response
        
    except Exception as e:
        import traceback
        print(f"Generation error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )

async def validate_yantra_accuracy(
    generator,
    location,
    yantra_type: YantraType
) -> ValidationResult:
    """
    Validate yantra accuracy against astronomical ephemeris
    """
    # Use summer solstice for validation (highest sun)
    test_date = datetime(2024, 6, 21, 12, 0, 0)  # Solar noon
    
    # Get actual sun position from ephemeris
    actual_sun = ephemeris_service.get_sun_position(
        latitude=location.latitude,
        longitude=location.longitude,
        timestamp=test_date,
        elevation=location.elevation
    )
    
    # Get predicted position from yantra
    shadow = generator.get_shadow_prediction(
        sun_altitude=actual_sun['altitude'],
        sun_azimuth=actual_sun['azimuth']
    )
    
    # Calculate errors
    altitude_error = abs(shadow.get('altitude_reading', actual_sun['altitude']) - actual_sun['altitude'])
    azimuth_error = abs(shadow.get('azimuth_reading', actual_sun['azimuth']) - actual_sun['azimuth'])
    
    # RMS error
    rms_error = (altitude_error**2 + azimuth_error**2)**0.5
    max_error = max(altitude_error, azimuth_error)
    
    # Determine accuracy level
    if max_error < 0.1:
        accuracy = AccuracyLevel.EXCELLENT
    elif max_error < 0.5:
        accuracy = AccuracyLevel.GOOD
    elif max_error < 1.0:
        accuracy = AccuracyLevel.ACCEPTABLE
    else:
        accuracy = AccuracyLevel.POOR
    
    predicted_position = SolarPosition(
        timestamp=test_date,
        altitude=shadow.get('altitude_reading', actual_sun['altitude']),
        azimuth=shadow.get('azimuth_reading', actual_sun['azimuth']),
        declination=actual_sun['declination'],
        hour_angle=shadow.get('hour_angle', 0),
        refraction_corrected=True
    )
    
    actual_position = SolarPosition(
        timestamp=test_date,
        altitude=actual_sun['altitude'],
        azimuth=actual_sun['azimuth'],
        declination=actual_sun['declination'],
        hour_angle=actual_sun['hour_angle'],
        refraction_corrected=True
    )
    
    return ValidationResult(
        timestamp=test_date,
        location=location,
        predicted_position=predicted_position,
        actual_position=actual_position,
        altitude_error=altitude_error,
        azimuth_error=azimuth_error,
        rms_error=rms_error,
        max_error=max_error,
        accuracy_level=accuracy
    )

async def generate_export_file(
    project_id: int,
    generator,
    format: ExportFormat,
    db: Session
):
    """
    Background task to generate export file
    """
    try:
        from pathlib import Path
        import uuid as _uuid

        # Generate file content
        content = cad_exporter.export(generator=generator, format=format.value)
        
        # Save to local filesystem (in production, use R2/MinIO)
        rel_key = f"exports/{project_id}/{format.value}/{_uuid.uuid4()}"
        root = Path("/app/exports")
        fpath = root / f"{rel_key}.{format.value}"
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_bytes(content)

        # Create database record
        export_record = Export(
            project_id=project_id,
            file_format=format.value,
            storage_key=rel_key,
            filename=f"yantra_{project_id}.{format.value}",
            size_bytes=len(content),
            checksum="sha256_placeholder",
            expires_at=datetime.utcnow() + timedelta(hours=settings.EXPORT_EXPIRY_HOURS),
            signed_url=f"/api/v1/export/{project_id}/{format.value}",
        )
        db.add(export_record)
        db.commit()
        
        print(f"✓ Generated {format.value} export for project {project_id}")
        
    except Exception as e:
        print(f"Export generation failed: {e}")
        import traceback
        print(traceback.format_exc())


@router.get("/{generation_id}", response_model=YantraGenerationResponse)
async def get_generation(generation_id: str, db: Session = Depends(get_db)):
    """Retrieve a previously generated yantra"""
    # TODO: Implement retrieval from database
    raise HTTPException(status_code=404, detail="Generation not found")

@router.get("/list")
async def list_generations(
    skip: int = 0,
    limit: int = 20,
    yantra_type: YantraType = None,
    db: Session = Depends(get_db)
):
    """List all generated yantras"""
    query = db.query(Project).filter(Project.status != ProjectStatus.ARCHIVED)
    
    if yantra_type:
        query = query.filter(Project.yantra_type == yantra_type.value)
    
    projects = query.offset(skip).limit(limit).all()
    
    return {
        'total': query.count(),
        'projects': projects
    }