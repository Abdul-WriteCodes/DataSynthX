"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import AuthGuard from "../../components/AuthGuard";
import Sidebar from "../../components/Sidebar";
import UploadBox from "../../components/UploadBox";
import { datasetApi, analysisApi } from "../../lib/api";
import { ChevronRight, ChevronLeft, Loader2 } from "lucide-react";
import clsx from "clsx";

const MODELS = [
  { key: "FE",   label: "Fixed Effects",   desc: "Controls for time-invariant entity heterogeneity" },
  { key: "RE",   label: "Random Effects",  desc: "Assumes entity effects are uncorrelated with regressors" },
  { key: "POLS", label: "Pooled OLS",      desc: "Standard OLS ignoring panel structure" },
  { key: "BE",   label: "Between Effects", desc: "Regression on entity means across time" },
];

const DIAGNOSTICS = [
  { key: "HAUSMAN",    label: "Hausman Test",         desc: "FE vs RE — requires both models selected", requiresBoth: true },
  { key: "BP",         label: "Breusch-Pagan Test",   desc: "Tests for heteroskedasticity" },
  { key: "VIF",        label: "VIF",                  desc: "Variance Inflation Factor — multicollinearity" },
  { key: "WOOLDRIDGE", label: "Wooldridge Test",      desc: "Serial correlation in panel residuals" },
];

type Step = "upload" | "configure" | "confirm";

export default function UploadPage() {
  const router = useRouter();

  // Step state
  const [step, setStep] = useState<Step>("upload");

  // Upload step
  const [file, setFile]           = useState<File | null>(null);
  const [entityCol, setEntityCol] = useState("");
  const [timeCol, setTimeCol]     = useState("");
  const [uploading, setUploading] = useState(false);
  const [dataset, setDataset]     = useState<any>(null);

  // Configure step
  const [title, setTitle]           = useState("");
  const [dependentVar, setDependentVar] = useState("");
  const [independentVars, setIndependentVars] = useState<string[]>([]);
  const [controlVars, setControlVars]         = useState<string[]>([]);
  const [selectedModels, setSelectedModels]   = useState<string[]>(["FE", "RE"]);
  const [selectedDiags, setSelectedDiags]     = useState<string[]>(["HAUSMAN", "BP", "VIF"]);

  // Submit
  const [submitting, setSubmitting] = useState(false);

  const availableVars: string[] = dataset
    ? (dataset.columns as string[]).filter(
        (c: string) => c !== dataset.entity_col && c !== dataset.time_col
      )
    : [];

  const unusedVars = availableVars.filter(
    (v) => v !== dependentVar && !independentVars.includes(v) && !controlVars.includes(v)
  );

  // ── Upload step ───────────────────────────────────────────

  async function handleUpload() {
    if (!file) { toast.error("Please select a file"); return; }
    if (!entityCol.trim()) { toast.error("Enter the entity column name"); return; }
    if (!timeCol.trim())   { toast.error("Enter the time column name"); return; }

    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("entity_col", entityCol.trim());
      fd.append("time_col", timeCol.trim());
      const res = await datasetApi.upload(fd);
      setDataset(res.data);
      toast.success("Dataset uploaded successfully");
      setStep("configure");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  // ── Analysis submission ───────────────────────────────────

  async function handleSubmit() {
    if (!title.trim())         { toast.error("Enter a study title"); return; }
    if (!dependentVar)         { toast.error("Select a dependent variable"); return; }
    if (independentVars.length === 0) { toast.error("Select at least one independent variable"); return; }
    if (selectedModels.length === 0)  { toast.error("Select at least one model"); return; }
    if (selectedDiags.includes("HAUSMAN") && !(selectedModels.includes("FE") && selectedModels.includes("RE"))) {
      toast.error("Hausman test requires both Fixed Effects and Random Effects");
      return;
    }

    setSubmitting(true);
    try {
      const res = await analysisApi.create({
        dataset_id: dataset.dataset_id,
        title: title.trim(),
        dependent_var: dependentVar,
        independent_vars: independentVars,
        control_vars: controlVars,
        models: selectedModels,
        diagnostics: selectedDiags,
      });
      toast.success("Analysis queued! Redirecting…");
      router.push(`/analysis/${res.data.analysis_id}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to start analysis");
    } finally {
      setSubmitting(false);
    }
  }

  // ── Toggle helpers ────────────────────────────────────────

  function toggleArr(arr: string[], setArr: (v: string[]) => void, val: string) {
    setArr(arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val]);
  }

  function assignRole(v: string, role: "dependent" | "independent" | "control" | "none") {
    setDependentVar((dep) => dep === v && role !== "dependent" ? "" : dep);
    setIndependentVars((iv) => role === "independent" ? [...iv.filter((x) => x !== v), v] : iv.filter((x) => x !== v));
    setControlVars((cv) => role === "control" ? [...cv.filter((x) => x !== v), v] : cv.filter((x) => x !== v));
    if (role === "dependent") {
      setDependentVar(v);
      setIndependentVars((iv) => iv.filter((x) => x !== v));
      setControlVars((cv) => cv.filter((x) => x !== v));
    }
  }

  function varRole(v: string): string {
    if (v === dependentVar) return "dependent";
    if (independentVars.includes(v)) return "independent";
    if (controlVars.includes(v)) return "control";
    return "none";
  }

  // ── Render ────────────────────────────────────────────────

  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 p-8 max-w-4xl">
          {/* Progress indicator */}
          <div className="flex items-center gap-2 mb-8">
            {(["upload", "configure", "confirm"] as Step[]).map((s, i) => (
              <div key={s} className="flex items-center gap-2">
                <div className={clsx(
                  "w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium",
                  step === s ? "bg-brand-500 text-white" :
                  (["upload","configure","confirm"].indexOf(step) > i) ? "bg-emerald-500 text-white" :
                  "bg-slate-200 text-slate-500"
                )}>
                  {i + 1}
                </div>
                <span className={clsx("text-sm capitalize", step === s ? "text-slate-800 font-medium" : "text-slate-400")}>
                  {s === "upload" ? "Upload dataset" : s === "configure" ? "Configure analysis" : "Review & run"}
                </span>
                {i < 2 && <ChevronRight size={14} className="text-slate-300 ml-1" />}
              </div>
            ))}
          </div>

          {/* ── STEP 1: Upload ── */}
          {step === "upload" && (
            <div className="space-y-6">
              <div>
                <h1 className="text-xl font-semibold text-slate-800">Upload your dataset</h1>
                <p className="text-sm text-slate-500 mt-1">CSV or Excel file with entity and time identifiers</p>
              </div>

              <UploadBox
                onFileSelected={setFile}
                selectedFile={file}
                onClear={() => setFile(null)}
              />

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">
                    Entity column <span className="text-slate-400 font-normal">(e.g. Company, Firm)</span>
                  </label>
                  <input
                    value={entityCol} onChange={(e) => setEntityCol(e.target.value)}
                    placeholder="Company"
                    className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">
                    Time column <span className="text-slate-400 font-normal">(e.g. Year, Quarter)</span>
                  </label>
                  <input
                    value={timeCol} onChange={(e) => setTimeCol(e.target.value)}
                    placeholder="Year"
                    className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              </div>

              <button
                onClick={handleUpload} disabled={uploading || !file}
                className="flex items-center gap-2 bg-brand-500 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-brand-600 disabled:opacity-50 transition-colors"
              >
                {uploading ? <><Loader2 size={15} className="animate-spin" /> Uploading…</> : <>Next <ChevronRight size={15} /></>}
              </button>
            </div>
          )}

          {/* ── STEP 2: Configure ── */}
          {step === "configure" && dataset && (
            <div className="space-y-8">
              <div>
                <h1 className="text-xl font-semibold text-slate-800">Configure analysis</h1>
                <p className="text-sm text-slate-500 mt-1">
                  {dataset.rows} rows · {dataset.columns.length} columns · Entity: <span className="font-mono text-brand-500">{dataset.entity_col}</span> · Time: <span className="font-mono text-brand-500">{dataset.time_col}</span>
                </p>
              </div>

              {/* Study title */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Study title</label>
                <input
                  value={title} onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. ESG and Firm Performance: Panel Evidence"
                  className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              {/* Variable assignment */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Assign variable roles
                </label>
                <div className="border border-slate-200 rounded-xl overflow-hidden">
                  <div className="grid grid-cols-5 bg-slate-50 border-b border-slate-200 px-4 py-2 text-xs font-medium text-slate-500 uppercase tracking-wide">
                    <span className="col-span-2">Variable</span>
                    <span className="text-center">Dependent</span>
                    <span className="text-center">Independent</span>
                    <span className="text-center">Control</span>
                  </div>
                  {availableVars.map((v, i) => (
                    <div key={v} className={clsx(
                      "grid grid-cols-5 px-4 py-3 items-center border-b border-slate-100 last:border-0",
                      i % 2 === 0 ? "bg-white" : "bg-slate-50/50"
                    )}>
                      <span className="col-span-2 font-mono text-sm text-slate-700">{v}</span>
                      {(["dependent", "independent", "control"] as const).map((role) => (
                        <div key={role} className="flex justify-center">
                          <input
                            type={role === "dependent" ? "radio" : "checkbox"}
                            name={role === "dependent" ? `dep_${v}` : undefined}
                            checked={varRole(v) === role}
                            onChange={() => assignRole(v, varRole(v) === role ? "none" : role)}
                            className="accent-brand-500 w-4 h-4 cursor-pointer"
                          />
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
                {/* Role summary */}
                <div className="flex gap-4 mt-3 text-xs text-slate-500">
                  <span>Dependent: <strong className="text-slate-700">{dependentVar || "—"}</strong></span>
                  <span>Independent: <strong className="text-slate-700">{independentVars.join(", ") || "—"}</strong></span>
                  {controlVars.length > 0 && <span>Controls: <strong className="text-slate-700">{controlVars.join(", ")}</strong></span>}
                </div>
              </div>

              {/* Models */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">Regression models</label>
                <div className="grid grid-cols-2 gap-3">
                  {MODELS.map(({ key, label, desc }) => (
                    <button
                      key={key} type="button"
                      onClick={() => toggleArr(selectedModels, setSelectedModels, key)}
                      className={clsx(
                        "text-left p-4 rounded-xl border-2 transition-all",
                        selectedModels.includes(key)
                          ? "border-brand-500 bg-brand-50"
                          : "border-slate-200 hover:border-slate-300"
                      )}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-sm text-slate-800">{label}</span>
                        <span className="font-mono text-xs text-slate-400">{key}</span>
                      </div>
                      <p className="text-xs text-slate-500">{desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Diagnostics */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">Diagnostic tests</label>
                <div className="grid grid-cols-2 gap-3">
                  {DIAGNOSTICS.map(({ key, label, desc, requiresBoth }) => {
                    const disabled = key === "HAUSMAN" && !(selectedModels.includes("FE") && selectedModels.includes("RE"));
                    return (
                      <button
                        key={key} type="button" disabled={disabled}
                        onClick={() => !disabled && toggleArr(selectedDiags, setSelectedDiags, key)}
                        className={clsx(
                          "text-left p-4 rounded-xl border-2 transition-all",
                          disabled ? "opacity-40 cursor-not-allowed border-slate-100" :
                          selectedDiags.includes(key)
                            ? "border-brand-500 bg-brand-50"
                            : "border-slate-200 hover:border-slate-300"
                        )}
                      >
                        <span className="font-medium text-sm text-slate-800 block mb-1">{label}</span>
                        <p className="text-xs text-slate-500">{desc}</p>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep("upload")}
                  className="flex items-center gap-2 border border-slate-200 text-slate-600 px-5 py-2.5 rounded-lg text-sm hover:bg-slate-50 transition-colors"
                >
                  <ChevronLeft size={15} /> Back
                </button>
                <button
                  onClick={() => {
                    if (!title.trim()) { toast.error("Enter a study title"); return; }
                    if (!dependentVar) { toast.error("Select a dependent variable"); return; }
                    if (independentVars.length === 0) { toast.error("Select at least one independent variable"); return; }
                    setStep("confirm");
                  }}
                  className="flex items-center gap-2 bg-brand-500 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-brand-600 transition-colors"
                >
                  Review <ChevronRight size={15} />
                </button>
              </div>
            </div>
          )}

          {/* ── STEP 3: Confirm ── */}
          {step === "confirm" && (
            <div className="space-y-6">
              <div>
                <h1 className="text-xl font-semibold text-slate-800">Review & run</h1>
                <p className="text-sm text-slate-500 mt-1">Confirm your analysis configuration</p>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
                {[
                  { label: "Study title",          value: title },
                  { label: "Dataset",              value: `${dataset?.filename} (${dataset?.rows} rows)` },
                  { label: "Entity column",        value: dataset?.entity_col },
                  { label: "Time column",          value: dataset?.time_col },
                  { label: "Dependent variable",   value: dependentVar },
                  { label: "Independent variables", value: independentVars.join(", ") },
                  { label: "Control variables",    value: controlVars.join(", ") || "None" },
                  { label: "Models",               value: selectedModels.join(", ") },
                  { label: "Diagnostics",          value: selectedDiags.join(", ") || "None" },
                ].map(({ label, value }) => (
                  <div key={label} className="flex items-start px-5 py-3 gap-4">
                    <span className="text-sm text-slate-500 w-44 shrink-0">{label}</span>
                    <span className="text-sm font-medium text-slate-800">{value}</span>
                  </div>
                ))}
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-xl px-5 py-4 text-sm text-amber-800">
                Analysis typically takes 30–120 seconds depending on dataset size and selected models.
                You can close this page — results will be saved to your dashboard.
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep("configure")}
                  className="flex items-center gap-2 border border-slate-200 text-slate-600 px-5 py-2.5 rounded-lg text-sm hover:bg-slate-50 transition-colors"
                >
                  <ChevronLeft size={15} /> Back
                </button>
                <button
                  onClick={handleSubmit} disabled={submitting}
                  className="flex items-center gap-2 bg-brand-500 text-white px-8 py-2.5 rounded-lg text-sm font-medium hover:bg-brand-600 disabled:opacity-60 transition-colors"
                >
                  {submitting
                    ? <><Loader2 size={15} className="animate-spin" /> Starting analysis…</>
                    : "Run analysis"}
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </AuthGuard>
  );
}
