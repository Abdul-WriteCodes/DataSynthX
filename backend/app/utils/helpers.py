import re
import pandas as pd


def sanitize_filename(name: str) -> str:
    """Remove unsafe characters from a filename."""
    return re.sub(r"[^\w\s\-.]", "", name).strip().replace(" ", "_")


def detect_panel_structure(df: pd.DataFrame) -> dict:
    """
    Heuristically suggest which columns might be entity and time identifiers.
    Returns suggestions based on dtype and cardinality.
    """
    suggestions = {"entity_col": None, "time_col": None}
    for col in df.columns:
        col_lower = col.lower()
        if any(k in col_lower for k in ["company", "firm", "entity", "id", "name"]):
            suggestions["entity_col"] = col
        if any(k in col_lower for k in ["year", "time", "date", "period", "quarter"]):
            suggestions["time_col"] = col
    return suggestions


def validate_panel_df(df: pd.DataFrame, entity_col: str, time_col: str) -> list[str]:
    """Return a list of validation warning strings."""
    warnings = []
    n_entities = df[entity_col].nunique()
    n_periods = df[time_col].nunique()
    if n_entities < 2:
        warnings.append("Panel requires at least 2 entities.")
    if n_periods < 2:
        warnings.append("Panel requires at least 2 time periods.")
    if df.isnull().any().any():
        null_cols = df.columns[df.isnull().any()].tolist()
        warnings.append(f"Missing values detected in: {', '.join(null_cols)}. Rows with NaN will be dropped.")
    return warnings
