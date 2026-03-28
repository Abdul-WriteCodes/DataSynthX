import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Text, Integer,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.db.session import Base


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    row_count = Column(Integer)
    column_count = Column(Integer)
    columns = Column(JSON)         # list of column names
    entity_col = Column(String)    # e.g. "Company"
    time_col = Column(String)      # e.g. "Year"
    created_at = Column(DateTime, default=datetime.utcnow)

    analyses = relationship("Analysis", back_populates="dataset", cascade="all, delete")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    title = Column(String, nullable=False)
    dependent_var = Column(String, nullable=False)
    independent_vars = Column(JSON, nullable=False)   # list of strings
    control_vars = Column(JSON, default=list)
    models = Column(JSON, nullable=False)              # ["FE", "RE", "POLS", "BE"]
    diagnostics = Column(JSON, default=list)

    status = Column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    celery_task_id = Column(String, nullable=True)

    # Results stored as JSON blobs
    descriptive_stats = Column(JSON, nullable=True)
    correlation_matrix = Column(JSON, nullable=True)
    regression_results = Column(JSON, nullable=True)
    diagnostic_results = Column(JSON, nullable=True)
    llm_narrative = Column(Text, nullable=True)

    report_path = Column(String, nullable=True)       # Supabase storage path
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    dataset = relationship("Dataset", back_populates="analyses")
