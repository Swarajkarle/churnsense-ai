"use client";

import { useAuthStore } from "@/lib/store";
import { authApi } from "@/lib/api";
import { useState } from "react";
import { toast } from "sonner";
import { User, Loader2, Save } from "lucide-react";

export default function ProfilePage() {
  const { user, setAuth } = useAuthStore();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await authApi.updateMe({ full_name: fullName });
      const meRes = await authApi.getMe();
      const token = localStorage.getItem("access_token") || "";
      setAuth(meRes.data, token);
      toast.success("Profile updated!");
    } catch { toast.error("Update failed"); }
    finally { setSaving(false); }
  };

  return (
    <div className="p-8 space-y-6 animate-fade-in max-w-xl">
      <div>
        <h1 className="section-title">Profile</h1>
        <p className="section-subtitle">Manage your account information</p>
      </div>
      <div className="glass-card space-y-5">
        <div className="flex items-center gap-4 mb-2">
          <div className="w-14 h-14 rounded-2xl bg-gradient-brand flex items-center justify-center text-white text-2xl font-bold shadow-brand">
            {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || "?"}
          </div>
          <div>
            <div className="text-lg font-semibold text-white">{user?.full_name || "—"}</div>
            <div className="text-sm text-slate-400">{user?.email}</div>
            <div className="text-xs text-brand-400 mt-0.5 capitalize">{user?.role}</div>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">Full Name</label>
          <input type="text" className="form-input" value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">Email</label>
          <input type="text" className="form-input opacity-60" value={user?.email || ""} disabled />
          <p className="text-xs text-slate-500 mt-1">Email cannot be changed here.</p>
        </div>
        <button onClick={handleSave} disabled={saving} className="btn-primary">
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          {saving ? "Saving…" : "Save Changes"}
        </button>
      </div>
    </div>
  );
}
