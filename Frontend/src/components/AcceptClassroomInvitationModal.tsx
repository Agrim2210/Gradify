import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Hash, Lock, CheckCircle2 } from "lucide-react";
import { api } from "../services/api";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  inviteToken: string;
  inviteEmail: string;
  onSuccess: (classroomId: string) => void;
}

export const AcceptClassroomInvitationModal: React.FC<Props> = ({
  isOpen,
  onClose,
  inviteToken,
  inviteEmail,
  onSuccess,
}) => {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [rollNumber, setRollNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleAccept = async () => {
    setError(null);
    if (!password || !rollNumber) {
      setError("Password and roll number are required.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    setLoading(true);
    try {
      const result = await api.acceptClassroomInvitation(inviteToken, password, rollNumber);
      setSuccess(true);
      setTimeout(() => {
        onSuccess(result.classroom_id);
      }, 1800);
    } catch (err: any) {
      setError(err.message || "Failed to accept invitation. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center"
        style={{ backgroundColor: "rgba(0,0,0,0.85)", backdropFilter: "blur(12px)" }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.3 }}
          className="relative w-full max-w-md mx-4"
          style={{
            background: "#101010",
            border: "1px solid rgba(222,219,200,0.18)",
            borderRadius: "24px",
            boxShadow: "0 20px 40px rgba(0,0,0,0.85)",
            padding: "40px",
          }}
        >
          {/* Close */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-cream opacity-40 hover:opacity-100 transition-opacity"
          >
            <X size={18} />
          </button>

          {success ? (
            <div className="text-center py-8">
              <CheckCircle2 size={48} className="mx-auto mb-4" style={{ color: "#DEDBC8" }} />
              <h2 style={{ color: "#E1E0CC", fontSize: "22px", fontWeight: 500, marginBottom: "8px" }}>
                Welcome to the Classroom!
              </h2>
              <p style={{ color: "rgba(222,219,200,0.6)", fontSize: "14px" }}>
                Signing you in and opening your classroom…
              </p>
            </div>
          ) : (
            <>
              {/* Header */}
              <div className="text-center mb-8">
                <div
                  style={{
                    display: "inline-block",
                    padding: "5px 14px",
                    background: "rgba(222,219,200,0.08)",
                    border: "1px solid rgba(222,219,200,0.2)",
                    borderRadius: "9999px",
                    fontSize: "11px",
                    letterSpacing: "2px",
                    color: "#DEDBC8",
                    textTransform: "uppercase",
                    fontWeight: 600,
                    marginBottom: "16px",
                  }}
                >
                  ● Student Classroom Protocol
                </div>
                <h2
                  style={{
                    color: "#E1E0CC",
                    fontSize: "26px",
                    fontWeight: 500,
                    letterSpacing: "-0.03em",
                    marginBottom: "6px",
                  }}
                >
                  Join Classroom
                </h2>
                <p style={{ color: "rgba(222,219,200,0.55)", fontSize: "13px" }}>
                  Invited as: <span style={{ color: "#DEDBC8" }}>{inviteEmail}</span>
                </p>
              </div>

              {/* Divider */}
              <div style={{ height: "1px", background: "rgba(255,255,255,0.08)", marginBottom: "24px" }} />

              {/* Form */}
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                {/* Roll Number */}
                <div>
                  <label style={{ color: "rgba(222,219,200,0.7)", fontSize: "12px", letterSpacing: "1px", textTransform: "uppercase", display: "block", marginBottom: "6px" }}>
                    Roll Number
                  </label>
                  <div style={{ position: "relative" }}>
                    <Hash
                      size={15}
                      style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)", color: "rgba(222,219,200,0.4)" }}
                    />
                    <input
                      type="text"
                      value={rollNumber}
                      onChange={(e) => setRollNumber(e.target.value)}
                      placeholder="e.g. 21CS001"
                      style={{
                        width: "100%",
                        background: "#161616",
                        border: "1px solid rgba(222,219,200,0.15)",
                        borderRadius: "12px",
                        color: "#DEDBC8",
                        padding: "12px 14px 12px 38px",
                        fontSize: "14px",
                        outline: "none",
                        boxSizing: "border-box",
                      }}
                    />
                  </div>
                </div>

                {/* Password */}
                <div>
                  <label style={{ color: "rgba(222,219,200,0.7)", fontSize: "12px", letterSpacing: "1px", textTransform: "uppercase", display: "block", marginBottom: "6px" }}>
                    Set Password
                  </label>
                  <div style={{ position: "relative" }}>
                    <Lock
                      size={15}
                      style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)", color: "rgba(222,219,200,0.4)" }}
                    />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Minimum 6 characters"
                      style={{
                        width: "100%",
                        background: "#161616",
                        border: "1px solid rgba(222,219,200,0.15)",
                        borderRadius: "12px",
                        color: "#DEDBC8",
                        padding: "12px 14px 12px 38px",
                        fontSize: "14px",
                        outline: "none",
                        boxSizing: "border-box",
                      }}
                    />
                  </div>
                </div>

                {/* Confirm Password */}
                <div>
                  <label style={{ color: "rgba(222,219,200,0.7)", fontSize: "12px", letterSpacing: "1px", textTransform: "uppercase", display: "block", marginBottom: "6px" }}>
                    Confirm Password
                  </label>
                  <div style={{ position: "relative" }}>
                    <Lock
                      size={15}
                      style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)", color: "rgba(222,219,200,0.4)" }}
                    />
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Repeat password"
                      style={{
                        width: "100%",
                        background: "#161616",
                        border: "1px solid rgba(222,219,200,0.15)",
                        borderRadius: "12px",
                        color: "#DEDBC8",
                        padding: "12px 14px 12px 38px",
                        fontSize: "14px",
                        outline: "none",
                        boxSizing: "border-box",
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Error */}
              {error && (
                <div style={{
                  marginTop: "16px",
                  padding: "12px 16px",
                  background: "rgba(239,68,68,0.1)",
                  border: "1px solid rgba(239,68,68,0.3)",
                  borderRadius: "10px",
                  color: "#f87171",
                  fontSize: "13px",
                }}>
                  {error}
                </div>
              )}

              {/* CTA */}
              <button
                onClick={handleAccept}
                disabled={loading}
                style={{
                  width: "100%",
                  marginTop: "24px",
                  padding: "14px",
                  background: loading ? "rgba(222,219,200,0.3)" : "#DEDBC8",
                  color: "#000",
                  borderRadius: "9999px",
                  fontSize: "13px",
                  fontWeight: 600,
                  letterSpacing: "0.5px",
                  cursor: loading ? "not-allowed" : "pointer",
                  border: "none",
                  transition: "all 0.2s",
                }}
              >
                {loading ? "Joining..." : "JOIN CLASSROOM & SET PASSWORD →"}
              </button>
            </>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
