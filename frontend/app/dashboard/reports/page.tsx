"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { reportApi } from "@/lib/api";
import type { Report } from "@/types";
import { toast } from "sonner";
import { FileText, Plus, Loader2, Download } from "lucide-react";

export default function ReportsPage() {
  const [generating, setGenerating] = useState(false);
  const { data: reports = [], refetch } = useQuery<Report[]>({
    queryKey: ["reports"],
    queryFn: () => reportApi.list().then((r) => r.data),
  });

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await reportApi.generate({ title: `Churn Report — ${new Date().toLocaleDateString("en-IN")}`, report_type: "overview" });
      toast.success("Report generated!");
      refetch();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Report generation failed");
    } finally { setGenerating(false); }
  };

  const handleExport = (report: Report) => {
    const blob = new Blob([JSON.stringify(report.content, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `churnsense-report-${report.id.slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Report downloaded as JSON");
  };

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">Reports</h1>
          <p className="section-subtitle">Generate and export analytics reports</p>
        </div>
        <button onClick={handleGenerate} disabled={generating} className="btn-primary">
          {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
          {generating ? "Generating…" : "Generate Report"}
        </button>
      </div>

      {reports.length === 0 ? (
        <div className="glass-card text-center py-16">
          <FileText className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <p className="text-sm text-slate-400">No reports generated yet</p>
          <p className="text-xs text-slate-500 mt-1">Click &quot;Generate Report&quot; to create your first analytics report.</p>
        </div>
      ) : (
        <div className="glass-card p-0 overflow-hidden">
          <table className="data-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Type</th>
                <th>Generated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.id}>
                  <td className="font-medium text-white">{r.title}</td>
                  <td className="text-xs text-slate-400 capitalize">{r.report_type}</td>
                  <td className="text-xs text-slate-400">{new Date(r.created_at).toLocaleDateString("en-IN")}</td>
                  <td>
                    <button onClick={() => handleExport(r)} className="btn-secondary text-xs py-1.5 px-3">
                      <Download className="w-3.5 h-3.5" /> Export JSON
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
