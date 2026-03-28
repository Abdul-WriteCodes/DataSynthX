"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, Upload, BarChart2, Settings, LogOut } from "lucide-react";
import { clearSession } from "../lib/auth";
import { authApi } from "../lib/api";
import clsx from "clsx";

const nav = [
  { href: "/dashboard", label: "Dashboard",  icon: LayoutDashboard },
  { href: "/upload",    label: "New Analysis", icon: Upload },
  { href: "/settings",  label: "Settings",    icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router   = useRouter();

  async function handleLogout() {
    try { await authApi.logout(); } catch {}
    clearSession();
    router.push("/auth/login");
  }

  return (
    <aside className="w-56 min-h-screen bg-white border-r border-slate-200 flex flex-col">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-100">
        <span className="text-brand-500 font-semibold text-lg tracking-tight">PanelStat</span>
        <p className="text-xs text-slate-400 mt-0.5">Panel Regression Platform</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {nav.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              "flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors",
              pathname.startsWith(href)
                ? "bg-brand-50 text-brand-500 font-medium"
                : "text-slate-600 hover:bg-slate-50"
            )}
          >
            <Icon size={16} />
            {label}
          </Link>
        ))}
      </nav>

      {/* Logout */}
      <div className="px-3 py-4 border-t border-slate-100">
        <button
          onClick={handleLogout}
          className="flex items-center gap-2.5 px-3 py-2 w-full rounded-lg text-sm text-slate-500 hover:bg-red-50 hover:text-red-600 transition-colors"
        >
          <LogOut size={16} />
          Sign out
        </button>
      </div>
    </aside>
  );
}
