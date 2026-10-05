import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X, Upload, Users, FileText, Download,
  Clock, Plus, Mail, CheckCircle2, ArrowLeft, BookOpen,
  Award, Check, BarChart3, ShieldAlert
} from "lucide-react";
import {
  api,
  type AssignmentResponse,
  type StudentOverviewResponse,
  type CategorizedSubmissionsResponse,
  type GradebookResponse,
} from "../services/api";
import { CinematicVideo } from "./CinematicVideo";

const VIDEO_URL =
  "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260405_170732_8a9ccda6-5cff-4628-b164-059c500a2b41.mp4";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  classroomId: string;
  classroomName: string;
  userRole: string; // OWNER (teacher) | STUDENT
}

export const ClassroomDashboard: React.FC<Props> = ({
  isOpen,
  onClose,
  classroomId,
  classroomName,
  userRole,
}) => {
  const isTeacher = userRole?.toUpperCase() === "OWNER" || userRole?.toUpperCase() === "TEACHER";

  // Tab switchers
  // Teacher: 'assignments' | 'gradebook' | 'notes'
  // Student: 'todo' | 'completed' | 'scores' | 'notes'
  const [activeTab, setActiveTab] = useState<string>(isTeacher ? "assignments" : "todo");

  // Keep active tab in sync with role changes if any
  useEffect(() => {
    setActiveTab(isTeacher ? "assignments" : "todo");
  }, [isTeacher]);

  // Assignments & Notes general state
  const [assignments, setAssignments] = useState<AssignmentResponse[]>([]);
  const [loadingAssignments, setLoadingAssignments] = useState(false);
  const [notes, setNotes] = useState<any[]>([]);
  const [loadingNotes, setLoadingNotes] = useState(false);

  // Student specific data state
  const [studentOverview, setStudentOverview] = useState<StudentOverviewResponse | null>(null);
  const [loadingStudentOverview, setLoadingStudentOverview] = useState(false);

  // Teacher: Gradebook state
  const [gradebook, setGradebook] = useState<GradebookResponse | null>(null);
  const [loadingGradebook, setLoadingGradebook] = useState(false);

  // Teacher: Create assignment
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newDueAt, setNewDueAt] = useState("");
  const [newFile, setNewFile] = useState<File | null>(null);
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [createSuccess, setCreateSuccess] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  // Teacher: Invite student
  const [studentEmail, setStudentEmail] = useState("");
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteMsg, setInviteMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Teacher: View categorized submissions
  const [selectedAssignment, setSelectedAssignment] = useState<AssignmentResponse | null>(null);
  const [categorizedSubs, setCategorizedSubs] = useState<CategorizedSubmissionsResponse | null>(null);
  const [submissionCategory, setSubmissionCategory] = useState<"on_time" | "late" | "missed" | "pending">("on_time");
  const [loadingSubmissions, setLoadingSubmissions] = useState(false);

  // Grading form state (per student)
  const [gradingState, setGradingState] = useState<{
    [studentUserId: string]: { score: string; feedback: string; saving: boolean; saved: boolean; error?: string };
  }>({});

  // Student: Submit assignment form inline
  const [submittingFor, setSubmittingFor] = useState<string | null>(null);
  const [submitFile, setSubmitFile] = useState<File | null>(null);
  const [studentRoll, setStudentRoll] = useState("");
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitMsg, setSubmitMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const submitFileRef = useRef<HTMLInputElement>(null);

  const loadAssignments = async () => {
    if (!classroomId) return;
    setLoadingAssignments(true);
    try {
      const data = await api.listAssignments(classroomId);
      setAssignments(data);
    } catch {
      // ignore
    } finally {
      setLoadingAssignments(false);
    }
  };

  const loadNotes = async () => {
    if (!classroomId) return;
    setLoadingNotes(true);
    try {
      const data = await api.listClassroomNotes(classroomId);
      setNotes(data);
    } catch {
      // ignore
    } finally {
      setLoadingNotes(false);
    }
  };

  const loadStudentOverview = async () => {
    if (!classroomId || isTeacher) return;
    setLoadingStudentOverview(true);
    try {
      const data = await api.getStudentOverview(classroomId);
      setStudentOverview(data);
    } catch {
      // ignore
    } finally {
      setLoadingStudentOverview(false);
    }
  };

  const loadGradebook = async () => {
    if (!classroomId || !isTeacher) return;
    setLoadingGradebook(true);
    try {
      const data = await api.getClassroomGradebook(classroomId);
      setGradebook(data);
    } catch {
      // ignore
    } finally {
      setLoadingGradebook(false);
    }
  };

  const loadAllContent = () => {
    loadAssignments();
    loadNotes();
    if (isTeacher) {
      loadGradebook();
    } else {
      loadStudentOverview();
    }
  };

  useEffect(() => {
    if (isOpen && classroomId) {
      loadAllContent();
    }
  }, [isOpen, classroomId, isTeacher]);

  const handleCreateAssignment = async () => {
    if (!newTitle.trim()) {
      setCreateError("Title is required.");
      return;
    }
    setCreateLoading(true);
    setCreateError(null);
    try {
      const fd = new FormData();
      fd.append("title", newTitle);
      if (newDesc) fd.append("description", newDesc);
      if (newDueAt) fd.append("due_at", new Date(newDueAt).toISOString());
      if (newFile) fd.append("file", newFile);
      await api.createAssignment(classroomId, fd);
      setCreateSuccess(true);
      setNewTitle("");
      setNewDesc("");
      setNewDueAt("");
      setNewFile(null);
      setShowCreateForm(false);
      loadAssignments();
      if (isTeacher) loadGradebook();
      setTimeout(() => setCreateSuccess(false), 3000);
    } catch (e: any) {
      setCreateError(e.message);
    } finally {
      setCreateLoading(false);
    }
  };

  const handleInviteStudent = async () => {
    if (!studentEmail.trim()) return;
    setInviteLoading(true);
    setInviteMsg(null);
    try {
      await api.inviteStudent(classroomId, studentEmail);
      setInviteMsg({ type: "success", text: `Invitation sent to ${studentEmail}` });
      setStudentEmail("");
      if (isTeacher) loadGradebook();
    } catch (e: any) {
      setInviteMsg({ type: "error", text: e.message });
    } finally {
      setInviteLoading(false);
    }
  };

  const handleViewCategorizedSubmissions = async (assignment: AssignmentResponse) => {
    setSelectedAssignment(assignment);
    setLoadingSubmissions(true);
    try {
      const data = await api.getCategorizedSubmissions(classroomId, assignment.id);
      setCategorizedSubs(data);
      const initialGrading: typeof gradingState = {};
      const allStudents = [...data.on_time, ...data.late, ...data.missed, ...data.pending];
      allStudents.forEach((st) => {
        initialGrading[st.student_user_id] = {
          score: st.grade?.score !== null && st.grade?.score !== undefined ? String(st.grade.score) : "",
          feedback: st.grade?.feedback || "",
          saving: false,
          saved: false,
        };
      });
      setGradingState(initialGrading);
      if (data.on_time.length > 0) setSubmissionCategory("on_time");
      else if (data.late.length > 0) setSubmissionCategory("late");
      else if (data.missed.length > 0) setSubmissionCategory("missed");
      else setSubmissionCategory("pending");
    } catch {
      setCategorizedSubs(null);
    } finally {
      setLoadingSubmissions(false);
    }
  };

  const handleSaveGrade = async (studentUserId: string) => {
    if (!selectedAssignment) return;
    const current = gradingState[studentUserId] || { score: "", feedback: "" };
    const numScore = parseFloat(current.score);
    if (isNaN(numScore) || numScore < 0) {
      setGradingState((prev) => ({
        ...prev,
        [studentUserId]: { ...prev[studentUserId], error: "Enter valid score (>= 0)" },
      }));
      return;
    }

    setGradingState((prev) => ({
      ...prev,
      [studentUserId]: { ...prev[studentUserId], saving: true, error: undefined, saved: false },
    }));

    try {
      await api.gradeSubmission(classroomId, selectedAssignment.id, {
        student_user_id: studentUserId,
        score: numScore,
        feedback: current.feedback.trim() || undefined,
      });

      setGradingState((prev) => ({
        ...prev,
        [studentUserId]: { ...prev[studentUserId], saving: false, saved: true },
      }));

      const refreshed = await api.getCategorizedSubmissions(classroomId, selectedAssignment.id);
      setCategorizedSubs(refreshed);
      loadGradebook();

      setTimeout(() => {
        setGradingState((prev) => ({
          ...prev,
          [studentUserId]: { ...prev[studentUserId], saved: false },
        }));
      }, 2500);
    } catch (e: any) {
      setGradingState((prev) => ({
        ...prev,
        [studentUserId]: { ...prev[studentUserId], saving: false, error: e.message },
      }));
    }
  };

  const handleSubmitAssignment = async (assignmentId: string) => {
    if (!submitFile) {
      setSubmitMsg({ type: "error", text: "Please select a PDF file." });
      return;
    }
    setSubmitLoading(true);
    setSubmitMsg(null);
    try {
      const fd = new FormData();
      fd.append("file", submitFile);
      if (studentRoll.trim()) {
        fd.append("roll_number", studentRoll.trim().toUpperCase());
      }
      await api.submitAssignment(classroomId, assignmentId, fd);
      setSubmitMsg({ type: "success", text: "Assignment submitted successfully!" });
      setSubmittingFor(null);
      setSubmitFile(null);
      setStudentRoll("");
      loadStudentOverview();
      loadAssignments();
    } catch (e: any) {
      setSubmitMsg({ type: "error", text: e.message });
    } finally {
      setSubmitLoading(false);
    }
  };

  if (!isOpen) return null;

  const cardStyle: React.CSSProperties = {
    background: "rgba(16, 16, 16, 0.65)",
    backdropFilter: "blur(16px)",
    WebkitBackdropFilter: "blur(16px)",
    border: "1px solid rgba(222,219,200,0.12)",
    borderRadius: "18px",
    padding: "20px 24px",
    marginBottom: "14px",
    boxShadow: "0 10px 30px -10px rgba(0, 0, 0, 0.5)",
  };

  const inputStyle: React.CSSProperties = {
    width: "100%",
    background: "rgba(12, 12, 12, 0.75)",
    backdropFilter: "blur(10px)",
    WebkitBackdropFilter: "blur(10px)",
    border: "1px solid rgba(222,219,200,0.16)",
    borderRadius: "12px",
    color: "#E1E0CC",
    padding: "11px 16px",
    fontSize: "13px",
    outline: "none",
    boxSizing: "border-box" as const,
  };

  const btnPrimary: React.CSSProperties = {
    background: "#DEDBC8",
    color: "#000",
    border: "none",
    borderRadius: "9999px",
    padding: "10px 22px",
    fontSize: "12px",
    fontWeight: 600,
    cursor: "pointer",
    letterSpacing: "0.5px",
    transition: "all 0.2s ease",
  };

  const pillBadge = (text: string, color: string, bg: string, border: string) => (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "5px",
        padding: "3px 10px",
        borderRadius: "9999px",
        fontSize: "11px",
        fontWeight: 600,
        color,
        background: bg,
        border: `1px solid ${border}`,
        letterSpacing: "0.4px",
      }}
    >
      {text}
    </span>
  );

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 p-3 sm:p-5 md:p-6 bg-black/80 backdrop-blur-md overflow-y-auto flex items-center justify-center"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: 20 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="relative w-full max-w-5xl max-h-[92vh] overflow-y-auto rounded-2xl md:rounded-[2rem] bg-black border border-white/[0.14] shadow-2xl p-6 sm:p-10 my-auto"
        >
          {/* Background Video with Cinematic blur */}
          <div className="absolute inset-0 w-full h-full -z-10 overflow-hidden pointer-events-none">
            <CinematicVideo
              src={VIDEO_URL}
              className="w-full h-full object-cover scale-105 filter brightness-[0.38] contrast-[1.1] blur-[3px]"
            />
            <div className="noise-overlay absolute inset-0 opacity-[0.55] mix-blend-overlay pointer-events-none" />
            <div className="absolute inset-0 bg-gradient-to-b from-black/75 via-black/85 to-black/95 pointer-events-none" />
          </div>

          {/* Close button */}
          <button
            onClick={selectedAssignment ? () => setSelectedAssignment(null) : onClose}
            className="absolute top-5 right-5 p-2 rounded-full bg-white/5 hover:bg-white/10 text-[#E1E0CC]/70 hover:text-[#E1E0CC] border border-white/10 transition-colors cursor-pointer"
            title={selectedAssignment ? "Back to assignments" : "Close classroom"}
          >
            {selectedAssignment ? <ArrowLeft size={18} /> : <X size={18} />}
          </button>

          {/* Header */}
          <div style={{ marginBottom: "26px" }}>
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
                marginBottom: "12px",
              }}
            >
              ● {isTeacher ? "Teacher Cockpit" : "Student View"}
            </div>
            <h1 style={{ color: "#E1E0CC", fontSize: "28px", fontWeight: 500, letterSpacing: "-0.03em" }}>
              {selectedAssignment ? `Submissions & Grading: ${selectedAssignment.title}` : classroomName}
            </h1>
          </div>

          <div style={{ height: "1px", background: "rgba(255,255,255,0.08)", marginBottom: "26px" }} />

          {/* TEACHER: CATEGORIZED SUBMISSIONS & GRADING VIEW */}
          {selectedAssignment && (
            <div>
              {loadingSubmissions ? (
                <p style={{ color: "rgba(222,219,200,0.5)", textAlign: "center", padding: "40px 0" }}>
                  Loading categorized submissions…
                </p>
              ) : !categorizedSubs ? (
                <p style={{ color: "rgba(222,219,200,0.5)", textAlign: "center", padding: "40px 0" }}>
                  Could not load submissions.
                </p>
              ) : (
                <div>
                  {/* Category switcher tabs */}
                  <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", marginBottom: "22px" }}>
                    <button
                      type="button"
                      onClick={() => setSubmissionCategory("on_time")}
                      style={{
                        ...btnPrimary,
                        background: submissionCategory === "on_time" ? "#22c55e" : "rgba(34, 197, 94, 0.12)",
                        color: submissionCategory === "on_time" ? "#000" : "#86efac",
                        border: "1px solid rgba(34, 197, 94, 0.3)",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <CheckCircle2 size={13} />
                      Completed on Time ({categorizedSubs.summary.on_time_count})
                    </button>

                    <button
                      type="button"
                      onClick={() => setSubmissionCategory("late")}
                      style={{
                        ...btnPrimary,
                        background: submissionCategory === "late" ? "#f59e0b" : "rgba(245, 158, 11, 0.12)",
                        color: submissionCategory === "late" ? "#000" : "#fcd34d",
                        border: "1px solid rgba(245, 158, 11, 0.3)",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <Clock size={13} />
                      Submitted Late ({categorizedSubs.summary.late_count})
                    </button>

                    <button
                      type="button"
                      onClick={() => setSubmissionCategory("missed")}
                      style={{
                        ...btnPrimary,
                        background: submissionCategory === "missed" ? "#ef4444" : "rgba(239, 68, 68, 0.12)",
                        color: submissionCategory === "missed" ? "#fff" : "#fca5a5",
                        border: "1px solid rgba(239, 68, 68, 0.3)",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <ShieldAlert size={13} />
                      Missed Deadline ({categorizedSubs.summary.missed_count})
                    </button>

                    <button
                      type="button"
                      onClick={() => setSubmissionCategory("pending")}
                      style={{
                        ...btnPrimary,
                        background: submissionCategory === "pending" ? "#94a3b8" : "rgba(148, 163, 184, 0.12)",
                        color: submissionCategory === "pending" ? "#000" : "#cbd5e1",
                        border: "1px solid rgba(148, 163, 184, 0.3)",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <Clock size={13} />
                      Pending / In Progress ({categorizedSubs.summary.pending_count})
                    </button>
                  </div>

                  {/* Category students list */}
                  {categorizedSubs[submissionCategory].length === 0 ? (
                    <div style={{ textAlign: "center", padding: "40px 0" }}>
                      <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "14px" }}>
                        No students in this category.
                      </p>
                    </div>
                  ) : (
                    categorizedSubs[submissionCategory].map((student) => {
                      const stGrading = gradingState[student.student_user_id] || { score: "", feedback: "" };
                      return (
                        <div key={student.student_user_id} style={cardStyle}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px", marginBottom: "16px" }}>
                            <div>
                              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
                                <span
                                  style={{
                                    background: "rgba(222,219,200,0.12)",
                                    borderRadius: "6px",
                                    padding: "2px 8px",
                                    fontSize: "12px",
                                    fontWeight: 600,
                                    color: "#DEDBC8",
                                    fontFamily: "monospace",
                                  }}
                                >
                                  {student.roll_number || "NO ROLL"}
                                </span>
                                <span style={{ color: "#E1E0CC", fontSize: "14px", fontWeight: 500 }}>
                                  {student.email}
                                </span>
                              </div>

                              {student.submission ? (
                                <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "12px" }}>
                                  {student.submission.file_name} · {(student.submission.file_size / 1024).toFixed(0)} KB · Submitted{" "}
                                  {new Date(student.submission.submitted_at).toLocaleString()}
                                </p>
                              ) : (
                                <p style={{ color: "rgba(239, 68, 68, 0.7)", fontSize: "12px" }}>
                                  {submissionCategory === "missed"
                                    ? "No submission uploaded before deadline — Automatically assigned 0."
                                    : "Not yet submitted (deadline pending)."}
                                </p>
                              )}
                            </div>

                            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                              {student.status === "ON_TIME" && pillBadge("On Time", "#86efac", "rgba(34, 197, 94, 0.12)", "rgba(34, 197, 94, 0.3)")}
                              {student.status === "LATE" && pillBadge("Submitted Late", "#fcd34d", "rgba(245, 158, 11, 0.12)", "rgba(245, 158, 11, 0.3)")}
                              {student.status === "MISSED" && pillBadge("Missed Deadline (Auto 0)", "#fca5a5", "rgba(239, 68, 68, 0.12)", "rgba(239, 68, 68, 0.3)")}
                              {student.status === "PENDING" && pillBadge("Pending", "#cbd5e1", "rgba(148, 163, 184, 0.12)", "rgba(148, 163, 184, 0.3)")}

                              {student.submission?.download_url && (
                                <a
                                  href={student.submission.download_url}
                                  download
                                  style={{
                                    ...btnPrimary,
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: "6px",
                                    textDecoration: "none",
                                    padding: "6px 14px",
                                    fontSize: "12px",
                                  }}
                                >
                                  <Download size={13} /> PDF
                                </a>
                              )}
                            </div>
                          </div>

                          {/* Inline Grading Form */}
                          <div
                            style={{
                              background: "rgba(0, 0, 0, 0.4)",
                              border: "1px solid rgba(222, 219, 200, 0.08)",
                              borderRadius: "12px",
                              padding: "14px 16px",
                              display: "flex",
                              flexDirection: "column",
                              gap: "10px",
                            }}
                          >
                            <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
                              <div style={{ width: "130px" }}>
                                <label style={{ display: "block", color: "rgba(222,219,200,0.6)", fontSize: "11px", marginBottom: "4px" }}>
                                  Score (0 - 100)
                                </label>
                                <input
                                  type="number"
                                  min="0"
                                  max="100"
                                  step="0.5"
                                  placeholder="e.g. 95"
                                  value={stGrading.score}
                                  onChange={(e) =>
                                    setGradingState((prev) => ({
                                      ...prev,
                                      [student.student_user_id]: { ...prev[student.student_user_id], score: e.target.value },
                                    }))
                                  }
                                  style={{ ...inputStyle, padding: "8px 12px", fontSize: "13px" }}
                                />
                              </div>

                              <div style={{ flex: 1, minWidth: "220px" }}>
                                <label style={{ display: "block", color: "rgba(222,219,200,0.6)", fontSize: "11px", marginBottom: "4px" }}>
                                  Feedback Remarks
                                </label>
                                <input
                                  type="text"
                                  placeholder="e.g. Excellent clarity and thorough calculations"
                                  value={stGrading.feedback}
                                  onChange={(e) =>
                                    setGradingState((prev) => ({
                                      ...prev,
                                      [student.student_user_id]: { ...prev[student.student_user_id], feedback: e.target.value },
                                    }))
                                  }
                                  style={{ ...inputStyle, padding: "8px 12px", fontSize: "13px" }}
                                />
                              </div>

                              <div style={{ alignSelf: "flex-end" }}>
                                <button
                                  type="button"
                                  disabled={stGrading.saving}
                                  onClick={() => handleSaveGrade(student.student_user_id)}
                                  style={{
                                    ...btnPrimary,
                                    padding: "9px 18px",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "6px",
                                    background: stGrading.saved ? "#22c55e" : "#DEDBC8",
                                    color: "#000",
                                  }}
                                >
                                  {stGrading.saving ? (
                                    "Saving…"
                                  ) : stGrading.saved ? (
                                    <>
                                      <Check size={14} /> Saved
                                    </>
                                  ) : (
                                    "Save Grade"
                                  )}
                                </button>
                              </div>
                            </div>

                            {stGrading.error && (
                              <p style={{ color: "#f87171", fontSize: "12px", margin: 0 }}>
                                {stGrading.error}
                              </p>
                            )}

                            {student.grade?.graded_at && (
                              <p style={{ color: "rgba(222,219,200,0.4)", fontSize: "11px", margin: 0 }}>
                                Last graded on {new Date(student.grade.graded_at).toLocaleString()}
                                {student.grade.is_auto_zero && " (Auto 0 assigned for missed deadline)"}
                              </p>
                            )}
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              )}
            </div>
          )}

          {/* TEACHER & STUDENT MAIN NAVIGATION TABS */}
          {!selectedAssignment && (
            <>
              {/* Teacher Tab Bar */}
              {isTeacher && (
                <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", marginBottom: "26px" }}>
                  <button
                    type="button"
                    onClick={() => setActiveTab("assignments")}
                    style={{
                      ...btnPrimary,
                      background: activeTab === "assignments" ? "#DEDBC8" : "rgba(222,219,200,0.08)",
                      color: activeTab === "assignments" ? "#000" : "#DEDBC8",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                    }}
                  >
                    <FileText size={14} />
                    <span>Curriculum & Assignments ({assignments.length})</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setActiveTab("gradebook");
                      loadGradebook();
                    }}
                    style={{
                      ...btnPrimary,
                      background: activeTab === "gradebook" ? "#DEDBC8" : "rgba(222,219,200,0.08)",
                      color: activeTab === "gradebook" ? "#000" : "#DEDBC8",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                    }}
                  >
                    <BarChart3 size={14} />
                    <span>Academic Record / Gradebook</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setActiveTab("notes")}
                    style={{
                      ...btnPrimary,
                      background: activeTab === "notes" ? "#DEDBC8" : "rgba(222,219,200,0.08)",
                      color: activeTab === "notes" ? "#000" : "#DEDBC8",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                    }}
                  >
                    <BookOpen size={14} />
                    <span>Lecture Notes ({notes.length})</span>
                  </button>
                </div>
              )}

              {/* Student Tab Bar */}
              {!isTeacher && (
                <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", marginBottom: "26px" }}>
                  <button
                    type="button"
                    onClick={() => {
                      setActiveTab("todo");
                      loadStudentOverview();
                    }}
                    style={{
                      ...btnPrimary,
                      background: activeTab === "todo" ? "#DEDBC8" : "rgba(222,219,200,0.08)",
                      color: activeTab === "todo" ? "#000" : "#DEDBC8",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                    }}
                  >
                    <Clock size={14} />
                    <span>To-Do ({studentOverview?.stats.todo_count ?? 0})</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setActiveTab("completed");
                      loadStudentOverview();
                    }}
                    style={{
                      ...btnPrimary,
                      background: activeTab === "completed" ? "#DEDBC8" : "rgba(222,219,200,0.08)",
                      color: activeTab === "completed" ? "#000" : "#DEDBC8",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                    }}
                  >
                    <CheckCircle2 size={14} />
                    <span>Completed ({studentOverview?.stats.completed_count ?? 0})</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setActiveTab("scores");
                      loadStudentOverview();
                    }}
                    style={{
                      ...btnPrimary,
                      background: activeTab === "scores" ? "#DEDBC8" : "rgba(222,219,200,0.08)",
                      color: activeTab === "scores" ? "#000" : "#DEDBC8",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                    }}
                  >
                    <Award size={14} />
                    <span>Scores & Feedback</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setActiveTab("notes")}
                    style={{
                      ...btnPrimary,
                      background: activeTab === "notes" ? "#DEDBC8" : "rgba(222,219,200,0.08)",
                      color: activeTab === "notes" ? "#000" : "#DEDBC8",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                    }}
                  >
                    <BookOpen size={14} />
                    <span>Lecture Notes ({notes.length})</span>
                  </button>
                </div>
              )}

              {/* STUDENT VIEW: TAB 1 (TO-DO PANEL) */}
              {!isTeacher && activeTab === "todo" && (
                <div>
                  {loadingStudentOverview ? (
                    <p style={{ color: "rgba(222,219,200,0.5)", textAlign: "center", padding: "40px 0" }}>
                      Loading pending assignments…
                    </p>
                  ) : !studentOverview || studentOverview.todo.length === 0 ? (
                    <div style={{ textAlign: "center", padding: "40px 0" }}>
                      <CheckCircle2 size={36} style={{ color: "#86efac", margin: "0 auto 12px" }} />
                      <p style={{ color: "#E1E0CC", fontSize: "16px", fontWeight: 500 }}>
                        All caught up! No pending assignments to do.
                      </p>
                    </div>
                  ) : (
                    studentOverview.todo.map((item) => {
                      const a = item.assignment;
                      const isMissed = item.status === "MISSED_DEADLINE";
                      return (
                        <div key={a.id} style={cardStyle}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "14px" }}>
                            <div style={{ flex: 1, minWidth: "260px" }}>
                              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
                                <h3 style={{ color: "#E1E0CC", fontSize: "16px", fontWeight: 500, margin: 0 }}>
                                  {a.title}
                                </h3>
                                {isMissed ? (
                                  pillBadge("Deadline Missed (Auto 0)", "#fca5a5", "rgba(239, 68, 68, 0.12)", "rgba(239, 68, 68, 0.3)")
                                ) : (
                                  pillBadge("To-Do", "#fcd34d", "rgba(245, 158, 11, 0.12)", "rgba(245, 158, 11, 0.3)")
                                )}
                              </div>

                              {a.description && (
                                <p style={{ color: "rgba(222,219,200,0.6)", fontSize: "13px", marginBottom: "10px" }}>
                                  {a.description}
                                </p>
                              )}

                              <div style={{ display: "flex", gap: "14px", alignItems: "center", flexWrap: "wrap" }}>
                                {a.due_at && (
                                  <span
                                    style={{
                                      display: "flex",
                                      alignItems: "center",
                                      gap: "4px",
                                      color: isMissed ? "#f87171" : "rgba(222,219,200,0.6)",
                                      fontSize: "12px",
                                      fontWeight: isMissed ? 600 : 400,
                                    }}
                                  >
                                    <Clock size={12} /> Due {new Date(a.due_at).toLocaleString()}
                                  </span>
                                )}
                                {a.download_url && (
                                  <a
                                    href={a.download_url}
                                    download
                                    style={{
                                      display: "flex",
                                      alignItems: "center",
                                      gap: "4px",
                                      color: "#DEDBC8",
                                      fontSize: "12px",
                                      textDecoration: "none",
                                    }}
                                  >
                                    <Download size={12} /> {a.file_name || "Attachment"}
                                  </a>
                                )}
                              </div>
                            </div>

                            <button
                              onClick={() => {
                                setSubmittingFor(a.id);
                                setSubmitFile(null);
                                setSubmitMsg(null);
                              }}
                              style={{
                                ...btnPrimary,
                                display: "flex",
                                alignItems: "center",
                                gap: "6px",
                                padding: "8px 16px",
                              }}
                            >
                              <Upload size={13} /> {isMissed ? "Submit Late Work" : "Submit Work"}
                            </button>
                          </div>

                          {/* Inline Submit Form */}
                          {submittingFor === a.id && (
                            <div style={{ marginTop: "16px", paddingTop: "16px", borderTop: "1px solid rgba(255,255,255,0.08)" }}>
                              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                                <input
                                  type="text"
                                  placeholder="Confirm Roll Number (e.g. 21CS042)"
                                  value={studentRoll}
                                  onChange={(e) => setStudentRoll(e.target.value)}
                                  style={inputStyle}
                                />
                                <input
                                  ref={submitFileRef}
                                  type="file"
                                  accept=".pdf"
                                  style={{ display: "none" }}
                                  onChange={(e) => setSubmitFile(e.target.files?.[0] || null)}
                                />
                                <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                                  <button
                                    onClick={() => submitFileRef.current?.click()}
                                    style={{
                                      flex: 1,
                                      background: "rgba(222,219,200,0.06)",
                                      border: "1px dashed rgba(222,219,200,0.25)",
                                      borderRadius: "10px",
                                      color: "rgba(222,219,200,0.7)",
                                      padding: "10px",
                                      fontSize: "13px",
                                      cursor: "pointer",
                                    }}
                                  >
                                    {submitFile ? `📎 ${submitFile.name}` : "Select Submission PDF"}
                                  </button>
                                  <button
                                    onClick={() => handleSubmitAssignment(a.id)}
                                    disabled={submitLoading || !submitFile}
                                    style={{ ...btnPrimary, whiteSpace: "nowrap" }}
                                  >
                                    {submitLoading ? "Uploading…" : "SUBMIT NOW →"}
                                  </button>
                                </div>
                              </div>
                              {submitMsg && (
                                <p style={{ marginTop: "8px", fontSize: "13px", color: submitMsg.type === "success" ? "#86efac" : "#f87171" }}>
                                  {submitMsg.text}
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              )}

              {/* STUDENT VIEW: TAB 2 (COMPLETED ACTIVITIES PANEL) */}
              {!isTeacher && activeTab === "completed" && (
                <div>
                  {loadingStudentOverview ? (
                    <p style={{ color: "rgba(222,219,200,0.5)", textAlign: "center", padding: "40px 0" }}>
                      Loading completed submissions…
                    </p>
                  ) : !studentOverview || studentOverview.completed.length === 0 ? (
                    <div style={{ textAlign: "center", padding: "40px 0" }}>
                      <FileText size={36} style={{ color: "rgba(222,219,200,0.3)", margin: "0 auto 12px" }} />
                      <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "14px" }}>
                        No completed assignments yet. Head over to the To-Do tab to submit your work.
                      </p>
                    </div>
                  ) : (
                    studentOverview.completed.map((item) => {
                      const a = item.assignment;
                      const sub = item.submission;
                      const isLate = item.status === "COMPLETED_LATE";
                      return (
                        <div key={a.id} style={cardStyle}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px", marginBottom: "12px" }}>
                            <div>
                              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
                                <h3 style={{ color: "#E1E0CC", fontSize: "16px", fontWeight: 500, margin: 0 }}>
                                  {a.title}
                                </h3>
                                {isLate
                                  ? pillBadge("Submitted Late", "#fcd34d", "rgba(245, 158, 11, 0.12)", "rgba(245, 158, 11, 0.3)")
                                  : pillBadge("Submitted On Time", "#86efac", "rgba(34, 197, 94, 0.12)", "rgba(34, 197, 94, 0.3)")}
                              </div>
                              {sub && (
                                <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "12px" }}>
                                  File: {sub.file_name} · Submitted {new Date(sub.submitted_at).toLocaleString()}
                                </p>
                              )}
                            </div>

                            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                              {sub?.download_url && (
                                <a
                                  href={sub.download_url}
                                  download
                                  style={{
                                    ...btnPrimary,
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: "6px",
                                    textDecoration: "none",
                                    padding: "6px 14px",
                                  }}
                                >
                                  <Download size={13} /> Your PDF
                                </a>
                              )}
                            </div>
                          </div>

                          {item.grade.score !== null ? (
                            <div
                              style={{
                                background: "rgba(222,219,200,0.06)",
                                border: "1px solid rgba(222,219,200,0.15)",
                                borderRadius: "10px",
                                padding: "10px 14px",
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                flexWrap: "wrap",
                                gap: "8px",
                              }}
                            >
                              <div>
                                <span style={{ color: "#DEDBC8", fontSize: "13px", fontWeight: 600 }}>
                                  Marks: {item.grade.score} / 100
                                </span>
                                {item.grade.feedback && (
                                  <p style={{ color: "rgba(222,219,200,0.7)", fontSize: "12px", margin: "4px 0 0" }}>
                                    "{item.grade.feedback}"
                                  </p>
                                )}
                              </div>
                              <span style={{ color: "#86efac", fontSize: "11px", fontWeight: 600 }}>
                                ✓ Graded by Teacher
                              </span>
                            </div>
                          ) : (
                            <div style={{ color: "rgba(222,219,200,0.4)", fontSize: "12px", fontStyle: "italic" }}>
                              Pending teacher review and grading.
                            </div>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              )}

              {/* STUDENT VIEW: TAB 3 (SCORE & ACADEMIC RECORD PANEL) */}
              {!isTeacher && activeTab === "scores" && (
                <div>
                  {loadingStudentOverview ? (
                    <p style={{ color: "rgba(222,219,200,0.5)", textAlign: "center", padding: "40px 0" }}>
                      Loading academic scores…
                    </p>
                  ) : !studentOverview ? (
                    <p style={{ color: "rgba(222,219,200,0.5)", textAlign: "center", padding: "40px 0" }}>
                      Could not load academic scores.
                    </p>
                  ) : (
                    <div>
                      {/* Metric Summary Cards */}
                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                          gap: "14px",
                          marginBottom: "24px",
                        }}
                      >
                        <div style={cardStyle}>
                          <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "11px", textTransform: "uppercase", letterSpacing: "1px", margin: 0 }}>
                            Average Score
                          </p>
                          <h2 style={{ color: "#DEDBC8", fontSize: "28px", fontWeight: 600, margin: "6px 0 0" }}>
                            {studentOverview.stats.average_score !== null ? `${studentOverview.stats.average_score}` : "—"}
                            <span style={{ fontSize: "14px", fontWeight: 400, color: "rgba(222,219,200,0.5)" }}> / 100</span>
                          </h2>
                        </div>

                        <div style={cardStyle}>
                          <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "11px", textTransform: "uppercase", letterSpacing: "1px", margin: 0 }}>
                            Completed
                          </p>
                          <h2 style={{ color: "#86efac", fontSize: "28px", fontWeight: 600, margin: "6px 0 0" }}>
                            {studentOverview.stats.completed_count}
                            <span style={{ fontSize: "14px", fontWeight: 400, color: "rgba(222,219,200,0.5)" }}> / {studentOverview.stats.total_assignments}</span>
                          </h2>
                        </div>

                        <div style={cardStyle}>
                          <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "11px", textTransform: "uppercase", letterSpacing: "1px", margin: 0 }}>
                            Missed Deadlines
                          </p>
                          <h2 style={{ color: "#f87171", fontSize: "28px", fontWeight: 600, margin: "6px 0 0" }}>
                            {studentOverview.stats.missed_count}
                            <span style={{ fontSize: "12px", fontWeight: 400, color: "rgba(248,113,113,0.7)" }}> (Auto 0)</span>
                          </h2>
                        </div>
                      </div>

                      {/* Detailed Score Breakdown */}
                      <h2 style={{ color: "#DEDBC8", fontSize: "16px", fontWeight: 500, marginBottom: "16px", letterSpacing: "0.5px" }}>
                        ASSIGNMENT SCORE BREAKDOWN
                      </h2>

                      {studentOverview.scores.map((item) => {
                        const a = item.assignment;
                        const grd = item.grade;
                        return (
                          <div key={a.id} style={cardStyle}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px", marginBottom: "10px" }}>
                              <div>
                                <h3 style={{ color: "#E1E0CC", fontSize: "16px", fontWeight: 500, margin: "0 0 4px" }}>
                                  {a.title}
                                </h3>
                                <p style={{ color: "rgba(222,219,200,0.4)", fontSize: "12px", margin: 0 }}>
                                  {a.due_at ? `Due: ${new Date(a.due_at).toLocaleDateString()}` : "No deadline"}
                                </p>
                              </div>

                              <div style={{ textAlign: "right" }}>
                                {grd.score !== null ? (
                                  <div>
                                    <span style={{ fontSize: "20px", fontWeight: 700, color: grd.score >= 50 ? "#DEDBC8" : "#f87171" }}>
                                      {grd.score}
                                    </span>
                                    <span style={{ color: "rgba(222,219,200,0.5)", fontSize: "12px" }}> / 100</span>
                                  </div>
                                ) : (
                                  <span style={{ color: "rgba(222,219,200,0.4)", fontSize: "13px" }}>Ungraded</span>
                                )}

                                <div style={{ marginTop: "4px" }}>
                                  {item.status === "COMPLETED_ON_TIME" && pillBadge("On Time", "#86efac", "rgba(34, 197, 94, 0.12)", "rgba(34, 197, 94, 0.3)")}
                                  {item.status === "COMPLETED_LATE" && pillBadge("Late Submission", "#fcd34d", "rgba(245, 158, 11, 0.12)", "rgba(245, 158, 11, 0.3)")}
                                  {item.status === "MISSED_DEADLINE" && pillBadge("Missed Deadline (Auto 0)", "#fca5a5", "rgba(239, 68, 68, 0.12)", "rgba(239, 68, 68, 0.3)")}
                                  {item.status === "TO_DO" && pillBadge("Pending Submission", "#cbd5e1", "rgba(148, 163, 184, 0.12)", "rgba(148, 163, 184, 0.3)")}
                                </div>
                              </div>
                            </div>

                            {grd.feedback && (
                              <div
                                style={{
                                  background: "rgba(222,219,200,0.05)",
                                  borderLeft: "3px solid #DEDBC8",
                                  padding: "8px 12px",
                                  borderRadius: "4px",
                                  marginTop: "8px",
                                }}
                              >
                                <span style={{ color: "rgba(222,219,200,0.5)", fontSize: "11px", textTransform: "uppercase" }}>
                                  Teacher Remarks:
                                </span>
                                <p style={{ color: "#E1E0CC", fontSize: "13px", margin: "2px 0 0" }}>
                                  {grd.feedback}
                                </p>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* TEACHER VIEW: TAB 1 (ASSIGNMENTS LIST & CREATION) */}
              {isTeacher && activeTab === "assignments" && (
                <div>
                  {/* Invite Student Section */}
                  <div style={{ marginBottom: "32px" }}>
                    <h2 style={{ color: "#DEDBC8", fontSize: "16px", fontWeight: 500, marginBottom: "16px", letterSpacing: "0.5px" }}>
                      INVITE STUDENT TO CLASSROOM
                    </h2>
                    <div style={{ display: "flex", gap: "10px" }}>
                      <div style={{ position: "relative", flex: 1 }}>
                        <Mail
                          size={14}
                          style={{
                            position: "absolute",
                            left: "12px",
                            top: "50%",
                            transform: "translateY(-50%)",
                            color: "rgba(222,219,200,0.4)",
                          }}
                        />
                        <input
                          type="email"
                          value={studentEmail}
                          onChange={(e) => setStudentEmail(e.target.value)}
                          placeholder="student@email.com"
                          style={{ ...inputStyle, paddingLeft: "36px" }}
                        />
                      </div>
                      <button onClick={handleInviteStudent} disabled={inviteLoading} style={btnPrimary}>
                        {inviteLoading ? "Sending…" : "INVITE →"}
                      </button>
                    </div>
                    {inviteMsg && (
                      <div
                        style={{
                          marginTop: "10px",
                          fontSize: "13px",
                          color: inviteMsg.type === "success" ? "#86efac" : "#f87171",
                        }}
                      >
                        {inviteMsg.text}
                      </div>
                    )}
                  </div>

                  {/* Create Assignment Header */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                    <h2 style={{ color: "#DEDBC8", fontSize: "16px", fontWeight: 500, letterSpacing: "0.5px" }}>
                      CLASSROOM ASSIGNMENTS
                    </h2>
                    <button
                      onClick={() => setShowCreateForm(!showCreateForm)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        background: "rgba(222,219,200,0.08)",
                        border: "1px solid rgba(222,219,200,0.2)",
                        borderRadius: "9999px",
                        color: "#DEDBC8",
                        padding: "7px 14px",
                        fontSize: "12px",
                        cursor: "pointer",
                      }}
                    >
                      <Plus size={13} /> New Assignment
                    </button>
                  </div>

                  {/* Create Assignment Form */}
                  {showCreateForm && (
                    <div style={cardStyle}>
                      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                        <input
                          value={newTitle}
                          onChange={(e) => setNewTitle(e.target.value)}
                          placeholder="Assignment title (e.g. Midterm Lab Report)"
                          style={inputStyle}
                        />
                        <textarea
                          value={newDesc}
                          onChange={(e) => setNewDesc(e.target.value)}
                          placeholder="Description & instructions (optional)"
                          rows={3}
                          style={{ ...inputStyle, resize: "none" }}
                        />
                        <div>
                          <label style={{ display: "block", color: "rgba(222,219,200,0.6)", fontSize: "11px", marginBottom: "4px" }}>
                            Submission Deadline
                          </label>
                          <input
                            type="datetime-local"
                            value={newDueAt}
                            onChange={(e) => setNewDueAt(e.target.value)}
                            style={{ ...inputStyle }}
                          />
                        </div>
                        <div>
                          <input
                            ref={fileRef}
                            type="file"
                            accept=".pdf"
                            style={{ display: "none" }}
                            onChange={(e) => setNewFile(e.target.files?.[0] || null)}
                          />
                          <button
                            onClick={() => fileRef.current?.click()}
                            style={{
                              background: "rgba(222,219,200,0.06)",
                              border: "1px dashed rgba(222,219,200,0.25)",
                              borderRadius: "10px",
                              color: "rgba(222,219,200,0.6)",
                              padding: "10px 20px",
                              fontSize: "13px",
                              cursor: "pointer",
                              width: "100%",
                            }}
                          >
                            {newFile ? `📎 ${newFile.name}` : "Attach Reference / Question PDF (optional)"}
                          </button>
                        </div>
                        {createError && <p style={{ color: "#f87171", fontSize: "13px" }}>{createError}</p>}
                        <button onClick={handleCreateAssignment} disabled={createLoading} style={btnPrimary}>
                          {createLoading ? "Creating…" : "CREATE ASSIGNMENT →"}
                        </button>
                      </div>
                    </div>
                  )}

                  {createSuccess && (
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#86efac", fontSize: "13px", marginBottom: "16px" }}>
                      <CheckCircle2 size={15} /> Assignment created successfully!
                    </div>
                  )}

                  {/* Assignments List */}
                  {loadingAssignments ? (
                    <p style={{ color: "rgba(222,219,200,0.5)", textAlign: "center", padding: "40px 0" }}>
                      Loading assignments…
                    </p>
                  ) : assignments.length === 0 ? (
                    <div style={{ textAlign: "center", padding: "40px 0" }}>
                      <FileText size={32} style={{ color: "rgba(222,219,200,0.3)", margin: "0 auto 12px" }} />
                      <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "14px" }}>
                        No assignments created yet.
                      </p>
                    </div>
                  ) : (
                    assignments.map((a) => (
                      <div key={a.id} style={cardStyle}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px" }}>
                          <div style={{ flex: 1, minWidth: "260px" }}>
                            <h3 style={{ color: "#E1E0CC", fontSize: "16px", fontWeight: 500, marginBottom: "6px" }}>
                              {a.title}
                            </h3>
                            {a.description && (
                              <p style={{ color: "rgba(222,219,200,0.6)", fontSize: "13px", marginBottom: "8px" }}>
                                {a.description}
                              </p>
                            )}
                            <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
                              {a.due_at && (
                                <span style={{ display: "flex", alignItems: "center", gap: "4px", color: "rgba(222,219,200,0.5)", fontSize: "12px" }}>
                                  <Clock size={12} /> Due {new Date(a.due_at).toLocaleString()}
                                </span>
                              )}
                              {a.download_url && (
                                <a
                                  href={a.download_url}
                                  download
                                  style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "4px",
                                    color: "#DEDBC8",
                                    fontSize: "12px",
                                    textDecoration: "none",
                                  }}
                                >
                                  <Download size={12} /> {a.file_name}
                                </a>
                              )}
                            </div>
                          </div>

                          <div>
                            <button
                              onClick={() => handleViewCategorizedSubmissions(a)}
                              style={{
                                ...btnPrimary,
                                display: "flex",
                                alignItems: "center",
                                gap: "6px",
                                padding: "8px 16px",
                              }}
                            >
                              <Users size={13} /> Submissions & Grading
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* TEACHER VIEW: TAB 2 (STUDENT ACADEMIC RECORD / GRADEBOOK) */}
              {isTeacher && activeTab === "gradebook" && (
                <div>
                  {loadingGradebook ? (
                    <p style={{ color: "rgba(222,219,200,0.5)", textAlign: "center", padding: "40px 0" }}>
                      Loading academic gradebook…
                    </p>
                  ) : !gradebook ? (
                    <p style={{ color: "rgba(222,219,200,0.5)", textAlign: "center", padding: "40px 0" }}>
                      Could not load academic record.
                    </p>
                  ) : (
                    <div>
                      {/* Gradebook Class Stats */}
                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                          gap: "14px",
                          marginBottom: "24px",
                        }}
                      >
                        <div style={cardStyle}>
                          <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "11px", textTransform: "uppercase", letterSpacing: "1px", margin: 0 }}>
                            Total Enrolled Students
                          </p>
                          <h2 style={{ color: "#DEDBC8", fontSize: "28px", fontWeight: 600, margin: "6px 0 0" }}>
                            {gradebook.stats.total_students}
                          </h2>
                        </div>

                        <div style={cardStyle}>
                          <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "11px", textTransform: "uppercase", letterSpacing: "1px", margin: 0 }}>
                            Total Assignments
                          </p>
                          <h2 style={{ color: "#DEDBC8", fontSize: "28px", fontWeight: 600, margin: "6px 0 0" }}>
                            {gradebook.stats.total_assignments}
                          </h2>
                        </div>

                        <div style={cardStyle}>
                          <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "11px", textTransform: "uppercase", letterSpacing: "1px", margin: 0 }}>
                            Class Average Score
                          </p>
                          <h2 style={{ color: "#86efac", fontSize: "28px", fontWeight: 600, margin: "6px 0 0" }}>
                            {gradebook.stats.class_average !== null ? `${gradebook.stats.class_average}` : "—"}
                            <span style={{ fontSize: "14px", fontWeight: 400, color: "rgba(222,219,200,0.5)" }}> / 100</span>
                          </h2>
                        </div>
                      </div>

                      {/* Gradebook Table */}
                      <h2 style={{ color: "#DEDBC8", fontSize: "16px", fontWeight: 500, marginBottom: "16px", letterSpacing: "0.5px" }}>
                        STUDENT ACADEMIC RECORD
                      </h2>

                      {gradebook.students.length === 0 ? (
                        <div style={{ textAlign: "center", padding: "40px 0" }}>
                          <Users size={32} style={{ color: "rgba(222,219,200,0.3)", margin: "0 auto 12px" }} />
                          <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "14px" }}>
                            No students enrolled yet. Invite students above to maintain their academic records.
                          </p>
                        </div>
                      ) : (
                        <div style={{ overflowX: "auto" }}>
                          <table
                            style={{
                              width: "100%",
                              borderCollapse: "separate",
                              borderSpacing: "0 8px",
                              color: "#E1E0CC",
                              fontSize: "13px",
                            }}
                          >
                            <thead>
                              <tr style={{ color: "rgba(222,219,200,0.5)", fontSize: "11px", textTransform: "uppercase", textAlign: "left" }}>
                                <th style={{ padding: "10px 16px" }}>Roll No</th>
                                <th style={{ padding: "10px 16px" }}>Student Email</th>
                                {gradebook.assignments.map((a) => (
                                  <th key={a.id} style={{ padding: "10px 16px", minWidth: "120px" }}>
                                    {a.title}
                                  </th>
                                ))}
                                <th style={{ padding: "10px 16px", textAlign: "right" }}>Total</th>
                                <th style={{ padding: "10px 16px", textAlign: "right" }}>Average</th>
                              </tr>
                            </thead>
                            <tbody>
                              {gradebook.students.map((student) => (
                                <tr
                                  key={student.student_user_id}
                                  style={{
                                    background: "rgba(16, 16, 16, 0.65)",
                                    backdropFilter: "blur(14px)",
                                    border: "1px solid rgba(222,219,200,0.08)",
                                    borderRadius: "12px",
                                  }}
                                >
                                  <td style={{ padding: "14px 16px", fontFamily: "monospace", fontWeight: 600, color: "#DEDBC8" }}>
                                    {student.roll_number || "—"}
                                  </td>
                                  <td style={{ padding: "14px 16px" }}>
                                    {student.email}
                                  </td>
                                  {student.grades.map((g) => (
                                    <td key={g.assignment_id} style={{ padding: "14px 16px" }}>
                                      {g.score !== null ? (
                                        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                                          <span style={{ fontWeight: 600, color: g.score >= 50 ? "#DEDBC8" : "#f87171" }}>
                                            {g.score}
                                          </span>
                                          {g.is_auto_zero && (
                                            <span
                                              title="Automatically assigned 0 due to missed deadline without submission"
                                              style={{
                                                fontSize: "10px",
                                                background: "rgba(239,68,68,0.2)",
                                                color: "#fca5a5",
                                                padding: "1px 5px",
                                                borderRadius: "4px",
                                              }}
                                            >
                                              Auto 0
                                            </span>
                                          )}
                                        </div>
                                      ) : g.status === "PENDING" ? (
                                        <span style={{ color: "rgba(222,219,200,0.3)" }}>Pending</span>
                                      ) : (
                                        <span style={{ color: "#fcd34d", fontSize: "11px" }}>Submitted</span>
                                      )}
                                    </td>
                                  ))}
                                  <td style={{ padding: "14px 16px", textAlign: "right", fontWeight: 600, color: "#DEDBC8" }}>
                                    {student.total_score}
                                  </td>
                                  <td style={{ padding: "14px 16px", textAlign: "right", fontWeight: 600, color: "#86efac" }}>
                                    {student.average_score !== null ? `${student.average_score}%` : "—"}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* LECTURE NOTES & READING MATERIALS (BOTH ROLES) */}
              {activeTab === "notes" && (
                <div>
                  {loadingNotes ? (
                    <p style={{ color: "rgba(222,219,200,0.5)", textAlign: "center", padding: "40px 0" }}>
                      Loading lecture notes…
                    </p>
                  ) : notes.length === 0 ? (
                    <div style={{ textAlign: "center", padding: "40px 0" }}>
                      <BookOpen size={32} style={{ color: "rgba(222,219,200,0.3)", margin: "0 auto 12px" }} />
                      <p style={{ color: "rgba(222,219,200,0.5)", fontSize: "14px" }}>
                        No lecture notes uploaded yet for this classroom.
                      </p>
                    </div>
                  ) : (
                    notes.map((n) => (
                      <div key={n.id} style={cardStyle}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <div>
                            <h3 style={{ color: "#E1E0CC", fontSize: "16px", fontWeight: 500, marginBottom: "4px" }}>
                              {n.title}
                            </h3>
                            {n.description && (
                              <p style={{ color: "rgba(222,219,200,0.6)", fontSize: "13px", marginBottom: "6px" }}>
                                {n.description}
                              </p>
                            )}
                            <p style={{ color: "rgba(222,219,200,0.4)", fontSize: "11px" }}>
                              {n.file_name} · {(n.file_size / 1024).toFixed(0)} KB · Uploaded{" "}
                              {new Date(n.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          {n.download_url && (
                            <a
                              href={n.download_url}
                              download
                              style={{
                                ...btnPrimary,
                                display: "flex",
                                alignItems: "center",
                                gap: "6px",
                                textDecoration: "none",
                                padding: "8px 14px",
                              }}
                            >
                              <Download size={14} /> Download PDF
                            </a>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
