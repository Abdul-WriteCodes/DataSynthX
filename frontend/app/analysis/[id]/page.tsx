"use client";
import { useEffect, useState, useCallback, useRef } from "react";
import { useParams } from "next/navigation";
import toast from "react-hot-toast";
import AuthGuard from "../../../components/AuthGuard";
import Sidebar from "../../../components/Sidebar";
import { analysisApi, taskApi } from "../../../lib/api";
import {
  CheckCircle, Clock, Loader2, AlertCircle,
  Download, ChevronDown, ChevronUp, FileText
} from "lucide-react";
import clsx from "clsx";

// ── Utility helpers ─────────────────────────────────────────

function fmt(val: any, decimals = 4): string {
  if (val === null || val === undefined) return "—";
  const n = parseFloat(val);
  if (isNaN(n)) return String(val);
  return n.toFixed(decimals);
}

function fmtPval(val: any): string {
  if (val === null || val === undefined) return "—";
  const n = parseFloat(val);
  if (isNaN(n)) return "—";
  if (n < 0.001) return "<0.001";
  return n.toFixed(4);
}

function sigStars(pval: any): string {
  const p = parseFloat(pval);
  if (isNaN(p)) return "";
  if (p < 0.01) return "***";
  if (p < 0.05) return "**";
  if (p < 0.10) return "*";
  return "";
}

// ── Section wrapper ──────────────────────────────────────────

function Section({ title, children, defaultOpen = true }: {
  title: string; children: React.ReactNode; defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden mb-6">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-6 py-4 hover:bg-slate-50 transition-colors"
      >
        <h2 className="text-sm font-semibold text-slate-800">{title}</h2>
        {open ? <ChevronUp size={16} className="text-slate-400" /> : <ChevronDown size={16} className="text-slate-400" />}
      </button>
      {open && <div className="px-6 pb-6 overflow-x-auto">{children}</div>}
    </div>
  );
}

// ── Table note ───────────────────────────────────────────────

function TableNote({ text }: { text: string }) {
  return <p className="text-xs text-slate-400 italic mt-3">{text}</p>;
}

// ── Descriptive Statistics Table ─────────────────────────────

function DescriptiveTable({ data }: { data: Record<string, any> }) {
  const vars = Object.keys(data);
  return (
    <div>
      <table className="result-table">
        <thead>
          <tr>
            {["Variable","N","Mean","Std. Dev.","Min","25th Pct.","Median","75th Pct.","Max","Skewness","Kurtosis"]
              .map((h) => <th key={h}>{h}</th>)}
          </tr>
        </thead>
        <tbody>
          {vars.map((v) => {
            const s = data[v];
            return (
              <tr key={v}>
                <td className="font-mono text-xs">{v}</td>
                <td>{fmt(s.count, 0)}</td>
                <td>{fmt(s.mean)}</td>
                <td>{fmt(s.std)}</td>
                <td>{fmt(s.min)}</td>
                <td>{fmt(s.p25)}</td>
                <td>{fmt(s.median)}</td>
                <td>{fmt(s.p75)}</td>
                <td>{fmt(s.max)}</td>
                <td>{fmt(s.skewness)}</td>
                <td>{fmt(s.kurtosis)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <TableNote text="Descriptive statistics computed for all study variables." />
    </div>
  );
}

// ── Correlation Matrix Table ─────────────────────────────────

function CorrelationTable({ data }: { data: any }) {
  const vars: string[] = data.variables || [];
  const coeffs = data.coefficients || {};
  const pvals  = data.pvalues     || {};

  return (
    <div>
      <table className="result-table">
        <thead>
          <tr>
            <th>Variable</th>
            {vars.map((_, i) => <th key={i} className="text-center">({i + 1})</th>)}
          </tr>
        </thead>
        <tbody>
          {vars.map((v, i) => (
            <tr key={v}>
              <td className="font-mono text-xs">({i + 1}) {v}</td>
              {vars.map((v2, j) => {
                if (i === j) return <td key={j} className="text-center font-medium">1.000</td>;
                const coeff = coeffs[v]?.[v2];
                const pval  = pvals[v]?.[v2];
                const stars = sigStars(pval);
                return (
                  <td key={j} className={clsx("text-center", stars ? "sig-green" : "")}>
                    {fmt(coeff, 3)}{stars}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <TableNote text="*** p<0.01, ** p<0.05, * p<0.10. Pearson correlation coefficients." />
    </div>
  );
}

// ── Regression Results Table ─────────────────────────────────

function RegressionTable({ modelKey, data }: { modelKey: string; data: any }) {
  const vars = data.variables || [];

  const fitStats = [
    { label: "R²",           val: data.r_squared           },
    { label: "R² (within)",  val: data.r_squared_within    },
    { label: "R² (between)", val: data.r_squared_between   },
    { label: "R² (overall)", val: data.r_squared_overall   },
    { label: "F-stat",       val: data.f_statistic         },
    { label: "F p-value",    val: data.f_pvalue            },
    { label: "Obs.",         val: data.n_obs               },
    { label: "Entities",     val: data.n_entities          },
    { label: "Periods",      val: data.n_periods           },
  ].filter((s) => s.val !== null && s.val !== undefined);

  return (
    <div className="mb-8">
      <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
        <span className="bg-brand-500 text-white text-xs px-2 py-0.5 rounded font-mono">{modelKey}</span>
        {data.model}
      </h3>
      <table className="result-table">
        <thead>
          <tr>
            {["Variable","β (Coef.)","Std. Error","t-Stat","p-Value","Sig.","LCL 95%","UCL 95%"].map((h) => (
              <th key={h} className={h === "Variable" ? "text-left" : "text-center"}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {vars.map((vd: any) => {
            const stars = sigStars(vd.p_value);
            return (
              <tr key={vd.variable}>
                <td className="font-mono text-xs text-left">{vd.variable}</td>
                <td className={clsx("text-center", stars ? "sig-green font-semibold" : "")}>{fmt(vd.beta)}</td>
                <td className="text-center">{fmt(vd.std_error)}</td>
                <td className="text-center">{fmt(vd.t_stat)}</td>
                <td className={clsx("text-center", stars ? "sig-green" : "")}>{fmtPval(vd.p_value)}</td>
                <td className={clsx("text-center font-bold", stars ? "sig-green" : "sig-none")}>{stars || "—"}</td>
                <td className="text-center">{fmt(vd.lcl)}</td>
                <td className="text-center">{fmt(vd.ucl)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* Fit statistics */}
      <div className="flex flex-wrap gap-4 mt-3">
        {fitStats.map(({ label, val }) => (
          <div key={label} className="text-xs text-slate-500">
            <span className="font-medium text-slate-700">{label}:</span>{" "}
            {typeof val === "number" ? fmt(val, 4) : val}
          </div>
        ))}
      </div>
      <TableNote text="*** p<0.01, ** p<0.05, * p<0.10. LCL/UCL = 95% confidence interval bounds. Robust std. errors where applicable." />
    </div>
  );
}

// ── Diagnostics Table ────────────────────────────────────────

function DiagnosticsPanel({ data }: { data: any }) {
  const hausman   = data.hausman;
  const bp        = data.breusch_pagan;
  const vif       = data.vif;
  const wooldridge = data.wooldridge;

  return (
    <div className="space-y-6">
      {/* Summary table */}
      <table className="result-table">
        <thead>
          <tr>
            <th className="text-left">Test</th>
            <th>Statistic</th>
            <th>df</th>
            <th>p-Value</th>
            <th className="text-left">Conclusion</th>
          </tr>
        </thead>
        <tbody>
          {hausman && !hausman.error && (
            <tr>
              <td className="text-left">Hausman Test</td>
              <td>χ² = {fmt(hausman.statistic)}</td>
              <td>{hausman.df}</td>
              <td>{fmtPval(hausman.p_value)}</td>
              <td className={clsx("text-left text-xs", hausman.p_value < 0.05 ? "text-amber-700" : "text-emerald-700")}>
                {hausman.preferred_model} preferred
              </td>
            </tr>
          )}
          {bp && !bp.error && (
            <tr>
              <td className="text-left">Breusch-Pagan Test</td>
              <td>LM = {fmt(bp.lm_statistic)}</td>
              <td>—</td>
              <td>{fmtPval(bp.lm_p_value)}</td>
              <td className={clsx("text-left text-xs", bp.heteroskedasticity_detected ? "text-red-600" : "text-emerald-700")}>
                {bp.heteroskedasticity_detected ? "Heteroskedasticity detected" : "No heteroskedasticity"}
              </td>
            </tr>
          )}
          {vif && !vif.error && (
            <tr>
              <td className="text-left">VIF (Multicollinearity)</td>
              <td>Max = {fmt(vif.max_vif)}</td>
              <td>—</td>
              <td>—</td>
              <td className={clsx("text-left text-xs", vif.multicollinearity_concern ? "text-red-600" : "text-emerald-700")}>
                {vif.multicollinearity_concern ? "Concern (VIF > 10)" : "No concern"}
              </td>
            </tr>
          )}
          {wooldridge && !wooldridge.error && (
            <tr>
              <td className="text-left">Wooldridge Test</td>
              <td>t = {fmt(wooldridge.t_statistic)}</td>
              <td>{wooldridge.df}</td>
              <td>{fmtPval(wooldridge.p_value)}</td>
              <td className={clsx("text-left text-xs", wooldridge.serial_correlation_detected ? "text-red-600" : "text-emerald-700")}>
                {wooldridge.serial_correlation_detected ? "Serial correlation detected" : "No serial correlation"}
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {/* VIF detail */}
      {vif?.values && (
        <div>
          <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wide mb-2">VIF Detail</h3>
          <table className="result-table">
            <thead>
              <tr>
                <th className="text-left">Variable</th>
                <th>VIF</th>
                <th>Assessment</th>
              </tr>
            </thead>
            <tbody>
              {vif.values.filter((v: any) => v.variable !== "const").map((v: any) => {
                const concern = v.vif > 10 ? "Severe" : v.vif > 5 ? "Moderate" : "Acceptable";
                const color   = v.vif > 10 ? "text-red-600" : v.vif > 5 ? "text-amber-600" : "text-emerald-700";
                return (
                  <tr key={v.variable}>
                    <td className="font-mono text-xs text-left">{v.variable}</td>
                    <td>{fmt(v.vif)}</td>
                    <td className={clsx("font-medium", color)}>{concern}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Interpretations */}
      <div className="space-y-2">
        {[hausman, bp, vif, wooldridge].filter(Boolean).map((t: any, i) => (
          t?.interpretation ? (
            <div key={i} className="bg-slate-50 rounded-lg px-4 py-3 text-xs text-slate-600">
              <span className="font-medium text-slate-700">{t.test}: </span>
              {t.interpretation}
            </div>
          ) : null
        ))}
      </div>
      <TableNote text="VIF < 5 acceptable; 5–10 moderate; > 10 severe. BP tests H₀ of homoskedasticity. Wooldridge tests H₀ of no AR(1) serial correlation." />
    </div>
  );
}

// ── Narrative section ────────────────────────────────────────

function NarrativeSection({ text }: { text: string }) {
  return (
    <div className="prose prose-sm max-w-none text-slate-700 leading-relaxed space-y-4">
      {text.split("\n").map((line, i) => {
        if (!line.trim()) return null;
        if (line.startsWith("## ")) return <h3 key={i} className="text-base font-semibold text-slate-800 mt-6 mb-2">{line.slice(3)}</h3>;
        if (line.startsWith("# "))  return <h2 key={i} className="text-lg font-semibold text-slate-800 mt-6 mb-2">{line.slice(2)}</h2>;
        return <p key={i} className="text-sm">{line}</p>;
      })}
    </div>
  );
}

// ── Status banner ────────────────────────────────────────────

function StatusBanner({ status, error }: { status: string; error?: string }) {
  if (status === "completed") return null;
  const cfg: Record<string, any> = {
    pending: { icon: Clock,     color: "bg-amber-50 border-amber-200 text-amber-800",  label: "Queued — analysis will begin shortly" },
    running: { icon: Loader2,   color: "bg-blue-50 border-blue-200 text-blue-800",    label: "Running analysis… this may take up to 2 minutes" },
    failed:  { icon: AlertCircle, color: "bg-red-50 border-red-200 text-red-800",    label: error || "Analysis failed" },
  };
  const c = cfg[status] || cfg.pending;
  const Icon = c.icon;
  return (
    <div className={clsx("flex items-center gap-3 border rounded-xl px-5 py-4 mb-6", c.color)}>
      <Icon size={18} className={status === "running" ? "animate-spin" : ""} />
      <span className="text-sm font-medium">{c.label}</span>
    </div>
  );
}

// ── Main page ────────────────────────────────────────────────

export default function AnalysisPage() {
  const { id } = useParams<{ id: string }>();
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading]   = useState(true);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  const fetchAnalysis = useCallback(async () => {
    try {
      const res = await analysisApi.get(id);
      setAnalysis(res.data);
      return res.data.status;
    } catch {
      toast.error("Failed to load analysis");
      return "failed";
    }
  }, [id]);

  // Poll while pending/running
  useEffect(() => {
    let cancelled = false;

    async function poll() {
      setLoading(true);
      const status = await fetchAnalysis();
      setLoading(false);

      if (["pending", "running"].includes(status) && !cancelled) {
        pollRef.current = setTimeout(async () => {
          if (!cancelled) {
            await fetchAnalysis();
            // Keep polling
            if (!cancelled) pollRef.current = setTimeout(poll, 5000);
          }
        }, 5000);
      }
    }

    poll();
    return () => {
      cancelled = true;
      if (pollRef.current) clearTimeout(pollRef.current);
    };
  }, [fetchAnalysis]);

  // Re-poll if still running
  useEffect(() => {
    if (!analysis) return;
    if (["pending", "running"].includes(analysis.status)) {
      const t = setTimeout(() => fetchAnalysis(), 5000);
      return () => clearTimeout(t);
    }
  }, [analysis, fetchAnalysis]);

  async function handleDownload() {
    try {
      const res = await analysisApi.downloadReport(id);
      const url = URL.createObjectURL(new Blob([res.data]));
      const a   = document.createElement("a");
      a.href     = url;
      a.download = `${analysis.title}_panel_report.docx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Download failed — please try again");
    }
  }

  const isReady = analysis?.status === "completed";
  const isRunning = ["pending", "running"].includes(analysis?.status);

  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 p-8 max-w-6xl">
          {loading && !analysis ? (
            <div className="flex justify-center py-32">
              <Loader2 size={28} className="animate-spin text-brand-500" />
            </div>
          ) : analysis ? (
            <>
              {/* Header */}
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h1 className="text-xl font-semibold text-slate-800">{analysis.title}</h1>
                  <p className="text-sm text-slate-500 mt-1">
                    Dependent: <span className="font-mono text-brand-500">{analysis.dependent_var}</span>
                    {" · "}
                    Models: {analysis.models?.join(", ")}
                    {" · "}
                    {new Date(analysis.created_at).toLocaleDateString("en-GB", { day:"numeric", month:"short", year:"numeric" })}
                  </p>
                </div>
                {isReady && analysis.has_report && (
                  <button
                    onClick={handleDownload}
                    className="flex items-center gap-2 bg-brand-500 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-brand-600 transition-colors"
                  >
                    <Download size={15} /> Download Word Report
                  </button>
                )}
              </div>

              <StatusBanner status={analysis.status} error={analysis.error} />

              {/* Results — shown when completed */}
              {isReady && (
                <>
                  {/* Descriptive stats */}
                  {analysis.descriptive_stats && (
                    <Section title="1. Descriptive Statistics">
                      <DescriptiveTable data={analysis.descriptive_stats} />
                    </Section>
                  )}

                  {/* Correlation */}
                  {analysis.correlation_matrix && (
                    <Section title="2. Pearson Correlation Matrix">
                      <CorrelationTable data={analysis.correlation_matrix} />
                    </Section>
                  )}

                  {/* Regression results */}
                  {analysis.regression_results && (
                    <Section title="3. Regression Results">
                      {Object.entries(analysis.regression_results).map(([key, modelData]: [string, any]) => (
                        <RegressionTable key={key} modelKey={key} data={modelData} />
                      ))}
                    </Section>
                  )}

                  {/* Diagnostics */}
                  {analysis.diagnostic_results && Object.keys(analysis.diagnostic_results).length > 0 && (
                    <Section title="4. Diagnostic Tests">
                      <DiagnosticsPanel data={analysis.diagnostic_results} />
                    </Section>
                  )}

                  {/* LLM Narrative */}
                  {analysis.llm_narrative && (
                    <Section title="5. AI-Written Results & Discussion">
                      <NarrativeSection text={analysis.llm_narrative} />
                    </Section>
                  )}

                  {/* Download CTA at bottom */}
                  {analysis.has_report && (
                    <div className="bg-brand-50 border border-brand-100 rounded-xl p-6 flex items-center justify-between mt-6">
                      <div className="flex items-center gap-3">
                        <FileText size={20} className="text-brand-500" />
                        <div>
                          <p className="text-sm font-medium text-slate-800">Full Word report ready</p>
                          <p className="text-xs text-slate-500 mt-0.5">
                            Includes all tables, diagnostics, and AI discussion — formatted for academic submission
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={handleDownload}
                        className="flex items-center gap-2 bg-brand-500 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-brand-600 transition-colors"
                      >
                        <Download size={15} /> Download .docx
                      </button>
                    </div>
                  )}
                </>
              )}

              {/* Running placeholder cards */}
              {isRunning && (
                <div className="space-y-4 mt-4">
                  {["Descriptive Statistics", "Correlation Matrix", "Regression Results", "Diagnostics"].map((label) => (
                    <div key={label} className="bg-white border border-slate-200 rounded-xl p-6 animate-pulse">
                      <div className="h-4 bg-slate-100 rounded w-48 mb-4" />
                      <div className="space-y-2">
                        <div className="h-3 bg-slate-100 rounded w-full" />
                        <div className="h-3 bg-slate-100 rounded w-5/6" />
                        <div className="h-3 bg-slate-100 rounded w-4/6" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="flex flex-col items-center justify-center py-32 text-center">
              <AlertCircle size={32} className="text-red-400 mb-4" />
              <p className="text-slate-600">Analysis not found</p>
            </div>
          )}
        </main>
      </div>
    </AuthGuard>
  );
}
