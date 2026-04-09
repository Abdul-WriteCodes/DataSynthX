import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ks_2samp, wasserstein_distance
import io
import warnings
warnings.filterwarnings('ignore')

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataSynthX",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface2: #1a1a24;
    --border: #2a2a3a;
    --accent: #7c6af7;
    --accent2: #3ecfcf;
    --accent3: #f76a6a;
    --text: #e8e8f0;
    --muted: #6b6b80;
}

html, body, [class*="css"] {
    background-color: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
}

.stApp { background: var(--bg); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Header */
.brand-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
}
.brand-logo {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}
.brand-name {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.brand-tag {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: -4px;
}

/* Cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 32px;
    font-weight: 800;
    line-height: 1;
}
.metric-sub {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    margin-top: 4px;
}

/* Score gauge */
.sci-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px;
    text-align: center;
}
.sci-ring {
    width: 160px; height: 160px;
    margin: 0 auto 16px;
    position: relative;
}
.sci-score {
    font-size: 48px;
    font-weight: 800;
    line-height: 1;
}
.sci-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 3px;
    color: var(--muted);
    text-transform: uppercase;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    letter-spacing: 1px;
    padding: 8px 20px;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent), #6055d4) !important;
    color: white !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #6055d4);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 28px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.5px;
    width: 100%;
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(124, 106, 247, 0.35);
}

/* Download button */
.stDownloadButton > button {
    background: var(--surface2);
    color: var(--accent2);
    border: 1px solid var(--accent2);
    border-radius: 10px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    width: 100%;
}

/* Inputs */
.stNumberInput input, .stSlider, .stSelectbox select {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* File uploader */
.stFileUploader {
    background: var(--surface);
    border: 2px dashed var(--border);
    border-radius: 12px;
    padding: 20px;
}

/* Section headers */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
    margin-left: 8px;
}
.section-sub {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 16px;
}

/* Status badge */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-green { background: rgba(62,207,207,0.1); color: var(--accent2); border: 1px solid rgba(62,207,207,0.3); }
.badge-purple { background: rgba(124,106,247,0.1); color: var(--accent); border: 1px solid rgba(124,106,247,0.3); }
.badge-red { background: rgba(247,106,106,0.1); color: var(--accent3); border: 1px solid rgba(247,106,106,0.3); }

/* Tables */
.stDataFrame { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
thead th { background: var(--surface2) !important; }

/* Progress bar */
.stProgress > div > div { background: linear-gradient(90deg, var(--accent), var(--accent2)); border-radius: 4px; }

/* Dividers */
hr { border-color: var(--border); }

/* Plotly charts */
.js-plotly-plot .plotly { background: transparent !important; }

/* Hide Streamlit branding — keep sidebar toggle visible */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
/* Only hide the Deploy/toolbar portion of the header, NOT the whole header
   so the sidebar collapse «« button remains functional */
header[data-testid="stHeader"] {
    background: transparent !important;
}
header[data-testid="stHeader"]::before {
    display: none;
}
/* Hide only the toolbar items (Deploy button etc.), not the collapse button */
div[data-testid="stToolbar"] {
    opacity: 0;
    pointer-events: none;
}
div[data-testid="collapsedControl"] { color: var(--text) !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  CORE ENGINES
# ═══════════════════════════════════════════════════════════════════════════

class DataProfiler:
    """Compute statistical profile of uploaded dataset."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        # Try to parse datetime columns
        self.datetime_cols = []
        for col in self.categorical_cols[:]:
            try:
                parsed = pd.to_datetime(df[col], infer_datetime_format=True, errors='coerce')
                if parsed.notna().sum() > len(df) * 0.7:
                    self.datetime_cols.append(col)
                    self.categorical_cols.remove(col)
            except Exception:
                pass

    def profile(self) -> dict:
        p = {}
        # Numeric stats
        p['numeric_stats'] = {}
        for col in self.numeric_cols:
            s = self.df[col].dropna()
            p['numeric_stats'][col] = {
                'mean': float(s.mean()),
                'std': float(s.std()),
                'variance': float(s.var()),
                'min': float(s.min()),
                'max': float(s.max()),
                'skew': float(s.skew()),
                'kurtosis': float(s.kurtosis()),
                'missing_ratio': float(self.df[col].isna().mean()),
                'values': s.values
            }

        # Categorical stats
        p['categorical_stats'] = {}
        for col in self.categorical_cols:
            s = self.df[col].dropna()
            freq = s.value_counts(normalize=True)
            p['categorical_stats'][col] = {
                'frequencies': freq.to_dict(),
                'n_unique': int(s.nunique()),
                'missing_ratio': float(self.df[col].isna().mean()),
                'mode': str(s.mode().iloc[0]) if len(s) > 0 else None
            }

        # Correlation matrix
        if len(self.numeric_cols) >= 2:
            p['correlation_matrix'] = self.df[self.numeric_cols].corr().fillna(0)
        else:
            p['correlation_matrix'] = pd.DataFrame()

        p['shape'] = self.df.shape
        p['numeric_cols'] = self.numeric_cols
        p['categorical_cols'] = self.categorical_cols
        p['datetime_cols'] = self.datetime_cols
        p['missing_overview'] = self.df.isna().mean().to_dict()

        return p


class SyntheticDataGenerator:
    """Generate synthetic data preserving statistical structure."""

    def __init__(self, df: pd.DataFrame, profile: dict):
        self.df = df
        self.profile = profile
        self.numeric_cols = profile['numeric_cols']
        self.categorical_cols = profile['categorical_cols']

    def generate(self, n_rows: int, noise_level: float = 0.02) -> pd.DataFrame:
        synthetic = {}

        # ── Numeric: Multivariate Gaussian ──────────────────────────────
        if self.numeric_cols:
            clean = self.df[self.numeric_cols].dropna()
            n_num = len(self.numeric_cols)
            if len(clean) >= 2:
                # Use fillna(0) + .copy() so NaN-heavy datasets don't produce
                # a read-only NaN matrix that crashes np.eye addition downstream.
                mean_vec = clean.mean().fillna(0).values
                cov_matrix = clean.cov().fillna(0).values.copy()
                # Ensure strictly 2-D square array before adding identity matrix.
                # Guards against: read-only arrays, scalar from single-column cov(),
                # and shape mismatches.
                cov_matrix = np.atleast_2d(cov_matrix).reshape(n_num, n_num)
                cov_matrix += np.eye(n_num) * 1e-8

                try:
                    samples = np.random.multivariate_normal(mean_vec, cov_matrix, n_rows)
                except (np.linalg.LinAlgError, ValueError):
                    # Fallback: independent per-column sampling (catches both
                    # LinAlgError from bad matrices AND ValueError from NaN cov)
                    samples = np.column_stack([
                        np.random.normal(
                            self.profile['numeric_stats'][c]['mean'],
                            max(self.profile['numeric_stats'][c]['std'], 1e-6),
                            n_rows
                        ) for c in self.numeric_cols
                    ])
                # Ensure samples is always 2-D (edge case: single column)
                samples = np.atleast_2d(samples).reshape(n_rows, n_num)

                # Add controlled noise
                noise = np.random.normal(0, noise_level, samples.shape)
                noise *= np.std(samples, axis=0, keepdims=True)
                samples = samples + noise

                # Clip to [min, max] of original
                for i, col in enumerate(self.numeric_cols):
                    stats_c = self.profile['numeric_stats'][col]
                    col_range = stats_c['max'] - stats_c['min']
                    lo = stats_c['min'] - col_range * 0.05
                    hi = stats_c['max'] + col_range * 0.05
                    samples[:, i] = np.clip(samples[:, i], lo, hi)

                    # Preserve integer dtype if original was integer
                    orig_dtype = self.df[col].dtype
                    if np.issubdtype(orig_dtype, np.integer):
                        synthetic[col] = np.round(samples[:, i]).astype(int)
                    else:
                        synthetic[col] = samples[:, i]
            else:
                # Too few rows — independent sampling
                for col in self.numeric_cols:
                    s = self.profile['numeric_stats'][col]
                    synthetic[col] = np.random.normal(s['mean'], max(s['std'], 1e-6), n_rows)

        # ── Categorical: Frequency-preserving sampling ───────────────────
        for col in self.categorical_cols:
            cat_stats = self.profile['categorical_stats'][col]
            categories = list(cat_stats['frequencies'].keys())
            probs = list(cat_stats['frequencies'].values())
            # Normalize probs
            probs = np.array(probs, dtype=float)
            probs /= probs.sum()
            synthetic[col] = np.random.choice(categories, size=n_rows, p=probs)

        # ── Inject missing values proportionally ────────────────────────
        for col in self.numeric_cols + self.categorical_cols:
            missing_ratio = self.profile['missing_overview'].get(col, 0)
            if missing_ratio > 0:
                mask = np.random.rand(n_rows) < missing_ratio
                synth_series = pd.Series(synthetic[col])
                synth_series[mask] = np.nan
                synthetic[col] = synth_series.values

        synth_df = pd.DataFrame(synthetic)
        # Restore original column order where possible
        orig_cols = [c for c in self.df.columns if c in synth_df.columns]
        return synth_df[orig_cols]


class TrustMetrics:
    """Compute trust / fidelity metrics between original and synthetic data."""

    def __init__(self, original: pd.DataFrame, synthetic: pd.DataFrame, profile: dict):
        self.orig = original
        self.synth = synthetic
        self.profile = profile
        self.numeric_cols = profile['numeric_cols']
        self.categorical_cols = profile['categorical_cols']

    def correlation_preservation_score(self) -> tuple[float, pd.DataFrame, pd.DataFrame]:
        if len(self.numeric_cols) < 2:
            return 1.0, pd.DataFrame(), pd.DataFrame()
        orig_corr = self.orig[self.numeric_cols].corr().fillna(0)
        synth_corr = self.synth[self.numeric_cols].corr().fillna(0)
        diff = np.abs(orig_corr.values - synth_corr.values)
        score = max(0.0, 1.0 - diff.mean())
        return float(score), orig_corr, synth_corr

    def distribution_similarity_scores(self) -> dict:
        scores = {}
        for col in self.numeric_cols:
            a = self.orig[col].dropna().values
            b = self.synth[col].dropna().values
            if len(a) < 2 or len(b) < 2:
                scores[col] = {'ks_stat': 0, 'ks_pvalue': 1, 'wasserstein': 0, 'score': 1.0}
                continue
            ks_stat, ks_p = ks_2samp(a, b)
            # Normalize Wasserstein by std of original
            std_a = np.std(a)
            w_dist = wasserstein_distance(a, b) / (std_a + 1e-9)
            score = max(0.0, 1.0 - ks_stat)
            scores[col] = {
                'ks_stat': float(ks_stat),
                'ks_pvalue': float(ks_p),
                'wasserstein': float(w_dist),
                'score': float(score)
            }
        return scores

    def categorical_fidelity_scores(self) -> dict:
        scores = {}
        for col in self.categorical_cols:
            orig_freq = self.orig[col].value_counts(normalize=True)
            synth_freq = self.synth[col].value_counts(normalize=True)
            all_cats = set(orig_freq.index) | set(synth_freq.index)
            p = np.array([orig_freq.get(c, 1e-10) for c in all_cats])
            q = np.array([synth_freq.get(c, 1e-10) for c in all_cats])
            p /= p.sum(); q /= q.sum()
            # KL divergence (clipped)
            kl_div = float(np.sum(p * np.log((p + 1e-10) / (q + 1e-10))))
            kl_div = min(kl_div, 10.0)
            score = max(0.0, 1.0 - kl_div / 10.0)
            scores[col] = {
                'kl_divergence': kl_div,
                'score': float(score),
                'orig_freq': orig_freq.to_dict(),
                'synth_freq': synth_freq.to_dict()
            }
        return scores

    def compute_sci(self) -> dict:
        """Structural Consistency Index — weighted composite score 0–100."""
        corr_score, orig_corr, synth_corr = self.correlation_preservation_score()
        dist_scores = self.distribution_similarity_scores()
        cat_scores = self.categorical_fidelity_scores()

        avg_dist = np.mean([v['score'] for v in dist_scores.values()]) if dist_scores else 1.0
        avg_cat = np.mean([v['score'] for v in cat_scores.values()]) if cat_scores else 1.0

        # Weights
        w_corr, w_dist, w_cat = 0.30, 0.40, 0.30
        if not dist_scores: w_corr, w_dist, w_cat = 0.40, 0.0, 0.60
        if not cat_scores: w_corr, w_dist, w_cat = 0.35, 0.65, 0.0
        if not dist_scores and not cat_scores: w_corr, w_dist, w_cat = 1.0, 0.0, 0.0

        sci_raw = w_corr * corr_score + w_dist * avg_dist + w_cat * avg_cat
        sci = round(sci_raw * 100, 1)

        return {
            'sci': sci,
            'correlation_score': round(corr_score * 100, 1),
            'distribution_score': round(avg_dist * 100, 1),
            'categorical_score': round(avg_cat * 100, 1),
            'orig_corr': orig_corr,
            'synth_corr': synth_corr,
            'dist_scores': dist_scores,
            'cat_scores': cat_scores,
        }


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def score_color(score: float) -> str:
    if score >= 85: return "#3ecfcf"
    if score >= 65: return "#7c6af7"
    return "#f76a6a"

def score_badge(score: float) -> str:
    if score >= 85: return "badge-green", "EXCELLENT"
    if score >= 65: return "badge-purple", "GOOD"
    return "badge-red", "NEEDS REVIEW"

def make_heatmap_html(corr_df: pd.DataFrame, title: str) -> str:
    """Build a simple HTML heatmap without Plotly dependency issues."""
    import json
    cols = list(corr_df.columns)
    n = len(cols)
    if n == 0:
        return "<p style='color:#6b6b80;font-family:Space Mono,monospace;font-size:12px'>Not enough numeric columns for correlation.</p>"

    cell_size = max(40, min(80, 400 // n))
    total = cell_size * n + 100

    cells_html = ""
    for i, row in enumerate(cols):
        for j, col in enumerate(cols):
            val = corr_df.loc[row, col]
            # Color: negative=red, zero=dark, positive=teal/purple
            if val > 0:
                r, g, b = int(124 * val), int(106 * val), int(247 * val + 100 * (1 - val))
            else:
                r, g, b = int(247 * (-val)), int(106 * (-val)), int(106 * (-val))
            bg = f"rgb({r},{g},{b})"
            text_col = "white" if abs(val) > 0.3 else "#6b6b80"
            x = j * cell_size + 80
            y = i * cell_size + 40
            cells_html += f"""
            <rect x="{x}" y="{y}" width="{cell_size-2}" height="{cell_size-2}" rx="3" fill="{bg}" opacity="0.85"/>
            <text x="{x + cell_size//2 - 1}" y="{y + cell_size//2 + 5}" text-anchor="middle"
                  font-size="11" fill="{text_col}" font-family="Space Mono,monospace">{val:.2f}</text>
            """

    labels_x = "".join([
        f'<text x="{j * cell_size + 80 + cell_size//2 - 1}" y="32" text-anchor="middle" '
        f'font-size="11" fill="#6b6b80" font-family="Syne,sans-serif">{c[:8]}</text>'
        for j, c in enumerate(cols)
    ])
    labels_y = "".join([
        f'<text x="74" y="{i * cell_size + 40 + cell_size//2 + 4}" text-anchor="end" '
        f'font-size="11" fill="#6b6b80" font-family="Syne,sans-serif">{c[:8]}</text>'
        for i, c in enumerate(cols)
    ])

    return f"""
    <div style="background:#111118;border:1px solid #2a2a3a;border-radius:12px;padding:16px;margin-bottom:8px;">
        <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">{title}</div>
        <svg width="{total}" height="{total}" style="max-width:100%">
            {labels_x}{labels_y}{cells_html}
        </svg>
    </div>"""


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='SyntheticData')
        wb = writer.book
        ws = writer.sheets['SyntheticData']
        header_fmt = wb.add_format({'bold': True, 'bg_color': '#1a1a24', 'font_color': '#7c6af7', 'border': 1})
        for ci, col in enumerate(df.columns):
            ws.write(0, ci, col, header_fmt)
            ws.set_column(ci, ci, max(12, len(str(col)) + 4))
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div class="brand-header">
        <div class="brand-logo"></div>
        <div>
            <div class="brand-name">DataSynthX</div>
            <div class="brand-tag">Synthetic Data Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">⬆ Upload Dataset</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "CSV or Excel",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown('<div class="section-title">⚙ Generation Config</div>', unsafe_allow_html=True)

    n_rows = st.number_input(
        "Target rows to generate",
        min_value=10,
        max_value=1_000_000,
        value=1000,
        step=100,
        help="Number of synthetic rows to generate"
    )

    noise_level = st.slider(
        "Noise level",
        min_value=0.0,
        max_value=0.20,
        value=0.02,
        step=0.01,
        help="Gaussian noise added to numeric columns (fraction of std)"
    )

    st.markdown("---")
    generate_btn = st.button("⬡ Generate Synthetic Data", type="primary")

    st.markdown("---")
    st.markdown("""
    <div style="font-family:Space Mono,monospace;font-size:10px;color:#3a3a4a;letter-spacing:1px;text-transform:uppercase;line-height:2;">
        v1.0.0 · DataSynthX<br>
        Multivariate Gaussian<br>
        Freq-Preserving Sampling<br>
        KS · Wasserstein · KL
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════

# Hero header
st.markdown("""
<div style="padding: 40px 0 24px;">
    <div style="font-family:Space Mono,monospace;font-size:10px;color:#3ecfcf;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">
        AI-POWERED · STATISTICAL FIDELITY · PRODUCTION READY
    </div>
    <h1 style="font-family:Syne,sans-serif;font-size:42px;font-weight:800;margin:0;line-height:1.1;
               background:linear-gradient(90deg,#e8e8f0,#7c6af7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        Synthetic Data<br>Generation Platform
    </h1>
    <p style="color:#6b6b80;font-size:15px;margin-top:12px;font-family:Syne,sans-serif;">
        Upload your dataset → Learn its structure → Generate privacy-safe synthetic data at any scale
    </p>
</div>
""", unsafe_allow_html=True)

if uploaded_file is None:
    # Empty state
    st.markdown("""
    <div style="border:2px dashed #2a2a3a;border-radius:16px;padding:60px;text-align:center;margin-top:20px;">
        <div style="font-size:48px;margin-bottom:16px;">⬡</div>
        <div style="font-family:Syne,sans-serif;font-size:20px;font-weight:700;color:#e8e8f0;margin-bottom:8px;">
            No Dataset Loaded
        </div>
        <div style="font-family:Space Mono,monospace;font-size:12px;color:#6b6b80;line-height:1.8;">
            Upload a CSV or Excel file in the sidebar to begin.<br>
            DataSynthX will profile your data and generate<br>
            statistically faithful synthetic records at any scale.
        </div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:32px;">
        <div class="metric-card">
            <div class="metric-label">Step 01</div>
            <div style="font-size:20px;font-weight:700;color:#7c6af7;margin:8px 0;">Upload & Profile</div>
            <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;line-height:1.7;">
                Auto-detects numeric, categorical & datetime columns. Computes distributions, correlations and missing value ratios.
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Step 02</div>
            <div style="font-size:20px;font-weight:700;color:#3ecfcf;margin:8px 0;">Generate at Scale</div>
            <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;line-height:1.7;">
                Multivariate Gaussian synthesis preserves correlations. Frequency-weighted categorical sampling. Up to 1M rows.
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Step 03</div>
            <div style="font-size:20px;font-weight:700;color:#f76a6a;margin:8px 0;">Trust Metrics</div>
            <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;line-height:1.7;">
                KS-test, Wasserstein distance, KL divergence and a composite Structural Consistency Index (SCI) 0–100.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── Load Data ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"Failed to load file: {e}")
    st.stop()

# ─── Profile ────────────────────────────────────────────────────────────────
profiler = DataProfiler(df)
profile = profiler.profile()

numeric_cols = profile['numeric_cols']
categorical_cols = profile['categorical_cols']
datetime_cols = profile['datetime_cols']

# ─── Quick Stats Row ────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
cols_data = [
    (c1, str(df.shape[0]), "Original Rows", "#7c6af7"),
    (c2, str(df.shape[1]), "Total Columns", "#3ecfcf"),
    (c3, str(len(numeric_cols)), "Numeric Cols", "#7c6af7"),
    (c4, str(len(categorical_cols)), "Categorical Cols", "#3ecfcf"),
    (c5, f"{df.isna().mean().mean()*100:.1f}%", "Missing Rate", "#f76a6a"),
]
for col, val, label, color in cols_data:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color}">{val}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs(["📊  Data Profile", "🧬  Synthetic Data", "📐  Trust Metrics", "⬇  Export"])

# ──────────────────────────────────────────────────────────────────────────
# TAB 1: DATA PROFILE
# ──────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Original Dataset Preview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">First 100 rows of uploaded data</div>', unsafe_allow_html=True)
    st.dataframe(df.head(100), use_container_width=True, height=240)

    if numeric_cols:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Numeric Column Statistics</div>', unsafe_allow_html=True)
        stats_rows = []
        for col in numeric_cols:
            s = profile['numeric_stats'][col]
            stats_rows.append({
                'Column': col,
                'Mean': f"{s['mean']:.4f}",
                'Std Dev': f"{s['std']:.4f}",
                'Min': f"{s['min']:.4f}",
                'Max': f"{s['max']:.4f}",
                'Skewness': f"{s['skew']:.4f}",
                'Kurtosis': f"{s['kurtosis']:.4f}",
                'Missing %': f"{s['missing_ratio']*100:.1f}%"
            })
        st.dataframe(pd.DataFrame(stats_rows), use_container_width=True, hide_index=True)

    if categorical_cols:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Categorical Column Summary</div>', unsafe_allow_html=True)
        cat_rows = []
        for col in categorical_cols:
            s = profile['categorical_stats'][col]
            top = sorted(s['frequencies'].items(), key=lambda x: -x[1])[:3]
            cat_rows.append({
                'Column': col,
                'Unique Values': s['n_unique'],
                'Mode': s['mode'],
                'Top 3 Categories': ', '.join([f"{k} ({v*100:.1f}%)" for k, v in top]),
                'Missing %': f"{s['missing_ratio']*100:.1f}%"
            })
        st.dataframe(pd.DataFrame(cat_rows), use_container_width=True, hide_index=True)

    if not profile['correlation_matrix'].empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Correlation Matrix</div>', unsafe_allow_html=True)
        st.markdown(make_heatmap_html(profile['correlation_matrix'], "ORIGINAL DATA — PEARSON CORRELATION"), unsafe_allow_html=True)

    # Distribution histograms
    if numeric_cols:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Distribution Histograms</div>', unsafe_allow_html=True)
        cols_per_row = 3
        for i in range(0, len(numeric_cols), cols_per_row):
            row_cols = st.columns(cols_per_row)
            for j, col in enumerate(numeric_cols[i:i+cols_per_row]):
                with row_cols[j]:
                    vals = df[col].dropna()
                    hist, edges = np.histogram(vals, bins=30)
                    max_h = max(hist)
                    bar_width = 100 / len(hist)
                    bars = "".join([
                        f'<rect x="{k*bar_width:.1f}%" y="{100 - h/max_h*100:.1f}%" '
                        f'width="{bar_width*0.85:.1f}%" height="{h/max_h*100:.1f}%" '
                        f'fill="url(#grad)" rx="1"/>'
                        for k, h in enumerate(hist)
                    ])
                    st.markdown(f"""
                    <div style="background:#111118;border:1px solid #2a2a3a;border-radius:10px;padding:14px;">
                        <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;letter-spacing:1px;margin-bottom:8px;">{col}</div>
                        <svg width="100%" height="80" viewBox="0 0 100 100" preserveAspectRatio="none">
                            <defs>
                                <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stop-color="#7c6af7"/>
                                    <stop offset="100%" stop-color="#3ecfcf" stop-opacity="0.5"/>
                                </linearGradient>
                            </defs>
                            {bars}
                        </svg>
                        <div style="display:flex;justify-content:space-between;font-family:Space Mono,monospace;font-size:9px;color:#3a3a4a;margin-top:4px;">
                            <span>{vals.min():.2f}</span><span>{vals.max():.2f}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
# TAB 2: SYNTHETIC DATA
# ──────────────────────────────────────────────────────────────────────────
with tab2:
    if 'synth_df' not in st.session_state:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;">
            <div style="font-size:40px;margin-bottom:12px;">🧬</div>
            <div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#e8e8f0;margin-bottom:8px;">
                Ready to Generate
            </div>
            <div style="font-family:Space Mono,monospace;font-size:12px;color:#6b6b80;">
                Configure settings in the sidebar and click<br><strong style="color:#7c6af7">Generate Synthetic Data</strong>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        synth_df = st.session_state['synth_df']
        st.markdown('<div class="section-title">Synthetic Dataset Preview</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-sub">{len(synth_df):,} rows generated · {synth_df.shape[1]} columns</div>', unsafe_allow_html=True)
        st.dataframe(synth_df.head(100), use_container_width=True, height=280)

        # Side-by-side summary
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Original vs Synthetic — Summary Comparison</div>', unsafe_allow_html=True)

        if numeric_cols:
            compare_rows = []
            for col in numeric_cols:
                o = df[col].dropna()
                s = synth_df[col].dropna()
                compare_rows.append({
                    'Column': col,
                    'Orig Mean': f"{o.mean():.4f}",
                    'Synth Mean': f"{s.mean():.4f}",
                    'Orig Std': f"{o.std():.4f}",
                    'Synth Std': f"{s.std():.4f}",
                    'Orig Min': f"{o.min():.4f}",
                    'Synth Min': f"{s.min():.4f}",
                    'Orig Max': f"{o.max():.4f}",
                    'Synth Max': f"{s.max():.4f}",
                })
            st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)

        # Overlay histograms
        if numeric_cols:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-title">Distribution Overlay — Original vs Synthetic</div>', unsafe_allow_html=True)
            cols_per_row = 3
            for i in range(0, len(numeric_cols), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for j, col in enumerate(numeric_cols[i:i+cols_per_row]):
                    with row_cols[j]:
                        o_vals = df[col].dropna()
                        s_vals = synth_df[col].dropna()
                        all_min = min(o_vals.min(), s_vals.min())
                        all_max = max(o_vals.max(), s_vals.max())
                        bins = np.linspace(all_min, all_max, 31)
                        o_hist, _ = np.histogram(o_vals, bins=bins)
                        s_hist, _ = np.histogram(s_vals, bins=bins)
                        max_h = max(o_hist.max(), s_hist.max(), 1)
                        bw = 100 / len(o_hist)

                        o_bars = "".join([
                            f'<rect x="{k*bw:.1f}%" y="{100 - h/max_h*100:.1f}%" '
                            f'width="{bw*0.85:.1f}%" height="{h/max_h*100:.1f}%" '
                            f'fill="#7c6af7" opacity="0.7" rx="1"/>'
                            for k, h in enumerate(o_hist)
                        ])
                        s_bars = "".join([
                            f'<rect x="{k*bw:.1f}%" y="{100 - h/max_h*100:.1f}%" '
                            f'width="{bw*0.85:.1f}%" height="{h/max_h*100:.1f}%" '
                            f'fill="#3ecfcf" opacity="0.5" rx="1"/>'
                            for k, h in enumerate(s_hist)
                        ])
                        st.markdown(f"""
                        <div style="background:#111118;border:1px solid #2a2a3a;border-radius:10px;padding:14px;">
                            <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;letter-spacing:1px;margin-bottom:4px;">{col}</div>
                            <div style="display:flex;gap:12px;font-family:Space Mono,monospace;font-size:9px;margin-bottom:6px;">
                                <span style="color:#7c6af7">■ Original</span>
                                <span style="color:#3ecfcf">■ Synthetic</span>
                            </div>
                            <svg width="100%" height="80" viewBox="0 0 100 100" preserveAspectRatio="none">
                                {o_bars}{s_bars}
                            </svg>
                        </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
# TAB 3: TRUST METRICS
# ──────────────────────────────────────────────────────────────────────────
with tab3:
    if 'trust_metrics' not in st.session_state:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;">
            <div style="font-size:40px;margin-bottom:12px;">📐</div>
            <div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#e8e8f0;margin-bottom:8px;">
                Awaiting Generation
            </div>
            <div style="font-family:Space Mono,monospace;font-size:12px;color:#6b6b80;">
                Generate synthetic data first to see trust metrics.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        tm = st.session_state['trust_metrics']
        sci = tm['sci']
        color = score_color(sci)
        badge_cls, badge_label = score_badge(sci)

        # SCI Hero
        pct = sci / 100
        circumference = 2 * 3.14159 * 54
        dash = circumference * pct
        gap = circumference - dash

        st.markdown(f"""
        <div class="sci-container" style="margin-bottom:24px;">
            <div class="metric-label" style="margin-bottom:16px;">STRUCTURAL CONSISTENCY INDEX</div>
            <svg width="160" height="160" viewBox="0 0 120 120" style="display:block;margin:0 auto 12px;">
                <circle cx="60" cy="60" r="54" fill="none" stroke="#1a1a24" stroke-width="10"/>
                <circle cx="60" cy="60" r="54" fill="none" stroke="{color}" stroke-width="10"
                    stroke-dasharray="{dash:.1f} {gap:.1f}"
                    stroke-dashoffset="{circumference/4:.1f}"
                    stroke-linecap="round"/>
                <text x="60" y="56" text-anchor="middle" font-size="28" font-weight="800"
                      fill="{color}" font-family="Syne,sans-serif">{sci}</text>
                <text x="60" y="72" text-anchor="middle" font-size="10"
                      fill="#6b6b80" font-family="Space Mono,monospace">/ 100</text>
            </svg>
            <span class="badge {badge_cls}">{badge_label}</span>
            <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;margin-top:12px;">
                Weighted composite of correlation, distribution and categorical fidelity scores
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Sub-scores
        c1, c2, c3 = st.columns(3)
        sub_scores = [
            (c1, "Correlation Preservation", tm['correlation_score'], "30% weight · Pearson matrix comparison"),
            (c2, "Distribution Similarity", tm['distribution_score'], "40% weight · KS-test · Wasserstein"),
            (c3, "Categorical Fidelity", tm['categorical_score'], "30% weight · KL Divergence"),
        ]
        for col, label, score, note in sub_scores:
            with col:
                clr = score_color(score)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="color:{clr}">{score}</div>
                    <div class="metric-sub">{note}</div>
                </div>""", unsafe_allow_html=True)

        # Correlation heatmaps
        if not tm['orig_corr'].empty:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-title">Correlation Matrix Comparison</div>', unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(make_heatmap_html(tm['orig_corr'], "ORIGINAL DATA"), unsafe_allow_html=True)
            with col_b:
                st.markdown(make_heatmap_html(tm['synth_corr'], "SYNTHETIC DATA"), unsafe_allow_html=True)

        # Distribution scores table
        if tm['dist_scores']:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-title">Per-Column Distribution Metrics</div>', unsafe_allow_html=True)
            dist_rows = []
            for col_name, v in tm['dist_scores'].items():
                badge_c, badge_t = score_badge(v['score'] * 100)
                dist_rows.append({
                    'Column': col_name,
                    'KS Statistic': f"{v['ks_stat']:.4f}",
                    'KS p-value': f"{v['ks_pvalue']:.4f}",
                    'Wasserstein (norm.)': f"{v['wasserstein']:.4f}",
                    'Fidelity Score': f"{v['score']*100:.1f}",
                    'Status': badge_t
                })
            st.dataframe(pd.DataFrame(dist_rows), use_container_width=True, hide_index=True)

        # Categorical fidelity
        if tm['cat_scores']:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-title">Categorical Distribution Fidelity</div>', unsafe_allow_html=True)
            cat_rows = []
            for col_name, v in tm['cat_scores'].items():
                badge_c, badge_t = score_badge(v['score'] * 100)
                cat_rows.append({
                    'Column': col_name,
                    'KL Divergence': f"{v['kl_divergence']:.4f}",
                    'Fidelity Score': f"{v['score']*100:.1f}",
                    'Status': badge_t
                })
            st.dataframe(pd.DataFrame(cat_rows), use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────────────────
# TAB 4: EXPORT
# ──────────────────────────────────────────────────────────────────────────
with tab4:
    if 'synth_df' not in st.session_state:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;">
            <div style="font-size:40px;margin-bottom:12px;">⬇</div>
            <div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#e8e8f0;margin-bottom:8px;">
                No Data to Export
            </div>
            <div style="font-family:Space Mono,monospace;font-size:12px;color:#6b6b80;">
                Generate synthetic data first.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        synth_df = st.session_state['synth_df']
        st.markdown('<div class="section-title">⬇ Export Synthetic Dataset</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-sub">{len(synth_df):,} rows ready for download</div>', unsafe_allow_html=True)

        # Summary card
        sci_val = st.session_state.get('trust_metrics', {}).get('sci', 'N/A')
        clr = score_color(float(sci_val)) if isinstance(sci_val, (int, float)) else '#7c6af7'

        st.markdown(f"""
        <div style="background:#111118;border:1px solid #2a2a3a;border-radius:12px;padding:24px;margin-bottom:24px;
                    display:grid;grid-template-columns:repeat(4,1fr);gap:20px;">
            <div>
                <div class="metric-label">Rows Generated</div>
                <div style="font-size:24px;font-weight:800;color:#7c6af7;">{len(synth_df):,}</div>
            </div>
            <div>
                <div class="metric-label">Columns</div>
                <div style="font-size:24px;font-weight:800;color:#3ecfcf;">{synth_df.shape[1]}</div>
            </div>
            <div>
                <div class="metric-label">SCI Score</div>
                <div style="font-size:24px;font-weight:800;color:{clr};">{sci_val}</div>
            </div>
            <div>
                <div class="metric-label">Memory (approx)</div>
                <div style="font-size:24px;font-weight:800;color:#e8e8f0;">{synth_df.memory_usage(deep=True).sum()//1024:,} KB</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            st.markdown("""
            <div style="background:#111118;border:1px solid #2a2a3a;border-radius:12px;padding:20px;margin-bottom:12px;">
                <div class="metric-label" style="margin-bottom:8px;">CSV Export</div>
                <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;line-height:1.7;margin-bottom:12px;">
                    Universal format · UTF-8 encoded<br>Compatible with all data tools
                </div>
            </div>""", unsafe_allow_html=True)
            csv_data = synth_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇ Download CSV",
                data=csv_data,
                file_name="datasynthx_synthetic.csv",
                mime="text/csv"
            )

        with col_dl2:
            st.markdown("""
            <div style="background:#111118;border:1px solid #2a2a3a;border-radius:12px;padding:20px;margin-bottom:12px;">
                <div class="metric-label" style="margin-bottom:8px;">Excel Export</div>
                <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;line-height:1.7;margin-bottom:12px;">
                    Styled .xlsx format · Column widths<br>auto-fitted · Purple header theme
                </div>
            </div>""", unsafe_allow_html=True)
            try:
                excel_data = to_excel_bytes(synth_df)
                st.download_button(
                    "⬇ Download Excel",
                    data=excel_data,
                    file_name="datasynthx_synthetic.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.warning(f"Excel export unavailable: {e}. Use CSV instead.")


# ═══════════════════════════════════════════════════════════════════════════
#  GENERATION TRIGGER
# ═══════════════════════════════════════════════════════════════════════════

if generate_btn:
    if not numeric_cols and not categorical_cols:
        st.error("No usable columns found. Please check your dataset.")
    else:
        with st.spinner(""):
            progress_bar = st.progress(0, text="Initializing generator…")

            progress_bar.progress(15, text="Building statistical model…")
            generator = SyntheticDataGenerator(df, profile)

            progress_bar.progress(40, text=f"Generating {n_rows:,} synthetic rows…")
            synth_df = generator.generate(n_rows, noise_level=noise_level)

            progress_bar.progress(70, text="Computing trust metrics…")
            tm = TrustMetrics(df, synth_df, profile)
            trust_data = tm.compute_sci()

            progress_bar.progress(95, text="Finalizing…")
            st.session_state['synth_df'] = synth_df
            st.session_state['trust_metrics'] = trust_data

            progress_bar.progress(100, text="Done!")

        sci = trust_data['sci']
        clr = score_color(sci)
        badge_cls, badge_label = score_badge(sci)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(124,106,247,0.08),rgba(62,207,207,0.08));
                    border:1px solid rgba(124,106,247,0.3);border-radius:12px;
                    padding:20px 24px;margin-top:16px;display:flex;align-items:center;gap:16px;">
            <div style="font-size:32px;">✓</div>
            <div>
                <div style="font-family:Syne,sans-serif;font-size:16px;font-weight:700;color:#e8e8f0;">
                    {n_rows:,} synthetic rows generated successfully
                </div>
                <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;margin-top:4px;">
                    SCI Score: <span style="color:{clr};font-weight:700;">{sci}/100</span> ·
                    Status: <span class="badge {badge_cls}">{badge_label}</span> ·
                    Columns: {synth_df.shape[1]}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.rerun()
