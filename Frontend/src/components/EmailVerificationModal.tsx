import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mail,
  CheckCircle2,
  ShieldCheck,
  Sparkles,
  RefreshCw,
  X,
} from "lucide-react";
import { api } from "../services/api";

interface EmailVerificationModalProps {
  isOpen: boolean;
  onClose: () => void;
  email: string;
  simulatedToken?: string;
  onVerified: (email: string) => void;
}

export const EmailVerificationModal: React.FC<EmailVerificationModalProps> = ({
  isOpen,
  onClose,
  email,
  onVerified,
}) => {
  const [isResending, setIsResending] = useState(false);
  const [resendSuccess, setResendSuccess] = useState<string | null>(null);
  const [verifiedSuccess, setVerifiedSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Auto-detect when account becomes verified (e.g. user clicked verify link in email in another tab or same browser)
  useEffect(() => {
    if (!isOpen || verifiedSuccess) return;
    const interval = setInterval(() => {
      const storedToken = localStorage.getItem("gradify_token");
      const storedEmail = localStorage.getItem("gradify_user_email");
      if (storedToken && storedEmail === email) {
        setVerifiedSuccess(true);
        setTimeout(() => {
          onVerified(email);
          onClose();
        }, 1200);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [isOpen, email, verifiedSuccess, onVerified, onClose]);

  const handleResend = async () => {
    setIsResending(true);
    setErrorMsg(null);
    setResendSuccess(null);
    try {
      await api.resendVerification(email);
      setResendSuccess("A fresh verification email has been sent. Please check your inbox and spam folder.");
    } catch (err: unknown) {
      setErrorMsg((err as Error).message || "Failed to resend email. Please try again.");
    } finally {
      setIsResending(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            className="relative w-full max-w-lg bg-[#101010] border border-primary/25 rounded-2xl md:rounded-3xl p-6 sm:p-9 shadow-2xl overflow-hidden"
          >
            {/* Noise texture overlay */}
            <div className="bg-noise absolute inset-0 opacity-[0.3] mix-blend-overlay pointer-events-none" />

            {/* Close Button */}
            <button
              type="button"
              onClick={onClose}
              className="absolute top-5 right-5 w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-gray-400 hover:text-primary transition-colors cursor-pointer z-10"
              title="Close modal"
            >
              <X className="w-4 h-4" />
            </button>

            {verifiedSuccess ? (
              /* Success State */
              <div className="relative z-10 py-8 text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 300, damping: 20 }}
                  className="w-16 h-16 rounded-full bg-primary/20 border border-primary/40 flex items-center justify-center text-primary mx-auto mb-5"
                >
                  <CheckCircle2 className="w-9 h-9" />
                </motion.div>
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono mb-3">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  IDENTITY ACTIVATED &bull; LOGGED IN
                </div>
                <h3 className="text-2xl font-medium text-[#E1E0CC] mb-2">
                  Email Verified Successfully
                </h3>
                <p className="text-xs sm:text-sm text-primary/70 max-w-md mx-auto font-light">
                  Welcome to Gradify. Redirecting you to your academic workspace cockpit...
                </p>
              </div>
            ) : (
              /* Verification Instruction Prompt */
              <div className="relative z-10 text-center sm:text-left">
                {/* Header Badge */}
                <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-primary/20 bg-primary/5 text-primary text-xs tracking-widest uppercase font-mono mb-5">
                  <Sparkles className="w-3.5 h-3.5" />
                  Verify Your Identity
                </div>

                <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4 mb-5">
                  <div className="w-12 h-12 rounded-2xl bg-primary/10 border border-primary/25 flex items-center justify-center text-primary shrink-0">
                    <Mail className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-2xl sm:text-3xl font-medium text-[#E1E0CC] tracking-tight mb-2">
                      Check Your Email
                    </h3>
                    <p className="text-xs sm:text-sm text-primary/70 font-light leading-relaxed">
                      We sent a verification link to{" "}
                      <span className="text-primary font-medium underline underline-offset-2">
                        {email}
                      </span>
                      .
                    </p>
                  </div>
                </div>

                {errorMsg && (
                  <div className="p-3 mb-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-mono text-left">
                    {errorMsg}
                  </div>
                )}

                {resendSuccess && (
                  <div className="p-3 mb-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-mono text-left">
                    {resendSuccess}
                  </div>
                )}

                {/* Instructions Card */}
                <div className="bg-[#161616] border border-white/[0.08] rounded-2xl p-5 mb-6 text-left space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full bg-primary/20 text-primary text-[11px] font-mono font-bold flex items-center justify-center shrink-0 mt-0.5">
                      1
                    </div>
                    <p className="text-xs text-gray-300 leading-relaxed">
                      Open the email from <strong className="text-primary">Gradify</strong> in your inbox.
                    </p>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full bg-primary/20 text-primary text-[11px] font-mono font-bold flex items-center justify-center shrink-0 mt-0.5">
                      2
                    </div>
                    <p className="text-xs text-gray-300 leading-relaxed">
                      Click the <strong className="text-[#E1E0CC]">"VERIFY EMAIL &amp; ENTER COCKPIT"</strong> button inside the email.
                    </p>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full bg-primary/20 text-primary text-[11px] font-mono font-bold flex items-center justify-center shrink-0 mt-0.5">
                      3
                    </div>
                    <p className="text-xs text-gray-300 leading-relaxed">
                      You will be automatically redirected to Gradify with your account signed in and cockpit unlocked.
                    </p>
                  </div>
                </div>

                {/* Live Waiting Radar Indicator */}
                <div className="flex items-center justify-between p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.06] mb-6">
                  <div className="flex items-center gap-2.5">
                    <span className="relative flex h-2.5 w-2.5">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary"></span>
                    </span>
                    <span className="text-xs font-mono text-primary/80">
                      Waiting for verification confirmation...
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-gray-500">
                    Expires in 30m
                  </span>
                </div>

                {/* Footer Controls: Resend & Dismiss */}
                <div className="pt-2 border-t border-white/[0.08] flex items-center justify-between gap-3 flex-wrap">
                  <button
                    type="button"
                    disabled={isResending}
                    onClick={handleResend}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-primary/10 border border-primary/30 text-primary text-xs font-mono hover:bg-primary/20 active:scale-95 transition-all cursor-pointer disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isResending ? "animate-spin" : ""}`} />
                    <span>{isResending ? "Dispatching..." : "Resend Verification Email"}</span>
                  </button>

                  <button
                    type="button"
                    onClick={onClose}
                    className="text-xs text-gray-400 hover:text-[#E1E0CC] transition-colors font-mono cursor-pointer"
                  >
                    Close / Change Email
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

