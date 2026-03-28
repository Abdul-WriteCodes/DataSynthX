from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, dataset, analysis, task
from app.db.session import engine
from app.db import models

# Create all tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PanelStat API",
    description="Panel data regression analysis SaaS platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dataset.router)
app.include_router(analysis.router)
app.include_router(task.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "PanelStat API"}
