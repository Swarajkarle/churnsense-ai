"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { customerApi } from "@/lib/api";
import type { Customer } from "@/types";
import Link from "next/link";
import { Search, ChevronLeft, ChevronRight, ExternalLink, Users } from "lucide-react";
import { clsx } from "clsx";

/**
 * ChurnSense AI — Customer Management Page
 * Searchable, filterable, paginated customer table.
 */
export default function CustomersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("");
  const PAGE_SIZE = 20;

  const { data, isLoading } = useQuery<Customer[]>({
    queryKey: ["customers", page, search, riskFilter],
    queryFn: () =>
      customerApi.list(page, PAGE_SIZE, search || undefined, riskFilter || undefined)
        .then((r) => r.data),
  });

  const customers = data || [];

  return (
    <div className="p-8 animate-fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">Customer Management</h1>
          <p className="section-subtitle">View, search, and analyze your customer base</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <div className="relative flex-1 min-w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            id="customer-search"
            placeholder="Search by name, ID, or email…"
            className="form-input pl-10"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        <select
          id="risk-filter"
          className="form-input w-44"
          value={riskFilter}
          onChange={(e) => { setRiskFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Risk Levels</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Table */}
      <div className="glass-card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Customer ID</th>
                <th>Name</th>
                <th>Tenure</th>
                <th>Contract</th>
                <th>Monthly Charges</th>
                <th>Payment Method</th>
                <th>Churn Status</th>
                <th>Latest Risk</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 9 }).map((_, j) => (
                      <td key={j}>
                        <div className="skeleton h-4 rounded w-full" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : customers.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-16">
                    <Users className="w-10 h-10 text-slate-600 mx-auto mb-3" />
                    <p className="text-sm text-slate-400">No customers found</p>
                    <p className="text-xs text-slate-500 mt-1">
                      Upload a dataset and run predictions to populate customers.
                    </p>
                  </td>
                </tr>
              ) : (
                customers.map((c) => (
                  <tr key={c.id}>
                    <td className="font-mono text-xs text-slate-400">{c.external_id || c.id.slice(0, 8)}</td>
                    <td className="font-medium text-white">{c.name || "—"}</td>
                    <td>{c.tenure !== undefined ? `${c.tenure} mo` : "—"}</td>
                    <td>
                      <span className="text-xs text-slate-300">{c.contract_type || "—"}</span>
                    </td>
                    <td>
                      {c.monthly_charges !== undefined
                        ? `₹${c.monthly_charges.toFixed(2)}`
                        : "—"}
                    </td>
                    <td className="text-xs text-slate-400">{c.payment_method || "—"}</td>
                    <td>
                      {c.churn_label !== undefined ? (
                        <span className={clsx("risk-badge", c.churn_label ? "risk-badge-high" : "risk-badge-low")}>
                          {c.churn_label ? "Churned" : "Active"}
                        </span>
                      ) : "—"}
                    </td>
                    <td>
                      {c.latest_prediction?.risk_level ? (
                        <span className={`risk-badge risk-badge-${c.latest_prediction.risk_level}`}>
                          {c.latest_prediction.risk_level}
                        </span>
                      ) : "—"}
                    </td>
                    <td>
                      <Link
                        href={`/dashboard/customers/${c.id}`}
                        className="inline-flex items-center gap-1 text-xs text-brand-400 hover:text-brand-300 transition-colors"
                      >
                        View <ExternalLink className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-surface-border">
          <span className="text-xs text-slate-400">
            Page {page} · {customers.length} results
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="btn-secondary text-xs py-1.5 px-3"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => customers.length === PAGE_SIZE && setPage(page + 1)}
              disabled={customers.length < PAGE_SIZE}
              className="btn-secondary text-xs py-1.5 px-3"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
