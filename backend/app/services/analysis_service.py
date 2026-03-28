"""
analysis_service.py
Performs all panel data statistical computations:
  - Descriptive statistics
  - Pearson correlation matrix
  - Fixed Effects (FE), Random Effects (RE), Pooled OLS (POLS), Between Effects (BE)
  - Diagnostics: Hausman, Breusch-Pagan, VIF, Wooldridge serial correlation
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS, RandomEffects, BetweenOLS, PooledOLS
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from scipy import stats
from typing import Any


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _safe_float(val) -> float | None:
    try:
        v = float(val)
        return None if (np.isnan(v) or np.isinf(v)) else round(v, 6)
    except Exception:
        return None


def _series_to_dict(series: pd.Series) -> dict:
    return {str(k): _safe_float(v) for k, v in series.items()}


def _conf_interval(results, alpha: float = 0.05) -> pd.DataFrame:
    """Return confidence intervals from linearmodels results."""
    ci = results.conf_int(level=1 - alpha)
    return ci


# ─────────────────────────────────────────────
# 1. Descriptive Statistics
# ─────────────────────────────────────────────

def compute_descriptive_stats(data: pd.DataFrame) -> dict:
    desc = data.describe().T  # variables as rows
    desc["skewness"] = data.skew()
    desc["kurtosis"] = data.kurt()

    result = {}
    for var in desc.index:
        result[str(var)] = {
            "count": _safe_float(desc.loc[var, "count"]),
            "mean": _safe_float(desc.loc[var, "mean"]),
            "std": _safe_float(desc.loc[var, "std"]),
            "min": _safe_float(desc.loc[var, "min"]),
            "p25": _safe_float(desc.loc[var, "25%"]),
            "median": _safe_float(desc.loc[var, "50%"]),
            "p75": _safe_float(desc.loc[var, "75%"]),
            "max": _safe_float(desc.loc[var, "max"]),
            "skewness": _safe_float(desc.loc[var, "skewness"]),
            "kurtosis": _safe_float(desc.loc[var, "kurtosis"]),
        }
    return result


# ─────────────────────────────────────────────
# 2. Pearson Correlation Matrix
# ─────────────────────────────────────────────

def compute_correlation_matrix(data: pd.DataFrame) -> dict:
    corr = data.corr(method="pearson")
    pval_matrix = pd.DataFrame(
        index=corr.index, columns=corr.columns, dtype=float
    )
    for c1 in corr.columns:
        for c2 in corr.columns:
            if c1 == c2:
                pval_matrix.loc[c1, c2] = 0.0
            else:
                _, p = stats.pearsonr(
                    data[c1].dropna(), data[c2].dropna()
                )
                pval_matrix.loc[c1, c2] = round(float(p), 6)

    return {
        "coefficients": {
            str(r): {str(c): _safe_float(corr.loc[r, c]) for c in corr.columns}
            for r in corr.index
        },
        "pvalues": {
            str(r): {str(c): _safe_float(pval_matrix.loc[r, c]) for c in pval_matrix.columns}
            for r in pval_matrix.index
        },
        "variables": list(corr.columns.astype(str)),
    }


# ─────────────────────────────────────────────
# 3. Regression helpers
# ─────────────────────────────────────────────

def _extract_linearmodels_results(results, model_name: str) -> dict:
    """Standardise linearmodels result objects into a clean dict."""
    params = results.params
    pvals = results.pvalues
    tstats = results.tstats
    std_err = results.std_errors

    try:
        ci = results.conf_int()
    except Exception:
        ci = pd.DataFrame({"lower": np.nan, "upper": np.nan}, index=params.index)

    variables = []
    for var in params.index:
        variables.append({
            "variable": str(var),
            "beta": _safe_float(params[var]),
            "std_error": _safe_float(std_err[var]),
            "t_stat": _safe_float(tstats[var]),
            "p_value": _safe_float(pvals[var]),
            "lcl": _safe_float(ci.iloc[list(params.index).index(var), 0]),
            "ucl": _safe_float(ci.iloc[list(params.index).index(var), 1]),
        })

    summary = {
        "model": model_name,
        "variables": variables,
        "r_squared": _safe_float(getattr(results, "rsquared", None)),
        "r_squared_within": _safe_float(getattr(results, "rsquared_within", None)),
        "r_squared_between": _safe_float(getattr(results, "rsquared_between", None)),
        "r_squared_overall": _safe_float(getattr(results, "rsquared_overall", None)),
        "f_statistic": _safe_float(
            getattr(results.f_statistic, "stat", None)
            if hasattr(results, "f_statistic") else None
        ),
        "f_pvalue": _safe_float(
            getattr(results.f_statistic, "pval", None)
            if hasattr(results, "f_statistic") else None
        ),
        "n_obs": int(results.nobs) if hasattr(results, "nobs") else None,
        "n_entities": int(results.entity_info.total) if hasattr(results, "entity_info") else None,
        "n_periods": int(results.time_info.total) if hasattr(results, "time_info") else None,
    }
    return summary


# ─────────────────────────────────────────────
# 4. Fixed Effects
# ─────────────────────────────────────────────

def run_fixed_effects(y: pd.Series, X: pd.DataFrame) -> tuple[dict, Any]:
    model = PanelOLS(y, X, entity_effects=True, time_effects=False)
    results = model.fit(cov_type="robust")
    return _extract_linearmodels_results(results, "Fixed Effects"), results


# ─────────────────────────────────────────────
# 5. Random Effects
# ─────────────────────────────────────────────

def run_random_effects(y: pd.Series, X: pd.DataFrame) -> tuple[dict, Any]:
    X_re = sm.add_constant(X)
    model = RandomEffects(y, X_re)
    results = model.fit()
    return _extract_linearmodels_results(results, "Random Effects"), results


# ─────────────────────────────────────────────
# 6. Pooled OLS
# ─────────────────────────────────────────────

def run_pooled_ols(y: pd.Series, X: pd.DataFrame) -> tuple[dict, Any]:
    X_pols = sm.add_constant(X)
    model = PooledOLS(y, X_pols)
    results = model.fit(cov_type="robust")
    return _extract_linearmodels_results(results, "Pooled OLS"), results


# ─────────────────────────────────────────────
# 7. Between Effects
# ─────────────────────────────────────────────

def run_between_effects(y: pd.Series, X: pd.DataFrame) -> tuple[dict, Any]:
    X_be = sm.add_constant(X)
    model = BetweenOLS(y, X_be)
    results = model.fit()
    return _extract_linearmodels_results(results, "Between Effects"), results


# ─────────────────────────────────────────────
# 8. Hausman Test
# ─────────────────────────────────────────────

def run_hausman_test(fe_results, re_results) -> dict:
    b = fe_results.params
    B = re_results.params
    v_b = fe_results.cov
    v_B = re_results.cov

    common = list(set(b.index) & set(B.index))
    b = b[common]
    B = B[common]
    v_b = v_b.loc[common, common]
    v_B = v_B.loc[common, common]

    diff = b - B
    cov_diff = v_b - v_B

    try:
        stat = float(diff.T @ np.linalg.pinv(cov_diff.values) @ diff)
    except Exception:
        stat = float(np.dot(diff, np.dot(np.linalg.pinv(cov_diff), diff)))

    df_h = len(common)
    pval = float(stats.chi2.sf(stat, df_h))
    preferred = "Fixed Effects" if pval < 0.05 else "Random Effects"

    return {
        "test": "Hausman Test",
        "statistic": round(stat, 4),
        "df": df_h,
        "p_value": round(pval, 6),
        "preferred_model": preferred,
        "interpretation": (
            f"χ²({df_h}) = {round(stat, 4)}, p = {round(pval, 4)}. "
            f"{'Reject null: Fixed Effects preferred.' if pval < 0.05 else 'Fail to reject null: Random Effects preferred.'}"
        ),
    }


# ─────────────────────────────────────────────
# 9. Breusch-Pagan Heteroskedasticity Test
# ─────────────────────────────────────────────

def run_breusch_pagan(y: pd.Series, X: pd.DataFrame) -> dict:
    X_bp = sm.add_constant(X.reset_index(drop=True))
    y_bp = y.reset_index(drop=True)
    ols = sm.OLS(y_bp, X_bp).fit()
    lm_stat, lm_pval, f_stat, f_pval = het_breuschpagan(ols.resid, ols.model.exog)

    return {
        "test": "Breusch-Pagan Test",
        "lm_statistic": round(float(lm_stat), 4),
        "lm_p_value": round(float(lm_pval), 6),
        "f_statistic": round(float(f_stat), 4),
        "f_p_value": round(float(f_pval), 6),
        "heteroskedasticity_detected": lm_pval < 0.05,
        "interpretation": (
            f"LM = {round(float(lm_stat), 4)}, p = {round(float(lm_pval), 4)}. "
            f"{'Heteroskedasticity detected. Use robust standard errors.' if lm_pval < 0.05 else 'No significant heteroskedasticity detected.'}"
        ),
    }


# ─────────────────────────────────────────────
# 10. VIF — Multicollinearity
# ─────────────────────────────────────────────

def run_vif(X: pd.DataFrame) -> dict:
    X_vif = sm.add_constant(X.reset_index(drop=True))
    vif_values = []
    for i, col in enumerate(X_vif.columns):
        vif = variance_inflation_factor(X_vif.values.astype(float), i)
        vif_values.append({"variable": str(col), "vif": round(float(vif), 4)})

    max_vif = max(v["vif"] for v in vif_values if v["variable"] != "const")
    concern = max_vif > 10

    return {
        "test": "VIF (Variance Inflation Factor)",
        "values": vif_values,
        "max_vif": round(max_vif, 4),
        "multicollinearity_concern": concern,
        "interpretation": (
            f"Maximum VIF = {round(max_vif, 4)}. "
            f"{'Severe multicollinearity detected (VIF > 10).' if max_vif > 10 else 'Moderate multicollinearity.' if max_vif > 5 else 'No multicollinearity concern (VIF < 5).'}"
        ),
    }


# ─────────────────────────────────────────────
# 11. Wooldridge Test for Serial Correlation
# ─────────────────────────────────────────────

def run_wooldridge_serial_correlation(
    y: pd.Series, X: pd.DataFrame, entity_col: str = None
) -> dict:
    """
    Wooldridge (2002) test for AR(1) serial correlation in panel data.
    Uses first-differenced OLS residuals and tests if autocorrelation = -0.5.
    """
    try:
        df_inner = X.copy()
        df_inner["__y__"] = y

        # Reset to access entity/time levels
        df_reset = df_inner.reset_index()
        entity_name = df_reset.columns[0]
        time_name = df_reset.columns[1]

        df_reset = df_reset.sort_values([entity_name, time_name])
        df_reset["__y_diff__"] = df_reset.groupby(entity_name)["__y__"].diff()

        X_cols = [c for c in X.columns]
        for col in X_cols:
            df_reset[f"__d_{col}__"] = df_reset.groupby(entity_name)[col].diff()

        df_d = df_reset.dropna(subset=["__y_diff__"] + [f"__d_{c}__" for c in X_cols])
        y_d = df_d["__y_diff__"]
        X_d = sm.add_constant(df_d[[f"__d_{c}__" for c in X_cols]])

        ols_d = sm.OLS(y_d, X_d).fit()
        resid = ols_d.resid.values

        # Group residuals by entity and compute lag correlation
        df_d = df_d.copy()
        df_d["__resid__"] = resid
        df_d["__resid_lag__"] = df_d.groupby(entity_name)["__resid__"].shift(1)
        df_d2 = df_d.dropna(subset=["__resid__", "__resid_lag__"])

        corr_ols = sm.OLS(
            df_d2["__resid__"].values,
            sm.add_constant(df_d2["__resid_lag__"].values)
        ).fit()

        rho = corr_ols.params[1]
        # H0: rho = -0.5 (no serial correlation in first differences)
        t_stat = (rho - (-0.5)) / corr_ols.bse[1]
        df_t = corr_ols.df_resid
        p_val = 2 * stats.t.sf(abs(t_stat), df_t)

        return {
            "test": "Wooldridge Serial Correlation Test",
            "rho": round(float(rho), 4),
            "t_statistic": round(float(t_stat), 4),
            "df": int(df_t),
            "p_value": round(float(p_val), 6),
            "serial_correlation_detected": p_val < 0.05,
            "interpretation": (
                f"t = {round(float(t_stat), 4)}, p = {round(float(p_val), 4)}. "
                f"{'Serial correlation detected. Consider AR(1) correction.' if p_val < 0.05 else 'No significant serial correlation detected.'}"
            ),
        }
    except Exception as e:
        return {
            "test": "Wooldridge Serial Correlation Test",
            "error": str(e),
            "interpretation": "Could not compute test. Ensure sufficient time periods per entity.",
        }


# ─────────────────────────────────────────────
# 12. Master runner
# ─────────────────────────────────────────────

def run_full_analysis(
    df: pd.DataFrame,
    entity_col: str,
    time_col: str,
    dependent_var: str,
    independent_vars: list[str],
    models: list[str],
    diagnostics: list[str],
) -> dict:
    """
    Orchestrates the full analysis pipeline.
    Returns a structured dict with all results.
    """
    all_vars = [dependent_var] + independent_vars
    data = df[all_vars].copy()

    # Set panel index
    panel_df = df.copy()
    panel_df = panel_df.set_index([entity_col, time_col])
    y = panel_df[dependent_var]
    X = panel_df[independent_vars]

    output = {}

    # Descriptive
    output["descriptive_stats"] = compute_descriptive_stats(data)

    # Correlation
    output["correlation_matrix"] = compute_correlation_matrix(data)

    # Regressions
    regression_results = {}
    fe_res_obj = None
    re_res_obj = None

    if "FE" in models:
        fe_dict, fe_res_obj = run_fixed_effects(y, X)
        regression_results["FE"] = fe_dict

    if "RE" in models:
        re_dict, re_res_obj = run_random_effects(y, X)
        regression_results["RE"] = re_dict

    if "POLS" in models:
        pols_dict, _ = run_pooled_ols(y, X)
        regression_results["POLS"] = pols_dict

    if "BE" in models:
        be_dict, _ = run_between_effects(y, X)
        regression_results["BE"] = be_dict

    output["regression_results"] = regression_results

    # Diagnostics
    diagnostic_results = {}

    if "HAUSMAN" in diagnostics and fe_res_obj is not None and re_res_obj is not None:
        diagnostic_results["hausman"] = run_hausman_test(fe_res_obj, re_res_obj)

    if "BP" in diagnostics:
        diagnostic_results["breusch_pagan"] = run_breusch_pagan(y, X)

    if "VIF" in diagnostics:
        diagnostic_results["vif"] = run_vif(X)

    if "WOOLDRIDGE" in diagnostics:
        diagnostic_results["wooldridge"] = run_wooldridge_serial_correlation(y, X)

    output["diagnostic_results"] = diagnostic_results

    return output
