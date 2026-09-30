"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { Loader2 } from "lucide-react";

const registerSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Must contain at least one uppercase letter")
    .regex(/[0-9]/, "Must contain at least one number"),
  full_name: z.string().min(2, "Full name is required"),
  organization_name: z.string().min(2, "Organization name is required"),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({ resolver: zodResolver(registerSchema) });

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    try {
      await authApi.register(data);
      // Auto-login after registration
      const loginRes = await authApi.login(data.email, data.password);
      const { access_token } = loginRes.data;

      // Store token BEFORE calling getMe so the axios interceptor
      // can attach it as Authorization header.
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", access_token);
      }

      const meRes = await authApi.getMe();
      setAuth(meRes.data, access_token);
      toast.success("Account created! Welcome to ChurnSense AI.");
      router.push("/dashboard");
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      if (Array.isArray(detail)) {
        toast.error(detail.map((e: any) => e.msg).join(", "));
      } else {
        toast.error(detail || "Registration failed. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const onValidationError = (errs: any) => {
    // Show the FIRST validation error as a toast so it's never invisible
    const firstErr = Object.values(errs)[0] as any;
    toast.error(firstErr?.message || "Please fix the highlighted fields.");
  };


  return (
    <div className="min-h-screen bg-surface flex items-center justify-center px-4 py-12">
      <div className="relative w-full max-w-md animate-slide-up">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4 shadow-brand overflow-hidden">
            <Image
              src="/logo.png"
              alt="ChurnSense AI"
              width={56}
              height={56}
              className="w-full h-full object-contain"
              priority
            />
          </div>
          <h1 className="text-2xl font-bold text-white">Create your account</h1>
          <p className="mt-1 text-sm text-slate-400">
            Start predicting churn in minutes
          </p>
        </div>

        <div className="glass-card">
        <form onSubmit={handleSubmit(onSubmit, onValidationError)} className="space-y-4">
            {[
              { id: "full_name", label: "Full Name", type: "text", placeholder: "Swaraj Karle" },
              { id: "email", label: "Work Email", type: "email", placeholder: "you@company.com" },
              { id: "organization_name", label: "Organization Name", type: "text", placeholder: "Acme Corp" },
              { id: "password", label: "Password", type: "password", placeholder: "Min 8 chars, 1 uppercase, 1 number" },
            ].map((field) => (
              <div key={field.id}>
                <label htmlFor={field.id} className="block text-sm font-medium text-slate-300 mb-2">
                  {field.label}
                </label>
                <input
                  id={field.id}
                  type={field.type}
                  className="form-input"
                  placeholder={field.placeholder}
                  {...register(field.id as keyof RegisterFormData)}
                />
                {errors[field.id as keyof RegisterFormData] && (
                  <p className="mt-1.5 text-xs text-red-400">
                    {errors[field.id as keyof RegisterFormData]?.message}
                  </p>
                )}
              </div>
            ))}

            <button
              type="submit"
              id="register-submit-btn"
              disabled={isLoading}
              className="btn-primary w-full justify-center py-3 mt-2"
            >
              {isLoading ? (
                <><Loader2 className="w-4 h-4 animate-spin" />Creating account…</>
              ) : (
                "Create Account"
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-surface-border text-center">
            <p className="text-sm text-slate-400">
              Already have an account?{" "}
              <Link href="/login" className="text-brand-400 hover:text-brand-300 font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
