"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuthStore } from "@/lib/store";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import {
  LayoutDashboard, Users, Database, Brain, TrendingDown,
  BarChart3, FileText, Settings, LogOut, ChevronRight,
  User, History, Lightbulb,
} from "lucide-react";
import { clsx } from "clsx";

const NAV_ITEMS = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/dashboard/customers", icon: Users, label: "Customers" },
  { href: "/dashboard/datasets", icon: Database, label: "Datasets" },
  { href: "/dashboard/models", icon: Brain, label: "Models" },
  { href: "/dashboard/predictions", icon: TrendingDown, label: "Predictions" },
  { href: "/dashboard/analytics", icon: BarChart3, label: "Analytics" },
  { href: "/dashboard/recommendations", icon: Lightbulb, label: "Recommendations" },
  { href: "/dashboard/history", icon: History, label: "History" },
  { href: "/dashboard/reports", icon: FileText, label: "Reports" },
];

const BOTTOM_ITEMS = [
  { href: "/dashboard/settings", icon: Settings, label: "Settings" },
  { href: "/dashboard/profile", icon: User, label: "Profile" },
];

/**
 * ChurnSense AI — Application Sidebar
 * Original navigation layout with brand identity.
 */
export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, clearAuth } = useAuthStore();

  const handleLogout = () => {
    clearAuth();
    toast.success("Signed out successfully");
    router.push("/login");
  };

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r border-surface-border bg-surface-card flex flex-col z-40">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-surface-border">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 overflow-hidden shadow-brand">
          <Image
            src="/logo.png"
            alt="ChurnSense AI"
            width={32}
            height={32}
            className="w-full h-full object-contain"
          />
        </div>
        <div>
          <div className="text-sm font-bold text-white">ChurnSense AI</div>
          <div className="text-xs text-slate-500">Churn Intelligence</div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ href, icon: Icon, label }) => {
          const isActive = pathname === href || (href !== "/dashboard" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={clsx("nav-item", { active: isActive })}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span className="flex-1">{label}</span>
              {isActive && <ChevronRight className="w-3 h-3 text-brand-400" />}
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="border-t border-surface-border px-3 py-3 space-y-1">
        {BOTTOM_ITEMS.map(({ href, icon: Icon, label }) => (
          <Link key={href} href={href} className={clsx("nav-item", { active: pathname === href })}>
            <Icon className="w-4 h-4 flex-shrink-0" />
            <span>{label}</span>
          </Link>
        ))}

        {/* User info + logout */}
        <div className="mt-2 pt-2 border-t border-surface-border">
          <div className="flex items-center gap-2 px-3 py-2">
            <div className="w-7 h-7 rounded-full bg-gradient-brand flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
              {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || "?"}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium text-slate-200 truncate">
                {user?.full_name || user?.email}
              </div>
              <div className="text-xs text-slate-500 truncate capitalize">{user?.role}</div>
            </div>
            <button
              onClick={handleLogout}
              title="Sign out"
              className="p-1 text-slate-500 hover:text-red-400 transition-colors flex-shrink-0"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
}
