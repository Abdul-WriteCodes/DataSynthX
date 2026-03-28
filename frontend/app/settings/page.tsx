"use client";
import { useState } from "react";
import toast from "react-hot-toast";
import AuthGuard from "../../components/AuthGuard";
import Sidebar from "../../components/Sidebar";
import { getUser } from "../../lib/auth";

export default function SettingsPage() {
  const user = getUser();
  const [copied, setCopied] = useState(false);

  function copyEmail() {
    if (user?.email) {
      navigator.clipboard.writeText(user.email);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast.success("Email copied");
    }
  }

  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 p-8 max-w-2xl">
          <h1 className="text-xl font-semibold text-slate-800 mb-1">Settings</h1>
          <p className="text-sm text-slate-500 mb-8">Your account details</p>

          <div className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
            <div className="px-6 py-4 flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-500 mb-0.5">Account email</p>
                <p className="text-sm font-medium text-slate-800">{user?.email || "—"}</p>
              </div>
              <button
                onClick={copyEmail}
                className="text-xs text-brand-500 hover:underline"
              >
                {copied ? "Copied!" : "Copy"}
              </button>
            </div>
            <div className="px-6 py-4">
              <p className="text-xs text-slate-500 mb-0.5">User ID</p>
              <p className="text-xs font-mono text-slate-500">{user?.id || "—"}</p>
            </div>
            <div className="px-6 py-4">
              <p className="text-xs text-slate-500 mb-1">Platform</p>
              <p className="text-sm text-slate-700">PanelStat — Panel Data Regression SaaS</p>
              <p className="text-xs text-slate-400 mt-0.5">
                Supports FE, RE, Pooled OLS, Between Effects · Hausman, Breusch-Pagan, VIF, Wooldridge
              </p>
            </div>
          </div>

          <div className="mt-6 bg-amber-50 border border-amber-200 rounded-xl px-5 py-4 text-sm text-amber-800">
            To change your password or delete your account, please use your Supabase email confirmation link or contact support.
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
