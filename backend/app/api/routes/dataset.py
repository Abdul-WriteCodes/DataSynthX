import uuid
import io
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Dataset
from app.core.security import get_current_user
from app.integrations.supabase_client import upload_file_to_storage, delete_file_from_storage
from app.core.config import settings

router = APIRouter(prefix="/api/datasets", tags=["datasets"])

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", status_code=201)
async def upload_dataset(
    file: UploadFile = File(...),
    entity_col: str = Form(...),
    time_col: str = Form(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate extension
    filename = file.filename or ""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 20 MB limit.")

    # Parse to validate and extract metadata
    try:
        if ext == ".csv":
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse file. Ensure it is valid.")

    if entity_col not in df.columns:
        raise HTTPException(status_code=400, detail=f"Entity column '{entity_col}' not found.")
    if time_col not in df.columns:
        raise HTTPException(status_code=400, detail=f"Time column '{time_col}' not found.")

    # Upload to Supabase Storage
    dataset_id = str(uuid.uuid4())
    storage_path = f"datasets/{current_user['user_id']}/{dataset_id}{ext}"
    upload_file_to_storage(
        bucket=settings.SUPABASE_STORAGE_BUCKET,
        path=storage_path,
        file_bytes=content,
        content_type=file.content_type or "text/csv",
    )

    # Save metadata to DB
    dataset = Dataset(
        id=uuid.UUID(dataset_id),
        user_id=current_user["user_id"],
        filename=filename,
        storage_path=storage_path,
        row_count=len(df),
        column_count=len(df.columns),
        columns=list(df.columns),
        entity_col=entity_col,
        time_col=time_col,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return {
        "dataset_id": str(dataset.id),
        "filename": filename,
        "rows": len(df),
        "columns": list(df.columns),
        "entity_col": entity_col,
        "time_col": time_col,
    }


@router.get("/")
async def list_datasets(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    datasets = db.query(Dataset).filter(
        Dataset.user_id == current_user["user_id"]
    ).order_by(Dataset.created_at.desc()).all()

    return [
        {
            "id": str(d.id),
            "filename": d.filename,
            "rows": d.row_count,
            "columns": d.columns,
            "entity_col": d.entity_col,
            "time_col": d.time_col,
            "created_at": d.created_at.isoformat(),
        }
        for d in datasets
    ]


@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == current_user["user_id"],
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return {
        "id": str(dataset.id),
        "filename": dataset.filename,
        "rows": dataset.row_count,
        "columns": dataset.columns,
        "entity_col": dataset.entity_col,
        "time_col": dataset.time_col,
        "created_at": dataset.created_at.isoformat(),
    }


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(
    dataset_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == current_user["user_id"],
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        delete_file_from_storage(settings.SUPABASE_STORAGE_BUCKET, dataset.storage_path)
    except Exception:
        pass

    db.delete(dataset)
    db.commit()
