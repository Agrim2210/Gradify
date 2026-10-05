import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Lock,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  GraduationCap,
  X,
} from "lucide-react";
import { api } from "../services/api";

interface AcceptInvitationModalProps {
  isOpen: boolean;
  onClose: () => void;
  token: string;
  email: string;
  role?: string;
  onAccepted: (data: any) => void;
}

export const AcceptInvitationModal: React.FC<AcceptInvitationModalProps> = ({
  isOpen,
  onClose,
  token,
  email,
  role = "TEACHER",
  onAccepted,
}) => {
  const isStudent = role?.toUpperCase() === "STUDENT";
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password.length < 6) {
      setError("Password must be at least 6 characters in length");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      const res = await api.acceptInvitation(token, password);
      setSuccess(true);
      setTimeout(() => {
        onAccepted(res);
      }, 1200);
    } catch (err: any) {
      setError(err.message || "Failed to accept invitation");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[60] p-4 bg-black/90 backdrop-blur-md flex items-center justify-center"
        >
          <motion.div
            initial={{ scale: 0.95, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.95, y: 20 }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            className="relative w-full max-w-lg bg-[#101010] border border-[#DEDBC8]/25 rounded-2xl sm:rounded-3xl p-6 sm:p-8 shadow-2xl overflow-hidden"
          >
            {/* Top decorative accent */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#DEDBC8]/10 via-[#DEDBC8] to-[#DEDBC8]/10" />

            <button
              onClick={onClose}
              className="absolute top-5 right-5 p-2 rounded-full bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Header Badge */}
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs tracking-widest uppercase font-mono mb-4 ${
              isStudent
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                : "border-primary/20 bg-primary/5 text-primary"
            }`}>
              <Sparkles className="w-3.5 h-3.5" />
              {isStudent ? "Student Workspace Protocol" : "Teacher Workspace Protocol"}
            </div>

            <h3 className="text-2xl font-light text-[#E1E0CC] mb-2 tracking-tight">
              {isStudent ? "Student Workspace Admission" : "Teacher Workspace Admission"}
            </h3>
            <p className="text-xs sm:text-sm text-primary/70 mb-6 leading-relaxed">
              {isStudent ? (
                <>
                  You have been admitted to the workspace as a{" "}
                  <strong className="text-emerald-300 font-medium">Student</strong>. Set your account password to confirm your credentials and immediately enter your workspace cockpit.
                </>
              ) : (
                <>
                  You have been invited to join the workspace as a{" "}
                  <strong className="text-primary font-medium">Teacher</strong>. Create your account password to confirm your credentials and immediately enter your workspace cockpit.
                </>
              )}
            </p>

            {/* Invited Email Badge */}
            <div className="mb-6 p-3 rounded-xl bg-black/50 border border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs">
                <GraduationCap className={`w-4 h-4 ${isStudent ? "text-emerald-400" : "text-primary"}`} />
                <span className="text-gray-400 font-mono">Invited Account:</span>
                <span className="text-[#E1E0CC] font-mono font-medium">{email || (isStudent ? "student@university.edu" : "teacher@university.edu")}</span>
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
                isStudent
                  ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-300"
                  : "bg-primary/10 border-primary/20 text-primary"
              }`}>
                ROLE: {isStudent ? "STUDENT" : "TEACHER"}
              </span>
            </div>

            {/* Error Banner */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-4 p-3 rounded-xl bg-red-950/40 border border-red-500/30 flex items-start gap-2.5 text-red-200 text-xs font-mono"
              >
                <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </motion.div>
            )}

            {/* Success Banner */}
            {success ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-6 rounded-2xl bg-emerald-950/30 border border-emerald-500/30 text-center space-y-3"
              >
                <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mx-auto text-emerald-400">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <h4 className="text-lg font-medium text-emerald-300">Identity Configured!</h4>
                <p className="text-xs text-emerald-200/70 font-mono">
                  {isStudent
                    ? "Password saved. Signing into workspace as Student..."
                    : "Password saved. Signing into workspace as Faculty Teacher..."}
                </p>
              </motion.div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-mono uppercase tracking-wider text-primary/80 mb-1.5">
                    Set Account Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="password"
                      required
                      placeholder="••••••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full bg-[#161616] border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-xs sm:text-sm text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-mono uppercase tracking-wider text-primary/80 mb-1.5">
                    Confirm Account Password
                  </label>
                  <div className="relative">
                    <ShieldCheck className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="password"
                      required
                      placeholder="••••••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full bg-[#161616] border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-xs sm:text-sm text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary text-black font-medium py-3 rounded-xl text-xs sm:text-sm flex items-center justify-center gap-2 hover:brightness-105 active:scale-[0.99] transition-all cursor-pointer shadow-lg disabled:opacity-50 mt-2"
                >
                  <span>
                    {loading
                      ? isStudent
                        ? "Activating Student Account..."
                        : "Activating Teacher Account..."
                      : isStudent
                      ? "CONFIRM PASSWORD & ENTER AS STUDENT →"
                      : "Create Password & Enter Workspace →"}
                  </span>
                  <ArrowRight className="w-4 h-4" />
                </button>

                <p className="text-[11px] text-gray-500 text-center font-mono pt-2">
                  Once set, you can log in directly at any time using your email and password.
                </p>
              </form>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
