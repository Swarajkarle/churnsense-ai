"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useRef } from "react";
import { datasetApi } from "@/lib/api";
import type { Dataset } from "@/types";
import { toast } from "sonner";
import { Upload, Trash2, Eye, CheckCircle, AlertTriangle, Database, Loader2 } from "lucide-react";
import { clsx } from "clsx";

/**
 * ChurnSense AI — Dataset Management Page
 * Handles CSV upload, validation initiation, and preprocessing config.
 */
export default function DatasetsPage() {
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [datasetName, setDatasetName] = useState("");
  const [description, setDescription] = useState("");
  const [selectedFileName, setSelectedFileName] = useState("");
  const [validatingId, setValidatingId] = useState<string | null>(null);

  const { data: datasets = [], isLoading } = useQuery<Dataset[]>({
    queryKey: ["datasets"],
    queryFn: () => datasetApi.list().then((r) => r.data),
  });

  const handleUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) { toast.error("Please select a CSV file"); return; }
    if (!datasetName.trim()) { toast.error("Please enter a dataset name"); return; }
    setUploading(true);
    try {
      await datasetApi.upload(file, datasetName, description);
      toast.success("Dataset uploaded successfully!");
      qc.invalidateQueries({ queryKey: ["datasets"] });
      setDatasetName(""); setDescription(""); setSelectedFileName("");
      if (fileRef.current) fileRef.current.value = "";
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Upload failed");
    } finally { setUploading(false); }
  };

  const handleValidate = async (id: string) => {
    setValidatingId(id);
    try {
      const res = await datasetApi.validate(id);
      const report = res.data;
      toast.success(`Validation complete! Quality score: ${report.quality_score?.toFixed(1)}`);
      qc.invalidateQueries({ queryKey: ["datasets"] });
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Validation failed");
    } finally { setValidatingId(null); }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Delete this dataset? This action cannot be undone.")) return;
    try {
      await datasetApi.delete(id);
      toast.success("Dataset deleted");
      qc.invalidateQueries({ queryKey: ["datasets"] });
    } catch {
      toast.error("Delete failed");
    }
  };

  const statusColor: Record<string, string> = {
    uploaded: "text-slate-400",
    validated: "text-emerald-400",
    ready: "text-brand-400",
    error: "text-red-400",
  };

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">Dataset Management</h1>
          <p className="section-subtitle">Upload, validate, and prepare datasets for model training</p>
        </div>
      </div>

      {/* Upload Card */}
      <div className="glass-card">
        <h2 className="text-sm font-semibold text-white mb-5 flex items-center gap-2">
          <Upload className="w-4 h-4 text-brand-400" />
          Upload New Dataset
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Dataset Name</label>
            <input
              id="dataset-name"
              type="text"
              placeholder="e.g. Q3 2026 Customer Data"
              className="form-input"
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Description (optional)</label>
            <input
              type="text"
              placeholder="Brief description of this dataset"
              className="form-input"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
        </div>
        <div className="flex items-center gap-4">
          <label
            htmlFor="csv-file-input"
            className="btn-secondary cursor-pointer flex items-center gap-2"
          >
            <Upload className="w-4 h-4" />
            <span className="truncate max-w-xs">{selectedFileName || "Choose CSV"}</span>
            <input
              id="csv-file-input"
              ref={fileRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) {
                  setSelectedFileName(f.name);
                  if (!datasetName) {
                    setDatasetName(f.name.replace(/\.[^/.]+$/, ""));
                  }
                }
              }}
            />
          </label>
          <button
            id="upload-btn"
            onClick={handleUpload}
            disabled={uploading}
            className="btn-primary"
          >
            {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            {uploading ? "Uploading…" : "Upload Dataset"}
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-3">
          Only CSV files are accepted. Max size: 50 MB.
          Your data is stored on your server and is not sent to external AI services.
        </p>
      </div>

      {/* Dataset List */}
      <div className="glass-card p-0 overflow-hidden">
        <div className="px-6 py-4 border-b border-surface-border">
          <h2 className="text-sm font-semibold text-white">Uploaded Datasets</h2>
        </div>
        {isLoading ? (
          <div className="p-6 space-y-3">
            {[1, 2, 3].map((i) => <div key={i} className="skeleton h-16 rounded-xl" />)}
          </div>
        ) : datasets.length === 0 ? (
          <div className="py-16 text-center">
            <Database className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <p className="text-sm text-slate-400">No datasets uploaded yet</p>
            <p className="text-xs text-slate-500 mt-1">
              Upload a CSV file above to get started.
            </p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Rows</th>
                <th>Columns</th>
                <th>Quality Score</th>
                <th>Status</th>
                <th>Uploaded</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((d) => (
                <tr key={d.id}>
                  <td className="font-medium text-white">{d.name}</td>
                  <td>{d.row_count?.toLocaleString() || "—"}</td>
                  <td>{d.column_count || "—"}</td>
                  <td>
                    {d.quality_score != null ? (
                      <div className="flex items-center gap-2">
                        <div className="progress-bar w-24">
                          <div className="progress-fill" style={{ width: `${d.quality_score}%` }} />
                        </div>
                        <span className="text-xs text-slate-300">{d.quality_score.toFixed(0)}</span>
                      </div>
                    ) : "—"}
                  </td>
                  <td>
                    <span className={clsx("text-xs font-medium capitalize", statusColor[d.status] || "text-slate-400")}>
                      {d.status}
                    </span>
                  </td>
                  <td className="text-xs text-slate-400">
                    {new Date(d.created_at).toLocaleDateString("en-IN")}
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleValidate(d.id)}
                        disabled={validatingId === d.id}
                        title="Validate dataset"
                        className="p-1.5 text-slate-400 hover:text-emerald-400 transition-colors"
                      >
                        {validatingId === d.id
                          ? <Loader2 className="w-4 h-4 animate-spin" />
                          : <CheckCircle className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={() => handleDelete(d.id)}
                        title="Delete dataset"
                        className="p-1.5 text-slate-400 hover:text-red-400 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
