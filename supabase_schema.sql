-- ============================================================
-- PanelStat — Supabase SQL Schema
-- Run this in your Supabase project → SQL Editor
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Datasets ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS datasets (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id       TEXT NOT NULL,
    filename      TEXT NOT NULL,
    storage_path  TEXT NOT NULL,
    row_count     INTEGER,
    column_count  INTEGER,
    columns       JSONB,
    entity_col    TEXT,
    time_col      TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_datasets_user_id ON datasets(user_id);

-- ── Analyses ─────────────────────────────────────────────────
CREATE TYPE analysis_status AS ENUM ('pending', 'running', 'completed', 'failed');

CREATE TABLE IF NOT EXISTS analyses (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             TEXT NOT NULL,
    dataset_id          UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    title               TEXT NOT NULL,
    dependent_var       TEXT NOT NULL,
    independent_vars    JSONB NOT NULL,
    control_vars        JSONB DEFAULT '[]',
    models              JSONB NOT NULL,
    diagnostics         JSONB DEFAULT '[]',
    status              analysis_status DEFAULT 'pending',
    celery_task_id      TEXT,
    descriptive_stats   JSONB,
    correlation_matrix  JSONB,
    regression_results  JSONB,
    diagnostic_results  JSONB,
    llm_narrative       TEXT,
    report_path         TEXT,
    error_message       TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    completed_at        TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_analyses_user_id    ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_dataset_id ON analyses(dataset_id);
CREATE INDEX IF NOT EXISTS idx_analyses_status     ON analyses(status);

-- ── Row Level Security ────────────────────────────────────────
ALTER TABLE datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;

-- Users can only see their own datasets
CREATE POLICY "Users see own datasets"
    ON datasets FOR ALL
    USING (user_id = auth.uid()::text);

-- Users can only see their own analyses
CREATE POLICY "Users see own analyses"
    ON analyses FOR ALL
    USING (user_id = auth.uid()::text);

-- ── Storage Buckets ───────────────────────────────────────────
-- Run these in Supabase Dashboard → Storage → New bucket
-- Or via the Supabase CLI:
--
--   supabase storage create panel-datasets --public false
--   supabase storage create panel-reports  --public false
--
-- The backend uses the service role key and bypasses RLS on storage.
