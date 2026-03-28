import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import io

from app.db.session import get_db
from app.db.models import Analysis, Dataset, AnalysisStatus
from app.core.security import get_current_user
from app.workers.analysis_tasks import run_panel_analysis
from app.integrations.supabase_client import download_file_from_storage
from app.core.config import settings

router = APIRouter(prefix="/api/analyses", tags=["analyses"])

VALID_MODELS = {"FE", "RE", "POLS", "BE"}
VALID_DIAGNOSTICS = {"HAUSMAN", "BP", "VIF", "WOOLDRIDGE"}


class CreateAnalysisRequest(BaseModel):
    dataset_id: str
    title: str
    dependent_var: str
    independent_vars: list[str]
    control_vars: list[str] = []
    models: list[str]
    diagnostics: list[str] = []


@router.post("/", status_code=201)
async def create_analysis(
    body: CreateAnalysisRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate models and diagnostics
    invalid_models = set(body.models) - VALID_MODELS
    if invalid_models:
        raise HTTPException(status_code=400, detail=f"Invalid models: {invalid_models}")

    invalid_diag = set(body.diagnostics) - VALID_DIAGNOSTICS
    if invalid_diag:
        raise HTTPException(status_code=400, detail=f"Invalid diagnostics: {invalid_diag}")

    # Verify dataset ownership
    dataset = db.query(Dataset).filter(
        Dataset.id == body.dataset_id,
        Dataset.user_id == current_user["user_id"],
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Validate variables exist in dataset
    all_req_vars = [body.dependent_var] + body.independent_vars + body.control_vars
    missing = [v for v in all_req_vars if v not in (dataset.columns or [])]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Variables not found in dataset: {missing}"
        )

    # Hausman requires both FE and RE
    if "HAUSMAN" in body.diagnostics and not ({"FE", "RE"} <= set(body.models)):
        raise HTTPException(
            status_code=400,
            detail="Hausman test requires both Fixed Effects and Random Effects models."
        )

    analysis_id = uuid.uuid4()
    analysis = Analysis(
        id=analysis_id,
        user_id=current_user["user_id"],
        dataset_id=uuid.UUID(body.dataset_id),
        title=body.title,
        dependent_var=body.dependent_var,
        independent_vars=body.independent_vars + body.control_vars,
        control_vars=body.control_vars,
        models=body.models,
        diagnostics=body.diagnostics,
        status=AnalysisStatus.PENDING,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Dispatch Celery task
    task = run_panel_analysis.apply_async(
        args=[str(analysis_id)],
        queue="analysis",
    )
    analysis.celery_task_id = task.id
    db.commit()

    return {
        "analysis_id": str(analysis_id),
        "status": "pending",
        "task_id": task.id,
        "message": "Analysis queued. Poll /api/analyses/{id} for status.",
    }


@router.get("/")
async def list_analyses(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analyses = db.query(Analysis).filter(
        Analysis.user_id == current_user["user_id"]
    ).order_by(Analysis.created_at.desc()).all()

    return [_serialize_analysis(a, include_results=False) for a in analyses]


@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = _get_owned_analysis(analysis_id, current_user, db)
    return _serialize_analysis(analysis, include_results=True)


@router.get("/{analysis_id}/download")
async def download_report(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = _get_owned_analysis(analysis_id, current_user, db)

    if analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Report not ready yet.")
    if not analysis.report_path:
        raise HTTPException(status_code=404, detail="Report file not found.")

    try:
        report_bytes = download_file_from_storage(
            settings.REPORT_STORAGE_BUCKET,
            analysis.report_path,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Could not retrieve report file.")

    safe_title = "".join(c for c in analysis.title if c.isalnum() or c in " _-")[:50]
    filename = f"{safe_title}_panel_report.docx"

    return StreamingResponse(
        io.BytesIO(report_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{analysis_id}", status_code=204)
async def delete_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = _get_owned_analysis(analysis_id, current_user, db)
    db.delete(analysis)
    db.commit()


# ── Helpers ──

def _get_owned_analysis(analysis_id: str, current_user: dict, db: Session) -> Analysis:
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user["user_id"],
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


def _serialize_analysis(analysis: Analysis, include_results: bool) -> dict:
    base = {
        "id": str(analysis.id),
        "title": analysis.title,
        "dataset_id": str(analysis.dataset_id),
        "dependent_var": analysis.dependent_var,
        "independent_vars": analysis.independent_vars,
        "models": analysis.models,
        "diagnostics": analysis.diagnostics,
        "status": analysis.status.value,
        "created_at": analysis.created_at.isoformat(),
        "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
        "has_report": analysis.report_path is not None,
        "error": analysis.error_message,
    }
    if include_results:
        base.update({
            "descriptive_stats": analysis.descriptive_stats,
            "correlation_matrix": analysis.correlation_matrix,
            "regression_results": analysis.regression_results,
            "diagnostic_results": analysis.diagnostic_results,
            "llm_narrative": analysis.llm_narrative,
        })
    return base
