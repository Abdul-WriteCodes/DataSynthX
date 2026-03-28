# PanelStat — Panel Data Regression SaaS

A no-code web platform for panel data regression analysis.
Upload a dataset, configure variables and models, run the analysis,
and download a fully formatted Word report with AI-written discussion.

---

## Features

- **Descriptive statistics** — N, mean, SD, min/max, skewness, kurtosis
- **Pearson correlation matrix** with significance stars
- **Panel regression models**: Fixed Effects, Random Effects, Pooled OLS, Between Effects
- **Full regression table**: β, Std. Error, t-stat, p-value, LCL, UCL, significance stars
- **Diagnostic tests**: Hausman, Breusch-Pagan, VIF, Wooldridge serial correlation
- **AI-written narrative** via OpenAI GPT-4o
- **Word (.docx) report export** — formatted for academic submission
- **Async processing** via Celery + Redis — analysis runs in background
- **Auth** via Supabase — email/password login
- **Storage** via Supabase Storage — datasets and reports

---

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | FastAPI + Uvicorn                   |
| Worker    | Celery + Redis                      |
| Database  | Supabase (PostgreSQL)               |
| Storage   | Supabase Storage                    |
| Auth      | Supabase Auth + JWT                 |
| Stats     | statsmodels, linearmodels, scipy    |
| AI        | OpenAI GPT-4o                       |
| Reports   | python-docx                         |
| Frontend  | Next.js 14 + Tailwind CSS           |

---

## Project Structure

```
panelSaaSx/
├── backend/
│   ├── .env                        ← Copy and fill in your secrets
│   ├── requirements.txt
│   └── app/
│       ├── main.py                 ← FastAPI entry point
│       ├── core/
│       │   ├── config.py           ← Settings from .env
│       │   ├── celery_app.py       ← Celery configuration
│       │   └── security.py        ← JWT auth
│       ├── db/
│       │   ├── models.py           ← SQLAlchemy ORM models
│       │   └── session.py          ← DB engine
│       ├── integrations/
│       │   └── supabase_client.py ← Storage upload/download
│       ├── api/routes/
│       │   ├── auth.py             ← Register, login, logout
│       │   ├── dataset.py          ← Upload CSV/Excel
│       │   ├── analysis.py        ← Create, list, get, download
│       │   └── task.py             ← Celery task status poll
│       ├── services/
│       │   ├── analysis_service.py ← ALL statistical computations
│       │   ├── llm_service.py     ← OpenAI narrative generation
│       │   └── report_service.py  ← Word document builder
│       └── workers/
│           └── analysis_tasks.py  ← Celery pipeline task
├── frontend/
│   ├── app/
│   │   ├── page.tsx               ← Redirect to dashboard/login
│   │   ├── layout.tsx
│   │   ├── dashboard/             ← Analysis list
│   │   ├── upload/                ← 3-step upload + configure
│   │   ├── analysis/[id]/         ← Results viewer + download
│   │   ├── auth/login/
│   │   ├── auth/signup/
│   │   └── settings/
│   ├── components/
│   │   ├── AuthGuard.tsx
│   │   ├── Sidebar.tsx
│   │   ├── AnalysisCard.tsx
│   │   └── UploadBox.tsx
│   └── lib/
│       ├── api.ts                 ← Axios client + all API calls
│       ├── auth.ts                ← Token storage helpers
│       └── supabaseClient.ts
└── supabase_schema.sql            ← Run in Supabase SQL editor
```

---

## Setup Instructions

### 1. Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** → paste and run `supabase_schema.sql`
3. Go to **Storage** → create two buckets:
   - `panel-datasets` (private)
   - `panel-reports` (private)
4. Note your **Project URL**, **anon key**, and **service role key**

### 2. Redis

Install and start Redis locally:

```bash
# macOS
brew install redis && brew services start redis

# Ubuntu/Debian
sudo apt install redis-server && sudo systemctl start redis
```

### 3. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env .env.local
# Edit .env and fill in all values

# Run database migrations (creates tables via SQLAlchemy)
# Tables are auto-created on first startup

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# In a separate terminal — start Celery worker
celery -A app.core.celery_app worker --loglevel=info -Q analysis
```

### 4. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local .env.local
# Edit .env.local — set NEXT_PUBLIC_API_URL, SUPABASE_URL, SUPABASE_ANON_KEY

# Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## Environment Variables

### Backend (`backend/.env`)

| Variable                  | Description                          |
|---------------------------|--------------------------------------|
| `SECRET_KEY`              | JWT signing secret (change in prod)  |
| `SUPABASE_URL`            | Your Supabase project URL            |
| `SUPABASE_ANON_KEY`       | Supabase anon/public key             |
| `SUPABASE_SERVICE_KEY`    | Supabase service role key            |
| `DATABASE_URL`            | PostgreSQL connection string         |
| `REDIS_URL`               | Redis connection URL                 |
| `CELERY_BROKER_URL`       | Redis URL for Celery broker          |
| `CELERY_RESULT_BACKEND`   | Redis URL for Celery results         |
| `OPENAI_API_KEY`          | Your OpenAI API key                  |
| `FRONTEND_URL`            | Frontend origin for CORS             |

### Frontend (`frontend/.env.local`)

| Variable                        | Description              |
|---------------------------------|--------------------------|
| `NEXT_PUBLIC_API_URL`           | Backend URL              |
| `NEXT_PUBLIC_SUPABASE_URL`      | Supabase project URL     |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key        |

---

## API Reference

| Method | Endpoint                         | Description                     |
|--------|----------------------------------|---------------------------------|
| POST   | `/api/auth/register`             | Register new user               |
| POST   | `/api/auth/login`                | Login, returns JWT              |
| POST   | `/api/datasets/upload`           | Upload CSV/Excel dataset        |
| GET    | `/api/datasets/`                 | List user datasets              |
| POST   | `/api/analyses/`                 | Create and queue analysis       |
| GET    | `/api/analyses/`                 | List user analyses              |
| GET    | `/api/analyses/{id}`             | Get analysis + results          |
| GET    | `/api/analyses/{id}/download`    | Download Word report            |
| GET    | `/api/tasks/{task_id}`           | Poll Celery task status         |

---

## Word Report Structure

The exported `.docx` includes:

1. **Cover page** — title, variables, date
2. **Descriptive statistics** — formatted table
3. **Pearson correlation matrix** — with significance stars
4. **Regression results** — one table per model (FE/RE/POLS/BE)
   - β, Std. Error, t-stat, p-value, Sig. stars, LCL, UCL
   - Model fit statistics (R², F-stat, N, entities, periods)
5. **Diagnostic tests** — summary table + VIF detail
6. **AI-written discussion** — GPT-4o academic narrative

---

## Significance Conventions

| Stars | p-value threshold |
|-------|-------------------|
| ***   | p < 0.01          |
| **    | p < 0.05          |
| *     | p < 0.10          |

---

## Notes

- The Hausman test requires both Fixed Effects and Random Effects to be selected
- Robust standard errors are used by default for FE and Pooled OLS
- Missing values (NaN) in the dataset are dropped row-wise before analysis
- The Wooldridge test requires at least 3 time periods per entity
- Analysis runs asynchronously — the frontend polls every 5 seconds for status
