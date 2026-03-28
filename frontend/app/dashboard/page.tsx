"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, BarChart2 } from "lucide-react";
import AuthGuard from "../../components/AuthGuard";
import Sidebar from "../../components/Sidebar";
import AnalysisCard from "../../components/AnalysisCard";
import { analysisApi } from "../../lib/api";

export default function DashboardPage() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    analysisApi.list()
      .then((res) => setAnalyses(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-xl font-semibold text-slate-800">Dashboard</h1>
              <p className="text-sm text-slate-500 mt-0.5">All your panel regression analyses</p>
            </div>
            <Link
              href="/upload"
              className="flex items-center gap-2 bg-brand-500 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-brand-600 transition-colors"
            >
              <Plus size={16} /> New analysis
            </Link>
          </div>

          {/* Stats bar */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            {[
              { label: "Total analyses", value: analyses.length },
              { label: "Completed", value: analyses.filter((a) => a.status === "completed").length },
              { label: "In progress", value: analyses.filter((a) => ["pending", "running"].includes(a.status)).length },
            ].map(({ label, value }) => (
              <div key={label} className="bg-white border border-slate-200 rounded-xl p-4">
                <p className="text-xs text-slate-500">{label}</p>
                <p className="text-2xl font-semibold text-slate-800 mt-1">{value}</p>
              </div>
            ))}
          </div>

          {/* Analysis list */}
          {loading ? (
            <div className="flex justify-center py-20">
              <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : analyses.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 text-center">
              <BarChart2 size={40} className="text-slate-300 mb-4" />
              <p className="text-slate-600 font-medium">No analyses yet</p>
              <p className="text-sm text-slate-400 mt-1 mb-6">Upload a dataset to run your first panel regression</p>
              <Link href="/upload" className="bg-brand-500 text-white text-sm px-5 py-2 rounded-lg hover:bg-brand-600 transition-colors">
                Get started
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {analyses.map((a) => (
                <AnalysisCard key={a.id} {...a} />
              ))}
            </div>
          )}
        </main>
      </div>
    </AuthGuard>
  );
}
