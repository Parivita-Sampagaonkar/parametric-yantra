"""
Export endpoints: list and download generated files saved to /app/exports (local, prototype)
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from pathlib import Path
from app.database import get_db, Export

router = APIRouter()

EXPORT_ROOT = Path("/app/exports")

@router.get("/{project_id}/{fmt}")
def latest_export_for_project(project_id: int, fmt: str, db: Session = Depends(get_db)):
    rec = db.query(Export).filter(
        Export.project_id == project_id,
        Export.file_format == fmt
    ).order_by(Export.created_at.desc()).first()

    if not rec:
        raise HTTPException(status_code=404, detail="No export found")

    file_path = EXPORT_ROOT / f"{rec.storage_key}.{fmt}"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Export file missing on server")

    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=rec.filename
    )
