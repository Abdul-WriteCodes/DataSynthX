"""
llm_service.py
Uses OpenAI GPT-4o to write a professional academic narrative
of the panel regression results.
"""

import json
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an expert econometrician and academic writer specialising in panel data analysis.
Your task is to write a clear, rigorous, and professional discussion of panel regression results
in the style of a peer-reviewed academic paper.

Structure your response with these sections using Markdown headings:
## 4.1 Descriptive Statistics
## 4.2 Correlation Analysis
## 4.3 Regression Results
## 4.4 Diagnostic Tests
## 4.5 Summary of Findings

Rules:
- Report all coefficient values, t-statistics, and p-values precisely as given.
- Use significance stars correctly: *** p<0.01, ** p<0.05, * p<0.1.
- Interpret the direction and magnitude of each significant coefficient.
- Reference diagnostic test outcomes and explain their implications.
- Write in third person, academic register.
- Do NOT fabricate numbers — use only what is provided.
- Keep each section concise but substantive (150–300 words each).
"""


def _format_regression_for_prompt(regression_results: dict) -> str:
    lines = []
    for model_key, model_data in regression_results.items():
        lines.append(f"\n--- {model_data.get('model', model_key)} ---")
        lines.append(
            f"R²={model_data.get('r_squared') or model_data.get('r_squared_within')}, "
            f"F={model_data.get('f_statistic')}, p={model_data.get('f_pvalue')}, "
            f"N={model_data.get('n_obs')}"
        )
        for var in model_data.get("variables", []):
            sig = ""
            pv = var.get("p_value") or 1
            if pv < 0.01:
                sig = "***"
            elif pv < 0.05:
                sig = "**"
            elif pv < 0.1:
                sig = "*"
            lines.append(
                f"  {var['variable']}: β={var['beta']}, SE={var['std_error']}, "
                f"t={var['t_stat']}, p={var['p_value']}{sig}, "
                f"95% CI [{var['lcl']}, {var['ucl']}]"
            )
    return "\n".join(lines)


def _format_diagnostics_for_prompt(diagnostic_results: dict) -> str:
    lines = []
    for key, result in diagnostic_results.items():
        lines.append(f"\n{result.get('test', key)}:")
        lines.append(result.get("interpretation", str(result)))
    return "\n".join(lines)


def _format_descriptive_for_prompt(descriptive_stats: dict) -> str:
    lines = []
    for var, stats in descriptive_stats.items():
        lines.append(
            f"  {var}: N={stats.get('count')}, mean={stats.get('mean')}, "
            f"SD={stats.get('std')}, min={stats.get('min')}, max={stats.get('max')}"
        )
    return "\n".join(lines)


def generate_narrative(
    analysis_title: str,
    dependent_var: str,
    independent_vars: list[str],
    descriptive_stats: dict,
    correlation_matrix: dict,
    regression_results: dict,
    diagnostic_results: dict,
) -> str:
    """
    Calls OpenAI and returns a full academic narrative as a string.
    """
    user_prompt = f"""
Study title: {analysis_title}
Dependent variable: {dependent_var}
Independent variables: {', '.join(independent_vars)}

DESCRIPTIVE STATISTICS:
{_format_descriptive_for_prompt(descriptive_stats)}

PEARSON CORRELATION MATRIX:
{json.dumps(correlation_matrix.get('coefficients', {}), indent=2)}

REGRESSION RESULTS:
{_format_regression_for_prompt(regression_results)}

DIAGNOSTIC TESTS:
{_format_diagnostics_for_prompt(diagnostic_results)}

Please write the full results and discussion section for this study.
"""

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=3000,
    )

    return response.choices[0].message.content
