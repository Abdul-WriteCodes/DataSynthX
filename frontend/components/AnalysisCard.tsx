"use client";
import Link from "next/link";
import { CheckCircle, Clock, AlertCircle, Loader2, FileText } from "lucide-react";
import clsx from "clsx";

interface Props {
  id: string;
  title: string;
  dependent_var: string;
  models: string[];
  status: "pending" | "running" | "completed" | "failed";
  created_at: string;
  has_report: boolean;
}

const statusConfig = {
  pending:   { label: "Pending",   icon: Clock,      color: "text-amber-500 bg-amber-50"  },
  running:   { label: "Running",   icon: Loader2,    color: "text-blue-500 bg-blue-50"    },
  completed: { label: "Completed", icon: CheckCircle, color: "text-emerald-600 bg-emerald-50" },
  failed:    { label: "Failed",    icon: AlertCircle, color: "text-red-500 bg-red-50"      },
};

export default function AnalysisCard({ id, title, dependent_var, models, status, created_at, has_report }: Props) {
  const cfg = statusConfig[status] || statusConfig.pending;
  const Icon = cfg.icon;

  return (
    <Link href={`/analysis/${id}`}>
      <div className="bg-white border border-slate-200 rounded-xl p-4 hover:shadow-md hover:border-brand-100 transition-all cursor-pointer">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-slate-800 truncate">{title}</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Dependent: <span className="font-mono text-brand-500">{dependent_var}</span>
            </p>
          </div>
          <span className={clsx("flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full", cfg.color)}>
            <Icon size={12} className={status === "running" ? "animate-spin" : ""} />
            {cfg.label}
          </span>
        </div>

        <div className="flex items-center gap-2 mt-3 flex-wrap">
          {models.map((m) => (
            <span key={m} className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">
              {m}
            </span>
          ))}
        </div>

        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-slate-400">
            {new Date(created_at).toLocaleDateString("en-GB", {
              day: "numeric", month: "short", year: "numeric",
            })}
          </span>
          {has_report && (
            <span className="flex items-center gap-1 text-xs text-brand-500">
              <FileText size={12} /> Report ready
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
