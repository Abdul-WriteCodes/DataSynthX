from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Analysis
from app.core.security import get_current_user
from app.core.celery_app import celery_app

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Poll Celery task status. Frontend polls this every few seconds."""
    result = celery_app.AsyncResult(task_id)

    # Also look up the DB analysis to return richer state
    analysis = db.query(Analysis).filter(
        Analysis.celery_task_id == task_id,
        Analysis.user_id == current_user["user_id"],
    ).first()

    return {
        "task_id": task_id,
        "celery_state": result.state,
        "analysis_id": str(analysis.id) if analysis else None,
        "analysis_status": analysis.status.value if analysis else None,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else None,
        "error": str(result.result) if result.failed() else None,
    }
