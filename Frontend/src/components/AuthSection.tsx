import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mail,
  Lock,
  User,
  GraduationCap,
  ArrowRight,
  Sparkles,
  CheckCircle,
  Eye,
  EyeOff,
  Shield,
} from "lucide-react";

import { api } from "../services/api";

interface AuthSectionProps {
  initialTab?: "signup" | "signin";
  onOpenWorkspace?: () => void;
  onOpenVerificationModal?: (email: string, token?: string) => void;
}

export const AuthSection: React.FC<AuthSectionProps> = ({
  initialTab = "signup",
  onOpenWorkspace,
  onOpenVerificationModal,
}) => {
  const [tab, setTab] = useState<"signup" | "signin">(initialTab);
  const [showPassword, setShowPassword] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Sync when prop changes
  useEffect(() => {
    setTab(initialTab);
  }, [initialTab]);

  // Form states
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    academicFocus: "Computer Science & Engineering",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    try {
      if (tab === "signup") {
        await api.signup(formData.email, formData.password);
        if (onOpenVerificationModal) {
          onOpenVerificationModal(formData.email);
        }
      } else {
        await api.login(formData.email, formData.password);
        localStorage.setItem("gradify_nav_state", "workspace");
        setSubmitted(true);
        setTimeout(() => {
          onOpenWorkspace?.();
        }, 1200);
      }
    } catch (err: unknown) {
      const error = err as Error & { code?: string; email?: string; status?: number };
      if ((error.code === "EMAIL_NOT_VERIFIED" || error.status === 403) && onOpenVerificationModal) {
        onOpenVerificationModal(error.email || formData.email);
      } else {
        setErrorMessage(error.message || "Authentication failed");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      id="auth-section"
      className="relative z-10 py-16 md:py-24 px-4 md:px-6 scroll-mt-12"
    >
      <div className="max-w-4xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-10 md:mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-primary/20 bg-primary/5 text-primary text-xs tracking-widest uppercase mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            Join The Academic Vanguard
          </div>
          <h2
            className="text-3xl sm:text-4xl md:text-5xl font-normal tracking-tight"
            style={{ color: "#E1E0CC" }}
          >
            {tab === "signup" ? (
              <>
                Initiate your{" "}
                <span className="font-serif italic font-normal text-primary">
                  Gradify Cockpit
                </span>
              </>
            ) : (
              <>
                Welcome back to{" "}
                <span className="font-serif italic font-normal text-primary">
                  The Lab
                </span>
              </>
            )}
          </h2>
          <p className="text-primary/70 text-sm sm:text-base mt-3 max-w-md mx-auto font-light">
            {tab === "signup"
              ? "Reclaim 14+ hours every week with automated task breakdown and cognitive streak pacing."
              : "Resume your active streak session and access your personalized mastery dashboard."}
          </p>
        </div>

        {/* Auth Master Card */}
        <div className="relative bg-[#101010]/95 backdrop-blur-xl border border-white/[0.08] rounded-2xl md:rounded-3xl p-6 sm:p-10 md:p-12 shadow-2xl overflow-hidden">
          {/* Subtle noise in auth card */}
          <div className="bg-noise absolute inset-0 opacity-[0.25] mix-blend-overlay pointer-events-none" />

          {/* Success Notification */}
          <AnimatePresence>
            {submitted && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="relative z-20 mb-6 p-4 rounded-xl bg-primary/10 border border-primary/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-primary text-sm"
              >
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 flex-shrink-0 text-primary" />
                  <span>
                    {tab === "signup"
                      ? "First Identity established! You can now configure your workspace."
                      : "Identity authenticated. Ready to enter Workspace Cockpit."}
                  </span>
                </div>
                {onOpenWorkspace && (
                  <button
                    type="button"
                    onClick={onOpenWorkspace}
                    className="px-3 py-1.5 rounded-lg bg-primary text-black text-xs font-medium hover:brightness-105 transition-all whitespace-nowrap cursor-pointer shadow"
                  >
                    Open Workspace Cockpit ↗
                  </button>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error Notification */}
          {errorMessage && (
            <div className="relative z-20 mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-mono">
              {errorMessage}
            </div>
          )}

          {/* Active Session Notification if already authenticated */}
          {localStorage.getItem("gradify_token") && !submitted && (
            <div className="relative z-20 mb-6 p-4 rounded-xl bg-primary/10 border border-primary/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-primary text-sm">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 flex-shrink-0 text-primary" />
                <span>
                  Active session detected:{" "}
                  <strong className="text-[#E1E0CC] font-mono text-xs">
                    {localStorage.getItem("gradify_user_email") || "Signed in"}
                  </strong>
                </span>
              </div>
              {onOpenWorkspace && (
                <button
                  type="button"
                  onClick={onOpenWorkspace}
                  className="px-3.5 py-1.5 rounded-lg bg-primary text-black text-xs font-semibold hover:brightness-105 transition-all whitespace-nowrap cursor-pointer shadow"
                >
                  Enter Cockpit ↗
                </button>
              )}
            </div>
          )}

          {/* Tab Selector */}
          <div className="relative z-10 flex p-1 bg-black/60 border border-white/10 rounded-full max-w-xs mx-auto mb-8">
            <button
              type="button"
              onClick={() => setTab("signup")}
              className={`relative flex-1 py-2 text-xs sm:text-sm font-medium rounded-full transition-all duration-300 ${
                tab === "signup" ? "text-black" : "text-primary/70 hover:text-primary"
              }`}
            >
              {tab === "signup" && (
                <motion.div
                  layoutId="auth-active-pill"
                  className="absolute inset-0 bg-primary rounded-full"
                  transition={{ type: "spring", stiffness: 400, damping: 35 }}
                />
              )}
              <span className="relative z-10">Sign Up</span>
            </button>

            <button
              type="button"
              onClick={() => setTab("signin")}
              className={`relative flex-1 py-2 text-xs sm:text-sm font-medium rounded-full transition-all duration-300 ${
                tab === "signin" ? "text-black" : "text-primary/70 hover:text-primary"
              }`}
            >
              {tab === "signin" && (
                <motion.div
                  layoutId="auth-active-pill"
                  className="absolute inset-0 bg-primary rounded-full"
                  transition={{ type: "spring", stiffness: 400, damping: 35 }}
                />
              )}
              <span className="relative z-10">Sign In</span>
            </button>
          </div>

          {/* Social Sign-In Button */}
          <div className="relative z-10 max-w-md mx-auto mb-6">
            <button
              type="button"
              onClick={() => {
                setLoading(true);
                setTimeout(() => {
                  setLoading(false);
                  setSubmitted(true);
                  setTimeout(() => setSubmitted(false), 4000);
                }, 800);
              }}
              className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-xl bg-[#1a1a1a] hover:bg-[#222222] border border-white/10 hover:border-primary/40 text-primary transition-all duration-200 text-xs sm:text-sm font-medium"
            >
              {/* Google SVG */}
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path
                  fill="#EA4335"
                  d="M12 5c1.56 0 2.96.54 4.07 1.43l3.05-3.05C17.27 1.63 14.82 1 12 1 7.37 1 3.4 3.65 1.46 7.51l3.66 2.84C6.01 7.42 8.76 5 12 5z"
                />
                <path
                  fill="#4285F4"
                  d="M23.49 12.27c0-.79-.07-1.54-.19-2.27H12v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58l3.7 2.87c2.16-1.99 3.72-4.93 3.72-8.69z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.12 14.65c-.24-.72-.37-1.49-.37-2.28s.13-1.56.37-2.28L1.46 7.25C.53 9.1 0 11.19 0 13.43s.53 4.33 1.46 6.18l3.66-2.96z"
                />
                <path
                  fill="#34A853"
                  d="M12 23.86c3.24 0 5.95-1.08 7.93-2.91l-3.7-2.87c-1.08.72-2.45 1.16-4.23 1.16-3.24 0-5.99-2.42-6.88-5.35L1.46 16.73C3.4 20.59 7.37 23.86 12 23.86z"
                />
              </svg>
              <span>Continue with University Google Account</span>
            </button>

            <div className="flex items-center gap-3 my-6">
              <div className="h-[1px] flex-1 bg-white/10" />
              <span className="text-[11px] uppercase tracking-widest text-gray-500 font-mono">
                or enter with credentials
              </span>
              <div className="h-[1px] flex-1 bg-white/10" />
            </div>
          </div>

          {/* Form */}
          <form
            onSubmit={handleSubmit}
            className="relative z-10 max-w-md mx-auto space-y-4"
          >
            <AnimatePresence mode="wait">
              {tab === "signup" ? (
                <motion.div
                  key="signup-fields"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 10 }}
                  transition={{ duration: 0.25 }}
                  className="space-y-4"
                >
                  {/* Full Name */}
                  <div>
                    <label className="block text-xs font-medium text-primary/80 mb-1.5 uppercase tracking-wider font-mono">
                      Full Legal or Preferred Name
                    </label>
                    <div className="relative">
                      <User className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input
                        type="text"
                        required
                        placeholder="Alex Vance"
                        value={formData.name}
                        onChange={(e) =>
                          setFormData({ ...formData, name: e.target.value })
                        }
                        className="w-full bg-[#181818] border border-white/10 rounded-xl py-3 pl-10 pr-4 text-xs sm:text-sm text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/40 transition-colors"
                      />
                    </div>
                  </div>

                  {/* Academic Track */}
                  <div>
                    <label className="block text-xs font-medium text-primary/80 mb-1.5 uppercase tracking-wider font-mono">
                      Field of Study / Academic Track
                    </label>
                    <div className="relative">
                      <GraduationCap className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <select
                        value={formData.academicFocus}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            academicFocus: e.target.value,
                          })
                        }
                        className="w-full bg-[#181818] border border-white/10 rounded-xl py-3 pl-10 pr-4 text-xs sm:text-sm text-[#E1E0CC] focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/40 transition-colors appearance-none cursor-pointer"
                      >
                        <option value="Computer Science & Engineering">
                          Computer Science & Engineering
                        </option>
                        <option value="Biomedical & Pre-Med">
                          Biomedical & Pre-Med
                        </option>
                        <option value="Business, Finance & Economics">
                          Business, Finance & Economics
                        </option>
                        <option value="Law & Legal Studies">
                          Law & Legal Studies
                        </option>
                        <option value="Pure Mathematics & Physics">
                          Pure Mathematics & Physics
                        </option>
                        <option value="Humanities & Architecture">
                          Humanities & Architecture
                        </option>
                      </select>
                    </div>
                  </div>
                </motion.div>
              ) : null}
            </AnimatePresence>

            {/* Email Field */}
            <div>
              <label className="block text-xs font-medium text-primary/80 mb-1.5 uppercase tracking-wider font-mono">
                University (.edu) or Personal Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  placeholder="name@university.edu"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  className="w-full bg-[#181818] border border-white/10 rounded-xl py-3 pl-10 pr-4 text-xs sm:text-sm text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/40 transition-colors"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-medium text-primary/80 uppercase tracking-wider font-mono">
                  Master Password
                </label>
                {tab === "signin" && (
                  <button
                    type="button"
                    onClick={() => alert("Password reset link sent to your registered email.")}
                    className="text-[11px] text-primary/60 hover:text-primary transition-colors underline cursor-pointer"
                  >
                    Forgot key?
                  </button>
                )}
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  placeholder="••••••••••••"
                  value={formData.password}
                  onChange={(e) =>
                    setFormData({ ...formData, password: e.target.value })
                  }
                  className="w-full bg-[#181818] border border-white/10 rounded-xl py-3 pl-10 pr-10 text-xs sm:text-sm text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/40 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-primary transition-colors cursor-pointer"
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <div className="pt-3">
              <button
                type="submit"
                disabled={loading}
                className="w-full group bg-primary text-black font-medium py-3 px-5 rounded-xl text-xs sm:text-sm flex items-center justify-center gap-2 hover:brightness-105 active:scale-[0.99] transition-all duration-200 shadow-lg shadow-primary/10 cursor-pointer disabled:opacity-60"
              >
                <span>
                  {loading
                    ? "Authenticating with Lab..."
                    : tab === "signup"
                    ? "Establish My Academic Cockpit"
                    : "Enter Gradify Cockpit"}
                </span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </button>
            </div>

            {/* Security note */}
            <div className="flex items-center justify-center gap-1.5 text-[11px] text-gray-500 pt-2 font-mono">
              <Shield className="w-3.5 h-3.5 text-primary/50" />
              <span>256-bit encryption. Zero telemetry sold to advertisers.</span>
            </div>

            {onOpenWorkspace && (
              <div className="pt-3 border-t border-white/[0.06] text-center">
                <button
                  type="button"
                  onClick={onOpenWorkspace}
                  className="inline-flex items-center gap-1.5 text-xs text-primary/80 hover:text-primary transition-colors cursor-pointer font-mono underline decoration-primary/40 underline-offset-4"
                >
                  <span>Already have an identity? Open Workspace Cockpit (Head View) ↗</span>
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </section>
  );
};
