"""
Database configuration and ORM models
Uses SQLAlchemy with PostgreSQL + PostGIS
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime
from typing import Generator
import enum

from app.config import settings

# Create engine
engine = create_engine(
    settings.get_database_url(),
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Enums for database
class YantraTypeEnum(str, enum.Enum):
    SAMRAT = "samrat"
    RAMA = "rama"
    DIGAMSA = "digamsa"
    DHRUVA_PRAKSHA = "dhruva_praksha"
    BHITTI = "bhitti"
    RASIVALAYA = "rasivalaya"
    NADI_VALAYA = "nadi_valaya"

class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    EXPORTED = "exported"
    ARCHIVED = "archived"

class ObservationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# ORM Models
class User(Base):
    """User account"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_educator = Column(Boolean, default=False)
    is_moderator = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User {self.username}>"

class Site(Base):
    """Geographic site for yantra installation"""
    __tablename__ = "sites"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, default=0.0)
    timezone = Column(String(50), nullable=False)
    magnetic_declination = Column(Float)  # Cached value
    declination_updated_at = Column(DateTime(timezone=True))
    description = Column(Text)
    owner_id = Column(Integer, nullable=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Site {self.name}>"

class Project(Base):
    """Yantra generation project"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    yantra_type = Column(SQLEnum(YantraTypeEnum), nullable=False)
    site_id = Column(Integer, nullable=False)
    scale = Column(Float, nullable=False)
    material_thickness = Column(Float, default=0.01)
    kerf_compensation = Column(Float, default=0.0)
    custom_params = Column(JSON)
    dimensions = Column(JSON)  # YantraDimensions as JSON
    validation_results = Column(JSON)  # ValidationResult as JSON
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)
    owner_id = Column(Integer, nullable=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Project {self.name} ({self.yantra_type})>"

class Export(Base):
    """Generated export file"""
    __tablename__ = "exports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    file_format = Column(String(10), nullable=False)
    storage_key = Column(String(500), nullable=False)  # R2/MinIO key
    filename = Column(String(255), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    checksum = Column(String(64), nullable=False)  # SHA256
    signed_url = Column(Text)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Export {self.filename}>"

class Observation(Base):
    """Citizen science observation"""
    __tablename__ = "observations"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, nullable=False)
    observer_id = Column(Integer, nullable=True)
    observation_time = Column(DateTime(timezone=True), nullable=False)
    method = Column(String(50))  # shadow, alignment, transit, etc.
    sun_altitude_measured = Column(Float)
    sun_azimuth_measured = Column(Float)
    sun_altitude_predicted = Column(Float)
    sun_azimuth_predicted = Column(Float)
    error_altitude = Column(Float)
    error_azimuth = Column(Float)
    photo_url = Column(String(500))
    notes = Column(Text)
    status = Column(SQLEnum(ObservationStatus), default=ObservationStatus.PENDING)
    reviewed_by = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Observation {self.id} at {self.observation_time}>"

class Lesson(Base):
    """Educational lesson content"""
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True)
    language = Column(String(10), default="en")
    content = Column(Text, nullable=False)  # Markdown
    yantra_type = Column(SQLEnum(YantraTypeEnum), nullable=True)
    difficulty_level = Column(Integer, default=1)  # 1-5
    tags = Column(JSON)  # Array of tags
    author_id = Column(Integer, nullable=True)
    is_published = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Lesson {self.title}>"

class Leaderboard(Base):
    """User achievements and scores"""
    __tablename__ = "leaderboard"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    total_observations = Column(Integer, default=0)
    accurate_observations = Column(Integer, default=0)
    yantras_generated = Column(Integer, default=0)
    contributions_approved = Column(Integer, default=0)
    score = Column(Integer, default=0)
    badges = Column(JSON)  # Array of badge IDs
    rank = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Leaderboard user={self.user_id} score={self.score}>"

class ModerationQueue(Base):
    """Content moderation queue"""
    __tablename__ = "moderation_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_type = Column(String(50), nullable=False)  # observation, lesson, photo
    submission_id = Column(Integer, nullable=False)
    submitter_id = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")
    reviewer_id = Column(Integer, nullable=True)
    review_notes = Column(Text)
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Moderation {self.submission_type} {self.submission_id}>"

# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

# Helper functions
def create_test_data(db: Session):
    """Create test data for development"""
    # Test site: Jaipur Jantar Mantar
    test_site = Site(
        name="Jaipur Jantar Mantar",
        latitude=26.9124,
        longitude=75.7873,
        elevation=431,
        timezone="Asia/Kolkata",
        magnetic_declination=1.2,
        is_public=True,
        description="Historic observatory in Jaipur, Rajasthan"
    )
    db.add(test_site)
    db.commit()
    
    print("✅ Test data created")