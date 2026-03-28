"""
analysis_tasks.py
Celery task: downloads dataset, runs full analysis,
generates Word report, uploads to Supabase, updates DB.
"""

import io
import uuid
import pandas as pd
from datetime import datetime
from celery import shared_task
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.models import Analysis, AnalysisStatus
from app.integrations.supabase_client import (
    download_file_from_storage,
    upload_file_to_storage,
)
from app.services.analysis_service import run_full_analysis
from app.services.llm_service import generate_narrative
from app.services.report_service import build_word_report
from app.core.config import settings


def _get_db() -> Session:
    return SessionLocal()


@celery_app.task(bind=True, name="app.workers.analysis_tasks.run_panel_analysis",
                 max_retries=2, default_retry_delay=30)
def run_panel_analysis(self, analysis_id: str):
    """
    Full pipeline:
    1. Load analysis config from DB
    2. Download CSV from Supabase Storage
    3. Run statistical analysis
    4. Generate LLM narrative
    5. Build Word report
    6. Upload report to Supabase Storage
    7. Update DB record with results
    """
    db = _get_db()
    try:
        analysis: Analysis = db.query(Analysis).filter(
            Analysis.id == analysis_id
        ).first()

        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")

        # Mark as running
        analysis.status = AnalysisStatus.RUNNING
        analysis.celery_task_id = self.request.id
        db.commit()

        # 1. Download dataset
        dataset = analysis.dataset
        csv_bytes = download_file_from_storage(
            settings.SUPABASE_STORAGE_BUCKET,
            dataset.storage_path,
        )
        df = pd.read_csv(io.BytesIO(csv_bytes))

        # 2. Run analysis
        results = run_full_analysis(
            df=df,
            entity_col=dataset.entity_col,
            time_col=dataset.time_col,
            dependent_var=analysis.dependent_var,
            independent_vars=analysis.independent_vars,
            models=analysis.models,
            diagnostics=analysis.diagnostics,
        )

        analysis.descriptive_stats = results["descriptive_stats"]
        analysis.correlation_matrix = results["correlation_matrix"]
        analysis.regression_results = results["regression_results"]
        analysis.diagnostic_results = results["diagnostic_results"]
        db.commit()

        # 3. LLM narrative
        narrative = generate_narrative(
            analysis_title=analysis.title,
            dependent_var=analysis.dependent_var,
            independent_vars=analysis.independent_vars,
            descriptive_stats=results["descriptive_stats"],
            correlation_matrix=results["correlation_matrix"],
            regression_results=results["regression_results"],
            diagnostic_results=results["diagnostic_results"],
        )
        analysis.llm_narrative = narrative
        db.commit()

        # 4. Build Word report
        report_bytes = build_word_report(
            title=analysis.title,
            dependent_var=analysis.dependent_var,
            independent_vars=analysis.independent_vars,
            descriptive_stats=results["descriptive_stats"],
            correlation_matrix=results["correlation_matrix"],
            regression_results=results["regression_results"],
            diagnostic_results=results["diagnostic_results"],
            llm_narrative=narrative,
        )

        # 5. Upload report
        report_filename = f"reports/{analysis.user_id}/{analysis_id}.docx"
        upload_file_to_storage(
            bucket=settings.REPORT_STORAGE_BUCKET,
            path=report_filename,
            file_bytes=report_bytes,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        analysis.report_path = report_filename

        # 6. Mark complete
        analysis.status = AnalysisStatus.COMPLETED
        analysis.completed_at = datetime.utcnow()
        db.commit()

        return {"status": "completed", "analysis_id": analysis_id}

    except Exception as exc:
        if db:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.status = AnalysisStatus.FAILED
                analysis.error_message = str(exc)
                db.commit()
        raise self.retry(exc=exc)
    finally:
        db.close()
