import React, { useState, useEffect, useRef, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  ShieldCheck,
  UserPlus,
  Mail,
  Send,
  Building2,
  Sparkles,
  CheckCircle2,
  School,
  GraduationCap,
  Plus,
  Users,
  AlertCircle,
  ChevronRight,
  UploadCloud,
  FileSpreadsheet,
  UserCheck,
  LogOut,
  Layers,
} from "lucide-react";
import { CinematicVideo } from "./CinematicVideo";
import { api, type WorkspaceResponse, type WorkspaceItem, type WorkspaceMember, type ClassroomResponse } from "../services/api";
import { ClassroomDashboard } from "./ClassroomDashboard";

interface WorkspaceCardProps {
  isOpen: boolean;
  onClose: () => void;
  onSignOut?: () => void;
  currentUserEmail?: string;
  initialRole?: string;
}

export const WorkspaceCard: React.FC<WorkspaceCardProps> = ({
  isOpen,
  onClose,
  onSignOut,
  currentUserEmail = "head.director@university.edu",
  initialRole,
}) => {
  const VIDEO_URL =
    "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260405_170732_8a9ccda6-5cff-4628-b164-059c500a2b41.mp4";

  // Workspace State
  const [workspace, setWorkspace] = useState<WorkspaceResponse | null>(null);
  const [userRole, setUserRole] = useState<string>(initialRole || "OWNER");
  const [loadingWorkspace, setLoadingWorkspace] = useState(true);

  // Synchronize internal userRole when initialRole prop updates
  useEffect(() => {
    if (initialRole) {
      setUserRole(initialRole);
    }
  }, [initialRole]);

  // Multi-Workspace Directory State
  const [allWorkspaces, setAllWorkspaces] = useState<WorkspaceItem[]>([]);
  const [isSelectingWorkspace, setIsSelectingWorkspace] = useState(false);

  // Creation form state (if creating a new one)
  const [isCreatingNew, setIsCreatingNew] = useState(false);
  const [newWsName, setNewWsName] = useState("");
  const [newWsDesc, setNewWsDesc] = useState("");
  const [wsLoading, setWsLoading] = useState(false);

  // Owner management sub-tab: 'teachers' | 'students'
  const [ownerTab, setOwnerTab] = useState<"teachers" | "students">("teachers");
  // Teacher management sub-tab: 'students' | 'roster'
  const [teacherTab, setTeacherTab] = useState<"students" | "roster">("students");

  // Single Student Invite State
  const [singleStudentEmail, setSingleStudentEmail] = useState("");
  const [singleStudentLoading, setSingleStudentLoading] = useState(false);

  // Invite Teacher State
  const [teacherEmail, setTeacherEmail] = useState("");
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteSuccess, setInviteSuccess] = useState<string | null>(null);
  const [inviteError, setInviteError] = useState<string | null>(null);

  // Batch Student Invite State
  const [batchEmails, setBatchEmails] = useState("");
  const [batchLoading, setBatchLoading] = useState(false);
  const [batchResult, setBatchResult] = useState<{ message: string; total_invited: number } | null>(null);
  const [batchError, setBatchError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Members List from Live Backend & 3-Button Filter State
  const [members, setMembers] = useState<WorkspaceMember[]>([]);
  const [teachers, setTeachers] = useState<WorkspaceMember[]>([]);
  const [updatingUserId, setUpdatingUserId] = useState<string | null>(null);
  const [memberRoleFilter, setMemberRoleFilter] = useState<"ALL" | "ADMIN" | "TEACHER" | "STUDENT">("ALL");

  const effectiveMembers = members.length > 0 ? members : teachers;
  const adminMembers = useMemo(
    () => effectiveMembers.filter((m) => m.role?.toUpperCase() === "OWNER" || m.role?.toUpperCase() === "ADMIN"),
    [effectiveMembers]
  );
  const teacherMembers = useMemo(
    () => effectiveMembers.filter((m) => m.role?.toUpperCase() === "TEACHER"),
    [effectiveMembers]
  );
  const studentMembers = useMemo(
    () => effectiveMembers.filter((m) => m.role?.toUpperCase() === "STUDENT"),
    [effectiveMembers]
  );
  const displayedMembers = useMemo(() => {
    switch (memberRoleFilter) {
      case "ADMIN":
        return adminMembers;
      case "TEACHER":
        return teacherMembers;
      case "STUDENT":
        return studentMembers;
      default:
        return effectiveMembers;
    }
  }, [memberRoleFilter, effectiveMembers, adminMembers, teacherMembers, studentMembers]);

  // Classrooms State
  const [classrooms, setClassrooms] = useState<ClassroomResponse[]>([]);
  const [newClassroomName, setNewClassroomName] = useState("");
  const [selectedTeacherId, setSelectedTeacherId] = useState("");
  const [classroomSuccess, setClassroomSuccess] = useState(false);

  // Active classroom dashboard (restores from localStorage if page is refreshed)
  const [activeClassroom, setActiveClassroom] = useState<ClassroomResponse | null>(() => {
    try {
      const saved = localStorage.getItem("gradify_active_classroom");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const handleOpenClassroom = (c: ClassroomResponse) => {
    setActiveClassroom(c);
    try {
      localStorage.setItem("gradify_active_classroom", JSON.stringify(c));
      localStorage.setItem("gradify_nav_state", "classroom");
      const url = new URL(window.location.href);
      url.searchParams.set("classroom", c.id);
      window.history.replaceState({}, document.title, url.toString());
    } catch (err) {
      console.error(err);
    }
  };

  const handleCloseClassroom = () => {
    setActiveClassroom(null);
    localStorage.removeItem("gradify_active_classroom");
    localStorage.setItem("gradify_nav_state", "workspace");
    const url = new URL(window.location.href);
    url.searchParams.delete("classroom");
    window.history.replaceState({}, document.title, url.toString());
  };

  // Load User Workspace, Members, Teachers & Classrooms
  const loadWorkspaceData = async (targetSlug?: string) => {
    setLoadingWorkspace(true);
    try {
      const savedSlug = targetSlug || localStorage.getItem("gradify_active_workspace_slug") || undefined;
      const myWs = await api.getMyWorkspace(savedSlug);
      if (myWs) {
        const available = myWs.workspaces || [];
        setAllWorkspaces(available);

        // If user has multiple workspaces and no specific workspace was passed / stored
        if (available.length > 1 && !savedSlug) {
          setIsSelectingWorkspace(true);
          setWorkspace(null);
          setLoadingWorkspace(false);
          return;
        }

        setIsSelectingWorkspace(false);
        localStorage.setItem("gradify_active_workspace_slug", myWs.slug);

        setWorkspace({
          id: myWs.slug,
          name: myWs.workspace_name,
          slug: myWs.slug,
        });
        if (myWs.role) {
          setUserRole(myWs.role);
          localStorage.setItem("gradify_user_role", myWs.role);
        }
        // Fetch all members (if admin/owner)
        try {
          const list = await api.getWorkspaceMembers(myWs.slug);
          setMembers(list);
        } catch {
          // If unauthenticated or no members
        }
        // Fetch faculty teachers (accessible by everyone including students)
        try {
          const tList = await api.getWorkspaceTeachers(myWs.slug);
          setTeachers(tList);
        } catch {
          // ignore
        }
        // Fetch classrooms
        try {
          const cls = await api.listClassrooms(myWs.slug);
          setClassrooms(cls);

          // Verify or restore active classroom on page refresh / URL query
          const params = new URLSearchParams(window.location.search);
          const classroomIdFromUrl = params.get("classroom");
          const savedActive = localStorage.getItem("gradify_active_classroom");
          let targetId = classroomIdFromUrl;
          if (!targetId && savedActive) {
            try {
              targetId = JSON.parse(savedActive).id;
            } catch {
              // ignore
            }
          }

          if (targetId) {
            const matched = cls.find((c) => c.id === targetId);
            if (matched) {
              setActiveClassroom(matched);
              localStorage.setItem("gradify_active_classroom", JSON.stringify(matched));
              localStorage.setItem("gradify_nav_state", "classroom");
              const url = new URL(window.location.href);
              url.searchParams.set("classroom", matched.id);
              window.history.replaceState({}, document.title, url.toString());
            } else {
              // Classroom not in available list
              setActiveClassroom(null);
              localStorage.removeItem("gradify_active_classroom");
              localStorage.setItem("gradify_nav_state", "workspace");
              const url = new URL(window.location.href);
              url.searchParams.delete("classroom");
              window.history.replaceState({}, document.title, url.toString());
            }
          }
        } catch {
          // ignore
        }
      } else {
        setAllWorkspaces([]);
        setWorkspace(null);
        setIsSelectingWorkspace(false);
      }
    } catch {
      setWorkspace(null);
      setAllWorkspaces([]);
      setIsSelectingWorkspace(false);
    } finally {
      setLoadingWorkspace(false);
    }
  };

  const handleSelectWorkspace = (ws: WorkspaceItem) => {
    localStorage.setItem("gradify_active_workspace_slug", ws.slug);
    setIsSelectingWorkspace(false);
    loadWorkspaceData(ws.slug);
  };

  const handleOpenWorkspaceSelector = () => {
    setIsCreatingNew(false);
    setIsSelectingWorkspace(true);
  };

  useEffect(() => {
    if (isOpen) {
      loadWorkspaceData();
    }
  }, [isOpen]);

  // Handle Batch Student Invitations
  const handleBatchInvite = async () => {
    if (!workspace) return;
    const emails = batchEmails
      .split(/[\n,;]+/)
      .map((e) => e.trim().toLowerCase())
      .filter((e) => e && e.includes("@"));

    if (emails.length === 0) {
      setBatchError("Please enter or upload at least one valid student email address.");
      return;
    }

    setBatchLoading(true);
    setBatchResult(null);
    setBatchError(null);
    try {
      const res = await api.batchInviteStudents(workspace.slug, emails);
      setBatchResult({ message: res.message, total_invited: res.total_invited });
      setBatchEmails("");
      loadWorkspaceData();
      setTimeout(() => setBatchResult(null), 6000);
    } catch (err: any) {
      setBatchError(err.message || "Failed to batch invite students");
      setTimeout(() => setBatchError(null), 5000);
    } finally {
      setBatchLoading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      if (text) {
        const matches = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g);
        if (matches && matches.length > 0) {
          const unique = Array.from(new Set(matches.map((m) => m.toLowerCase())));
          setBatchEmails(unique.join("\n"));
        } else {
          setBatchError("No valid email addresses found in the selected file.");
        }
      }
    };
    reader.readAsText(file);
  };

  // Handle Workspace Creation
  const handleCreateWorkspace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWsName.trim()) return;
    setWsLoading(true);
    try {
      const res = await api.createWorkspace(newWsName, newWsDesc);
      localStorage.setItem("gradify_active_workspace_slug", res.slug);
      setWorkspace(res);
      setUserRole("OWNER");
      setIsCreatingNew(false);
      setIsSelectingWorkspace(false);
      setNewWsName("");
      setNewWsDesc("");
      loadWorkspaceData(res.slug);
    } catch (err: any) {
      console.error(err);
    } finally {
      setWsLoading(false);
    }
  };

  // Handle Teacher Invitation (Owner feature)
  const handleInviteTeacher = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!teacherEmail.trim() || !workspace) return;
    setInviteLoading(true);
    setInviteSuccess(null);
    setInviteError(null);
    try {
      await api.inviteTeacher(workspace.slug, teacherEmail.trim());
      setInviteSuccess(`Invitation email dispatched to ${teacherEmail}. Teacher can set password and join!`);
      setTeacherEmail("");
      loadWorkspaceData();
      setTimeout(() => setInviteSuccess(null), 5000);
    } catch (err: any) {
      setInviteError(err.message || "Failed to invite teacher");
      setTimeout(() => setInviteError(null), 4000);
    } finally {
      setInviteLoading(false);
    }
  };

  // Handle Changing Member Role (Admin/Owner feature)
  const handleRoleChange = async (userId: string, newRole: string) => {
    if (!workspace) return;
    setUpdatingUserId(userId);
    try {
      await api.updateMemberRole(workspace.slug, userId, newRole);
      // Update locally
      setMembers((prev) =>
        prev.map((m) => (m.user_id === userId ? { ...m, role: newRole as any } : m))
      );
      setInviteSuccess(`Role updated to ${newRole} successfully`);
      setTimeout(() => setInviteSuccess(null), 3000);
    } catch (err: any) {
      setInviteError(err.message || "Failed to update role");
      setTimeout(() => setInviteError(null), 4000);
    } finally {
      setUpdatingUserId(null);
    }
  };

  // Handle Classroom Creation
  const handleCreateClassroom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newClassroomName.trim() || !workspace) return;
    try {
      await api.createClassroom(
        workspace.slug,
        newClassroomName,
        isOwner && selectedTeacherId ? selectedTeacherId : undefined
      );
      const updated = await api.listClassrooms(workspace.slug);
      setClassrooms(updated);
      setNewClassroomName("");
      setSelectedTeacherId("");
      setClassroomSuccess(true);
      setTimeout(() => setClassroomSuccess(false), 3000);
    } catch (err: any) {
      console.error(err);
    }
  };

  // Handle Single Student Invitation (Owner or Teacher feature)
  const handleInviteSingleStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!singleStudentEmail.trim() || !workspace) return;
    setSingleStudentLoading(true);
    setInviteSuccess(null);
    setInviteError(null);
    try {
      await api.inviteWorkspaceStudent(workspace.slug, singleStudentEmail.trim());
      setInviteSuccess(`Invitation dispatched to student: ${singleStudentEmail}. Student can set password and join workspace!`);
      setSingleStudentEmail("");
      loadWorkspaceData(workspace.slug);
      setTimeout(() => setInviteSuccess(null), 5000);
    } catch (err: any) {
      setInviteError(err.message || "Failed to invite student");
      setTimeout(() => setInviteError(null), 4000);
    } finally {
      setSingleStudentLoading(false);
    }
  };

  const isOwner = userRole.toUpperCase() === "OWNER";
  const isTeacher = userRole.toUpperCase() === "TEACHER";

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 p-3 sm:p-5 md:p-6 bg-black/90 backdrop-blur-md overflow-y-auto flex items-center justify-center"
        >
          {/* Main Card with Background Video matching Landing Page */}
          <motion.div
            initial={{ scale: 0.96, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.96, y: 20 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="relative w-full max-w-7xl min-h-[85vh] md:min-h-[90vh] rounded-2xl md:rounded-[2rem] overflow-hidden bg-black border border-white/[0.12] shadow-2xl flex flex-col justify-between"
          >
            {/* Background Video */}
            <CinematicVideo
              src={VIDEO_URL}
              className="absolute inset-0 w-full h-full object-cover"
            />

            <div className="noise-overlay absolute inset-0 opacity-[0.7] mix-blend-overlay pointer-events-none" />
            <div className="absolute inset-0 bg-gradient-to-b from-black/85 via-black/75 to-black/95 pointer-events-none" />

            {/* Header Bar */}
            <header className="relative z-20 p-5 sm:p-8 border-b border-white/[0.08] flex flex-wrap items-center justify-between gap-4 bg-black/40 backdrop-blur-md">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/30 flex items-center justify-center text-primary">
                  <Building2 className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs uppercase tracking-widest text-primary/60 font-mono">
                      Workspace Cockpit
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border text-[10px] font-mono font-semibold ${
                        isOwner
                          ? "bg-primary/15 border-primary/30 text-primary"
                          : userRole.toUpperCase() === "STUDENT"
                          ? "bg-blue-500/15 border-blue-500/30 text-blue-300"
                          : "bg-emerald-500/15 border-emerald-500/30 text-emerald-300"
                      }`}
                    >
                      <ShieldCheck className="w-3 h-3" />
                      {userRole.toUpperCase()} // {isOwner ? "HEAD" : userRole.toUpperCase() === "STUDENT" ? "STUDENT" : "FACULTY"}
                    </span>
                  </div>
                  <h3 className="text-lg sm:text-xl font-medium mt-0.5" style={{ color: "#E1E0CC" }}>
                    {isSelectingWorkspace
                      ? "Academic Workspace Directory"
                      : workspace
                      ? workspace.name
                      : "Initialize Workspace"}
                  </h3>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {allWorkspaces.length > 1 && !isSelectingWorkspace && (
                  <button
                    type="button"
                    onClick={handleOpenWorkspaceSelector}
                    className="px-3.5 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-primary/80 hover:text-primary text-xs font-mono transition-colors flex items-center gap-1.5 cursor-pointer"
                  >
                    <Layers className="w-3.5 h-3.5" />
                    <span>Switch Workspace ({allWorkspaces.length})</span>
                  </button>
                )}

                {isOwner && (
                  <button
                    type="button"
                    onClick={() => {
                      setIsSelectingWorkspace(false);
                      setIsCreatingNew(!isCreatingNew);
                    }}
                    className="px-3.5 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-primary/80 hover:text-primary text-xs font-mono transition-colors flex items-center gap-1.5 cursor-pointer"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    {isCreatingNew ? "View Active Workspace" : "New Workspace"}
                  </button>
                )}

                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-1.5 rounded-full bg-white/10 hover:bg-white/20 text-[#E1E0CC] font-medium text-xs flex items-center gap-1.5 transition-all cursor-pointer border border-white/10"
                >
                  <span>Return to Landing</span>
                  <X className="w-3.5 h-3.5" />
                </button>

                {onSignOut && (
                  <button
                    type="button"
                    onClick={onSignOut}
                    className="px-3.5 py-1.5 rounded-full bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 text-xs font-mono transition-colors flex items-center gap-1.5 cursor-pointer"
                    title="Sign out of current account"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                )}
              </div>
            </header>

            {/* Main Content Body */}
            <div className="relative z-20 p-5 sm:p-8 md:p-10 flex-1 flex flex-col justify-center">
              {loadingWorkspace ? (
                <div className="max-w-md mx-auto text-center py-24">
                  <div className="w-10 h-10 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                  <p className="text-sm font-mono text-primary/80">Connecting to Workspace Cockpit…</p>
                </div>
              ) : isSelectingWorkspace && allWorkspaces.length > 1 ? (
                <div className="max-w-4xl mx-auto w-full py-6">
                  {/* Selector Header */}
                  <div className="text-center mb-8">
                    <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full border border-primary/20 bg-primary/5 text-primary text-xs tracking-widest uppercase font-mono mb-3">
                      <Layers className="w-3.5 h-3.5" />
                      Academic Multi-Workspace Directory
                    </div>
                    <h3 className="text-2xl sm:text-3xl font-light text-[#E1E0CC]">
                      Select Workspace Cockpit
                    </h3>
                    <p className="text-xs sm:text-sm text-primary/70 font-light mt-1.5 max-w-lg mx-auto">
                      Your identity has access to {allWorkspaces.length} academic workspaces. Select one to enter its cockpit and manage classrooms, faculty, and submissions.
                    </p>
                  </div>

                  {/* Workspace Cards Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 mb-8">
                    {allWorkspaces.map((ws) => {
                      const isWsOwner = ws.role?.toUpperCase() === "OWNER";
                      const isWsTeacher = ws.role?.toUpperCase() === "TEACHER";
                      return (
                        <motion.div
                          key={ws.id}
                          whileHover={{ y: -3, transition: { duration: 0.2 } }}
                          onClick={() => handleSelectWorkspace(ws)}
                          className="group relative bg-[#121212]/90 hover:bg-[#181818] border border-white/10 hover:border-primary/50 rounded-2xl p-6 transition-all duration-300 shadow-xl cursor-pointer flex flex-col justify-between"
                        >
                          <div>
                            <div className="flex items-start justify-between gap-3 mb-4">
                              <div className="w-12 h-12 rounded-xl bg-primary/10 border border-primary/25 flex items-center justify-center text-primary group-hover:scale-105 transition-transform">
                                <Building2 className="w-6 h-6" />
                              </div>
                              <span
                                className={`px-2.5 py-1 rounded-full border text-[10px] font-mono font-semibold tracking-wider uppercase ${
                                  isWsOwner
                                    ? "bg-primary/15 border-primary/30 text-primary"
                                    : isWsTeacher
                                    ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-300"
                                    : "bg-blue-500/15 border-blue-500/30 text-blue-300"
                                }`}
                              >
                                {isWsOwner ? "HEAD / OWNER" : isWsTeacher ? "FACULTY TEACHER" : "STUDENT SCHOLAR"}
                              </span>
                            </div>

                            <h4 className="text-lg font-medium text-[#E1E0CC] group-hover:text-primary transition-colors">
                              {ws.name}
                            </h4>
                            <p className="text-xs font-mono text-gray-500 mt-1 mb-3">
                              ID: {ws.slug}
                            </p>
                            <p className="text-xs text-primary/70 line-clamp-2 leading-relaxed font-light mb-6">
                              {ws.description || "Academic institution space for classrooms, curriculum, assignments, and cognitive student telemetry."}
                            </p>
                          </div>

                          <div className="pt-4 border-t border-white/[0.08] flex items-center justify-between">
                            <span className="text-[11px] font-mono text-primary/60 group-hover:text-primary transition-colors flex items-center gap-1">
                              Launch Cockpit
                            </span>
                            <div className="w-8 h-8 rounded-full bg-white/5 group-hover:bg-primary group-hover:text-black text-[#E1E0CC] flex items-center justify-center transition-all">
                              <ChevronRight className="w-4 h-4" />
                            </div>
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>

                  {/* Optional New Workspace Button for Owner */}
                  {isOwner && (
                    <div className="text-center pt-2">
                      <button
                        type="button"
                        onClick={() => {
                          setIsSelectingWorkspace(false);
                          setIsCreatingNew(true);
                        }}
                        className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-primary/80 hover:text-primary text-xs font-mono transition-colors inline-flex items-center gap-2 cursor-pointer"
                      >
                        <Plus className="w-4 h-4" />
                        <span>Provision Another Academic Workspace</span>
                      </button>
                    </div>
                  )}
                </div>
              ) : isOwner && (isCreatingNew || !workspace) ? (
                <div className="max-w-xl mx-auto w-full bg-black/60 backdrop-blur-xl border border-primary/25 rounded-2xl p-6 sm:p-8 shadow-2xl">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/20 bg-primary/5 text-primary text-xs tracking-widest uppercase font-mono mb-4">
                    <Sparkles className="w-3.5 h-3.5" />
                    First Identity Established
                  </div>

                  <h4 className="text-2xl font-normal text-[#E1E0CC] mb-2">
                    Create Academic Workspace
                  </h4>
                  <p className="text-xs sm:text-sm text-primary/70 mb-6 font-light">
                    As the creator, your identity will be designated as the{" "}
                    <strong className="text-primary font-medium">Head of Workspace (Owner)</strong> with exclusive authorization to invite faculty teachers.
                  </p>

                  <form onSubmit={handleCreateWorkspace} className="space-y-4">
                    <div>
                      <label className="block text-xs font-mono uppercase tracking-wider text-primary/80 mb-1.5">
                        Workspace Name
                      </label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. Department of AI & Computational Science"
                        value={newWsName}
                        onChange={(e) => setNewWsName(e.target.value)}
                        className="w-full bg-[#181818] border border-white/10 rounded-xl py-2.5 px-4 text-xs sm:text-sm text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-mono uppercase tracking-wider text-primary/80 mb-1.5">
                        Description / Scope
                      </label>
                      <textarea
                        rows={3}
                        placeholder="e.g. Unified faculty curricula, assignment pipelines, and student cognitive telemetry..."
                        value={newWsDesc}
                        onChange={(e) => setNewWsDesc(e.target.value)}
                        className="w-full bg-[#181818] border border-white/10 rounded-xl py-2.5 px-4 text-xs sm:text-sm text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60 resize-none"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={wsLoading}
                      className="w-full bg-primary text-black font-medium py-3 rounded-xl text-xs sm:text-sm flex items-center justify-center gap-2 hover:brightness-105 active:scale-[0.99] transition-all cursor-pointer shadow-lg disabled:opacity-50"
                    >
                      <span>
                        {wsLoading ? "Provisioning..." : "Provision Workspace & Become Head"}
                      </span>
                      <Building2 className="w-4 h-4" />
                    </button>
                  </form>
                </div>
              ) : !workspace ? (
                <div className="max-w-md mx-auto text-center py-16 p-8 bg-black/60 border border-white/10 rounded-2xl shadow-xl">
                  <div className="w-10 h-10 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                  <p className="text-sm font-mono text-gray-300 mb-3">Syncing workspace telemetry…</p>
                  <button
                    type="button"
                    onClick={() => loadWorkspaceData()}
                    className="px-4 py-2 rounded-xl bg-primary text-black text-xs font-semibold hover:brightness-105 transition-all cursor-pointer"
                  >
                    Reload Cockpit
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-8 items-start">
                  {/* Left Column (5 cols): Workspace Metadata & Classrooms */}
                  <div className="lg:col-span-5 space-y-6">
                    <div className="bg-black/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl">
                      <div className="text-xs font-mono uppercase tracking-wider text-primary/60 mb-1">
                        Active Authenticated User
                      </div>
                      <div className="text-sm font-medium text-[#E1E0CC] flex items-center justify-between">
                        <span>{currentUserEmail}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-primary/10 border border-primary/20 text-primary">
                          {userRole}
                        </span>
                      </div>
                      <div className="mt-4 pt-4 border-t border-white/[0.08] flex items-center justify-between text-xs">
                        <span className="text-gray-400 font-mono">Workspace Slug:</span>
                        <code className="text-primary font-mono bg-white/5 px-2 py-0.5 rounded border border-white/10">
                          /{workspace.slug}
                        </code>
                      </div>
                    </div>

                    {/* Classrooms Manager */}
                    <div className="bg-black/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2 text-sm font-medium text-primary">
                          <School className="w-4 h-4" />
                          <span>Classrooms ({classrooms.length})</span>
                        </div>
                        <span className="text-[11px] font-mono text-gray-400">
                          Curricula Pipeline
                        </span>
                      </div>

                      {userRole.toUpperCase() !== "STUDENT" && (
                        <form onSubmit={handleCreateClassroom} className="space-y-2 mb-4">
                          <div className="flex gap-2">
                            <input
                              type="text"
                              required
                              placeholder="New Classroom Name..."
                              value={newClassroomName}
                              onChange={(e) => setNewClassroomName(e.target.value)}
                              className="flex-1 bg-[#181818] border border-white/10 rounded-xl py-2 px-3 text-xs text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60"
                            />
                            <button
                              type="submit"
                              className="px-3 py-2 bg-primary text-black rounded-xl text-xs font-medium hover:brightness-105 transition-all cursor-pointer whitespace-nowrap"
                            >
                              Add
                            </button>
                          </div>
                          {isOwner && (
                            <div className="flex flex-col gap-1">
                              <label className="text-[10px] text-gray-400 font-mono">
                                Assign To Faculty Teacher:
                              </label>
                              <select
                                value={selectedTeacherId}
                                onChange={(e) => setSelectedTeacherId(e.target.value)}
                                className="w-full bg-[#181818] border border-white/10 rounded-xl py-1.5 px-3 text-xs text-[#E1E0CC] focus:outline-none focus:border-primary/60 cursor-pointer"
                              >
                                <option value="">-- Workspace Admin (Self) --</option>
                                {teacherMembers.map((t) => (
                                  <option key={t.user_id} value={t.user_id}>
                                    {t.email || t.user_id}
                                  </option>
                                ))}
                              </select>
                            </div>
                          )}
                        </form>
                      )}

                      {classroomSuccess && (
                        <div className="text-[11px] text-emerald-400 font-mono mb-2">
                          ✓ Classroom created in workspace
                        </div>
                      )}

                      <div className="space-y-2">
                        {classrooms.length === 0 ? (
                          <div className="p-3 text-center text-xs text-gray-500 font-mono">
                            No classrooms yet.
                          </div>
                        ) : (
                          classrooms.map((c, i) => (
                            <div
                              key={c.id || i}
                              className="flex items-center justify-between p-2.5 rounded-xl bg-[#141414] border border-white/5 text-xs text-gray-300 hover:border-primary/30 transition-colors"
                            >
                              <div className="flex flex-col truncate pr-2">
                                <span className="flex items-center gap-2 truncate font-medium text-gray-200">
                                  <GraduationCap className="w-3.5 h-3.5 text-primary flex-shrink-0" />
                                  <span className="truncate">{c.name}</span>
                                </span>
                                {c.assigned_teacher_email ? (
                                  <span className="text-[10px] text-emerald-400/90 font-mono pl-5.5 truncate">
                                    Teacher: {c.assigned_teacher_email}
                                  </span>
                                ) : (
                                  <span className="text-[10px] text-gray-500 font-mono pl-5.5 truncate">
                                    Admin Curricula
                                  </span>
                                )}
                              </div>
                              <button
                                type="button"
                                onClick={() => handleOpenClassroom(c)}
                                className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 text-[11px] font-mono transition-colors cursor-pointer flex-shrink-0"
                              >
                                <span>Open</span>
                                <ChevronRight className="w-3 h-3" />
                              </button>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right Column (7 cols): Faculty Teachers, Batch Student Admissions, or Student Directory */}
                  <div className="lg:col-span-7 bg-black/60 backdrop-blur-xl border border-primary/30 rounded-2xl p-6 sm:p-8 shadow-2xl flex flex-col justify-between">
                    <div>
                      {/* Top Header / Tab Switcher */}
                      {isOwner ? (
                        <div className="flex flex-wrap items-center justify-between gap-3 mb-6 border-b border-white/[0.08] pb-4">
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => setOwnerTab("teachers")}
                              className={`px-3.5 py-1.5 rounded-full text-xs font-mono transition-colors flex items-center gap-2 cursor-pointer ${
                                ownerTab === "teachers"
                                  ? "bg-primary text-black font-semibold shadow-md"
                                  : "bg-white/5 text-primary/70 hover:bg-white/10"
                              }`}
                            >
                              <UserPlus className="w-3.5 h-3.5" />
                              <span>Faculty Teachers</span>
                            </button>

                            <button
                              type="button"
                              onClick={() => setOwnerTab("students")}
                              className={`px-3.5 py-1.5 rounded-full text-xs font-mono transition-colors flex items-center gap-2 cursor-pointer ${
                                ownerTab === "students"
                                  ? "bg-primary text-black font-semibold shadow-md"
                                  : "bg-white/5 text-primary/70 hover:bg-white/10"
                              }`}
                            >
                              <FileSpreadsheet className="w-3.5 h-3.5" />
                              <span>Student Admissions</span>
                            </button>
                          </div>

                          <span className="text-[11px] font-mono uppercase tracking-wider px-2.5 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary">
                            Head of Workspace
                          </span>
                        </div>
                      ) : isTeacher ? (
                        <div className="flex flex-wrap items-center justify-between gap-3 mb-6 border-b border-white/[0.08] pb-4">
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => setTeacherTab("students")}
                              className={`px-3.5 py-1.5 rounded-full text-xs font-mono transition-colors flex items-center gap-2 cursor-pointer ${
                                teacherTab === "students"
                                  ? "bg-primary text-black font-semibold shadow-md"
                                  : "bg-white/5 text-primary/70 hover:bg-white/10"
                              }`}
                            >
                              <FileSpreadsheet className="w-3.5 h-3.5" />
                              <span>Student Admissions</span>
                            </button>

                            <button
                              type="button"
                              onClick={() => setTeacherTab("roster")}
                              className={`px-3.5 py-1.5 rounded-full text-xs font-mono transition-colors flex items-center gap-2 cursor-pointer ${
                                teacherTab === "roster"
                                  ? "bg-primary text-black font-semibold shadow-md"
                                  : "bg-white/5 text-primary/70 hover:bg-white/10"
                              }`}
                            >
                              <UserCheck className="w-3.5 h-3.5" />
                              <span>Workspace Directory</span>
                            </button>
                          </div>

                          <span className="text-[11px] font-mono uppercase tracking-wider px-2.5 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300">
                            Faculty Teacher
                          </span>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between mb-6 border-b border-white/[0.08] pb-4">
                          <div className="flex items-center gap-2">
                            <UserCheck className="w-5 h-5 text-primary" />
                            <div>
                              <h4 className="text-xl font-medium text-[#E1E0CC]">
                                Workspace Members Directory
                              </h4>
                              <p className="text-xs text-primary/70 font-light mt-0.5">
                                Explore workspace members across administrative heads, faculty instructors, and admitted students.
                              </p>
                            </div>
                          </div>
                          <span className="text-[11px] font-mono uppercase tracking-wider px-2.5 py-1 rounded-full border bg-blue-500/15 border-blue-500/30 text-blue-300">
                            Student Seat
                          </span>
                        </div>
                      )}

                      {/* Feedback Toasts */}
                      {inviteSuccess && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="mb-4 p-3 rounded-xl bg-primary/10 border border-primary/30 flex items-center gap-2 text-primary text-xs font-mono"
                        >
                          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                          <span>{inviteSuccess}</span>
                        </motion.div>
                      )}

                      {inviteError && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="mb-4 p-3 rounded-xl bg-red-950/40 border border-red-500/30 flex items-center gap-2 text-red-200 text-xs font-mono"
                        >
                          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                          <span>{inviteError}</span>
                        </motion.div>
                      )}

                      {batchResult && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="mb-4 p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center gap-2 text-emerald-300 text-xs font-mono"
                        >
                          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                          <span>{batchResult.message}</span>
                        </motion.div>
                      )}

                      {batchError && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="mb-4 p-3 rounded-xl bg-red-950/40 border border-red-500/30 flex items-center gap-2 text-red-200 text-xs font-mono"
                        >
                          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                          <span>{batchError}</span>
                        </motion.div>
                      )}

                      {/* ─── OWNER TAB 1: TEACHERS & ROSTER ─── */}
                      {isOwner && ownerTab === "teachers" && (
                        <div>
                          <p className="text-xs text-primary/70 mb-5 font-light leading-relaxed">
                            Invite faculty professors and instructors. They receive a styled email invitation, set their password, and enter the workspace as teachers.
                          </p>

                          <form onSubmit={handleInviteTeacher} className="space-y-4 mb-6">
                            <div className="grid grid-cols-1 sm:grid-cols-12 gap-3">
                              <div className="sm:col-span-8 relative">
                                <Mail className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                                <input
                                  type="email"
                                  required
                                  placeholder="professor.smith@university.edu"
                                  value={teacherEmail}
                                  onChange={(e) => setTeacherEmail(e.target.value)}
                                  className="w-full bg-[#181818] border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-xs sm:text-sm text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60"
                                />
                              </div>

                              <div className="sm:col-span-4">
                                <button
                                  type="submit"
                                  disabled={inviteLoading}
                                  className="w-full h-full bg-primary text-black font-medium py-2.5 px-4 rounded-xl text-xs sm:text-sm flex items-center justify-center gap-2 hover:brightness-105 active:scale-[0.99] transition-all cursor-pointer disabled:opacity-50"
                                >
                                  <span>{inviteLoading ? "Sending..." : "Invite Teacher"}</span>
                                  <Send className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            </div>
                          </form>

                          {/* Members Roster & Role Management */}
                          <div>
                            <div className="text-xs uppercase tracking-wider text-primary/70 font-mono mb-3 flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <Users className="w-3.5 h-3.5" />
                                <span>Workspace Roster ({effectiveMembers.length})</span>
                              </div>
                              <span className="text-[10px] text-gray-500 font-mono">
                                Admin can modify permissions
                              </span>
                            </div>

                            {/* 3 Different Filter Buttons: Admin, Teacher, Student (+ All) */}
                            <div className="flex flex-wrap items-center gap-1.5 p-1 bg-black/60 border border-white/10 rounded-xl mb-3">
                              <button
                                type="button"
                                onClick={() => setMemberRoleFilter("ALL")}
                                className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all flex items-center gap-1.5 cursor-pointer ${
                                  memberRoleFilter === "ALL"
                                    ? "bg-white/15 text-[#E1E0CC] font-semibold border border-white/20"
                                    : "text-gray-400 hover:text-white hover:bg-white/5"
                                }`}
                              >
                                <span>All</span>
                                <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-white/10 font-mono">
                                  {effectiveMembers.length}
                                </span>
                              </button>

                              <button
                                type="button"
                                onClick={() => setMemberRoleFilter("ADMIN")}
                                className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all flex items-center gap-1.5 cursor-pointer ${
                                  memberRoleFilter === "ADMIN"
                                    ? "bg-primary text-black font-semibold shadow-md"
                                    : "text-primary/70 hover:text-primary hover:bg-primary/5"
                                }`}
                              >
                                <ShieldCheck className="w-3.5 h-3.5" />
                                <span>Admin</span>
                                <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                                  memberRoleFilter === "ADMIN" ? "bg-black/20 text-black" : "bg-primary/10 text-primary"
                                }`}>
                                  {adminMembers.length}
                                </span>
                              </button>

                              <button
                                type="button"
                                onClick={() => setMemberRoleFilter("TEACHER")}
                                className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all flex items-center gap-1.5 cursor-pointer ${
                                  memberRoleFilter === "TEACHER"
                                    ? "bg-emerald-500 text-black font-semibold shadow-md"
                                    : "text-emerald-400/80 hover:text-emerald-300 hover:bg-emerald-500/10"
                                }`}
                              >
                                <GraduationCap className="w-3.5 h-3.5" />
                                <span>Teacher</span>
                                <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                                  memberRoleFilter === "TEACHER" ? "bg-black/20 text-black" : "bg-emerald-500/20 text-emerald-300"
                                }`}>
                                  {teacherMembers.length}
                                </span>
                              </button>

                              <button
                                type="button"
                                onClick={() => setMemberRoleFilter("STUDENT")}
                                className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all flex items-center gap-1.5 cursor-pointer ${
                                  memberRoleFilter === "STUDENT"
                                    ? "bg-blue-500 text-black font-semibold shadow-md"
                                    : "text-blue-400/80 hover:text-blue-300 hover:bg-blue-500/10"
                                }`}
                              >
                                <Users className="w-3.5 h-3.5" />
                                <span>Student</span>
                                <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                                  memberRoleFilter === "STUDENT" ? "bg-black/20 text-black" : "bg-blue-500/20 text-blue-300"
                                }`}>
                                  {studentMembers.length}
                                </span>
                              </button>
                            </div>

                            <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
                              {displayedMembers.length === 0 ? (
                                <div className="p-4 rounded-xl bg-[#141414] border border-white/[0.06] text-center text-xs text-gray-500 font-mono">
                                  No {memberRoleFilter === "ALL" ? "" : memberRoleFilter.toLowerCase()} members registered yet.
                                </div>
                              ) : (
                                displayedMembers.map((member) => (
                                  <div
                                    key={member.membership_id}
                                    className="flex items-center justify-between p-3 rounded-xl bg-[#141414] border border-white/[0.06] hover:border-primary/30 transition-colors gap-3"
                                  >
                                    <div className="flex items-center gap-3 min-w-0">
                                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-mono font-bold flex-shrink-0 border ${
                                        member.role === "OWNER"
                                          ? "bg-primary/10 border-primary/20 text-primary"
                                          : member.role === "TEACHER"
                                          ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                                          : "bg-blue-500/10 border-blue-500/20 text-blue-300"
                                      }`}>
                                        {member.email.charAt(0).toUpperCase()}
                                      </div>
                                      <div className="min-w-0">
                                        <div className="text-xs font-medium text-[#E1E0CC] truncate">
                                          {member.email}
                                        </div>
                                        <div className="text-[10px] text-gray-500 font-mono">
                                          Status: {member.status}
                                        </div>
                                      </div>
                                    </div>

                                    <div className="flex items-center gap-2 flex-shrink-0">
                                      {isOwner && member.role !== "OWNER" ? (
                                        <select
                                          value={member.role}
                                          disabled={updatingUserId === member.user_id}
                                          onChange={(e) => handleRoleChange(member.user_id, e.target.value)}
                                          className="bg-black/60 text-[#E1E0CC] border border-primary/30 rounded-lg text-[11px] font-mono px-2 py-1 focus:outline-none focus:border-primary cursor-pointer"
                                        >
                                          <option value="TEACHER">TEACHER</option>
                                          <option value="STUDENT">STUDENT</option>
                                        </select>
                                      ) : (
                                        <span
                                          className={`text-[10px] font-mono px-2.5 py-0.5 rounded-full border ${
                                            member.role === "OWNER"
                                              ? "bg-primary/20 border-primary/40 text-primary"
                                              : member.role === "TEACHER"
                                              ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-400"
                                              : "bg-blue-500/15 border-blue-500/30 text-blue-300"
                                          }`}
                                        >
                                          {member.role}
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                ))
                              )}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* ─── STUDENT ADMISSIONS (OWNER OR TEACHER) ─── */}
                      {((isOwner && ownerTab === "students") || (isTeacher && teacherTab === "students")) && (
                        <div>
                          <p className="text-xs text-primary/70 mb-4 font-light leading-relaxed">
                            {isOwner
                              ? "As Head of Workspace, invite students individually or upload a batch roster. Students will receive immediate workspace credentials via email."
                              : "As a Faculty Teacher, you can invite students to join this academic workspace. Students will receive an invitation email to set their password and enter the workspace."}
                          </p>

                          {/* Quick Single Student Invite */}
                          <div className="mb-5 p-4 rounded-xl bg-white/[0.03] border border-white/10">
                            <div className="text-xs uppercase tracking-wider text-primary/80 font-mono mb-2.5 flex items-center gap-2">
                              <Mail className="w-3.5 h-3.5 text-primary" />
                              <span>Quick Student Invitation</span>
                            </div>
                            <form onSubmit={handleInviteSingleStudent} className="flex flex-col sm:flex-row gap-2">
                              <div className="relative flex-1">
                                <Mail className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                                <input
                                  type="email"
                                  required
                                  placeholder="student.21cs@university.edu"
                                  value={singleStudentEmail}
                                  onChange={(e) => setSingleStudentEmail(e.target.value)}
                                  className="w-full bg-[#181818] border border-white/10 rounded-xl py-2 pl-10 pr-3 text-xs text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60"
                                />
                              </div>
                              <button
                                type="submit"
                                disabled={singleStudentLoading}
                                className="px-4 py-2 bg-primary text-black font-semibold rounded-xl text-xs flex items-center justify-center gap-1.5 hover:brightness-105 transition-all cursor-pointer disabled:opacity-50 whitespace-nowrap"
                              >
                                <span>{singleStudentLoading ? "Inviting..." : "Invite Student"}</span>
                                <Send className="w-3 h-3" />
                              </button>
                            </form>
                          </div>

                          <div className="flex items-center gap-3 my-4">
                            <div className="h-[1px] flex-1 bg-white/10" />
                            <span className="text-[10px] uppercase tracking-widest text-gray-500 font-mono">
                              or batch admission
                            </span>
                            <div className="h-[1px] flex-1 bg-white/10" />
                          </div>

                          {/* File Uploader */}
                          <div className="mb-4">
                            <input
                              ref={fileInputRef}
                              type="file"
                              accept=".csv,.txt"
                              style={{ display: "none" }}
                              onChange={handleFileUpload}
                            />
                            <button
                              type="button"
                              onClick={() => fileInputRef.current?.click()}
                              className="w-full p-3.5 rounded-xl border border-dashed border-primary/30 hover:border-primary/60 bg-primary/5 hover:bg-primary/10 transition-colors flex items-center justify-center gap-3 cursor-pointer text-xs font-mono text-primary"
                            >
                              <UploadCloud className="w-5 h-5 text-primary" />
                              <span>Upload Student Emails (.csv or .txt)</span>
                            </button>
                          </div>

                          {/* Textarea for direct pasting */}
                          <div className="mb-4">
                            <label className="block text-[11px] font-mono uppercase tracking-wider text-primary/80 mb-1.5 flex items-center justify-between">
                              <span>Batch Email Roster</span>
                              <span className="text-gray-500">
                                {
                                  batchEmails
                                    .split(/[\n,;]+/)
                                    .map((e) => e.trim())
                                    .filter((e) => e && e.includes("@")).length
                                }{" "}
                                detected
                              </span>
                            </label>
                            <textarea
                              rows={4}
                              value={batchEmails}
                              onChange={(e) => setBatchEmails(e.target.value)}
                              placeholder="alex.21cs@university.edu&#10;maya.21cs@university.edu&#10;karan.21cs@university.edu"
                              className="w-full bg-[#181818] border border-white/10 rounded-xl p-3 text-xs font-mono text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60 resize-none"
                            />
                          </div>

                          {/* Dispatch Button */}
                          <button
                            type="button"
                            onClick={handleBatchInvite}
                            disabled={batchLoading}
                            className="w-full bg-primary text-black font-semibold py-3 rounded-xl text-xs sm:text-sm flex items-center justify-center gap-2 hover:brightness-105 active:scale-[0.99] transition-all cursor-pointer disabled:opacity-50 shadow-lg"
                          >
                            <Send className="w-4 h-4" />
                            <span>
                              {batchLoading
                                ? "Queuing & Dispatching Emails..."
                                : "DISPATCH BATCH STUDENT INVITATIONS →"}
                            </span>
                          </button>
                        </div>
                      )}

                      {/* ─── MEMBER DIRECTORY VIEW (STUDENTS OR TEACHER ROSTER TAB) ─── */}
                      {((isTeacher && teacherTab === "roster") || (!isOwner && !isTeacher)) && (
                        <div>
                          <div className="text-xs uppercase tracking-wider text-primary/70 font-mono mb-3 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Users className="w-3.5 h-3.5" />
                              <span>Workspace Directory ({effectiveMembers.length})</span>
                            </div>
                            <span className="text-[10px] text-gray-500 font-mono">
                              Open Academic Community
                            </span>
                          </div>

                          {/* 3 Different Filter Buttons: Admin, Teacher, Student (+ All) */}
                          <div className="flex flex-wrap items-center gap-1.5 p-1 bg-black/60 border border-white/10 rounded-xl mb-3">
                            <button
                              type="button"
                              onClick={() => setMemberRoleFilter("ALL")}
                              className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all flex items-center gap-1.5 cursor-pointer ${
                                memberRoleFilter === "ALL"
                                  ? "bg-white/15 text-[#E1E0CC] font-semibold border border-white/20"
                                  : "text-gray-400 hover:text-white hover:bg-white/5"
                              }`}
                            >
                              <span>All</span>
                              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-white/10 font-mono">
                                {effectiveMembers.length}
                              </span>
                            </button>

                            <button
                              type="button"
                              onClick={() => setMemberRoleFilter("ADMIN")}
                              className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all flex items-center gap-1.5 cursor-pointer ${
                                memberRoleFilter === "ADMIN"
                                  ? "bg-primary text-black font-semibold shadow-md"
                                  : "text-primary/70 hover:text-primary hover:bg-primary/5"
                              }`}
                            >
                              <ShieldCheck className="w-3.5 h-3.5" />
                              <span>Admin</span>
                              <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                                memberRoleFilter === "ADMIN" ? "bg-black/20 text-black" : "bg-primary/10 text-primary"
                              }`}>
                                {adminMembers.length}
                              </span>
                            </button>

                            <button
                              type="button"
                              onClick={() => setMemberRoleFilter("TEACHER")}
                              className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all flex items-center gap-1.5 cursor-pointer ${
                                memberRoleFilter === "TEACHER"
                                  ? "bg-emerald-500 text-black font-semibold shadow-md"
                                  : "text-emerald-400/80 hover:text-emerald-300 hover:bg-emerald-500/10"
                              }`}
                            >
                              <GraduationCap className="w-3.5 h-3.5" />
                              <span>Teacher</span>
                              <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                                memberRoleFilter === "TEACHER" ? "bg-black/20 text-black" : "bg-emerald-500/20 text-emerald-300"
                              }`}>
                                {teacherMembers.length}
                              </span>
                            </button>

                            <button
                              type="button"
                              onClick={() => setMemberRoleFilter("STUDENT")}
                              className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all flex items-center gap-1.5 cursor-pointer ${
                                memberRoleFilter === "STUDENT"
                                  ? "bg-blue-500 text-black font-semibold shadow-md"
                                  : "text-blue-400/80 hover:text-blue-300 hover:bg-blue-500/10"
                              }`}
                            >
                              <Users className="w-3.5 h-3.5" />
                              <span>Student</span>
                              <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                                memberRoleFilter === "STUDENT" ? "bg-black/20 text-black" : "bg-blue-500/20 text-blue-300"
                              }`}>
                                {studentMembers.length}
                              </span>
                            </button>
                          </div>

                          <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
                            {displayedMembers.length === 0 ? (
                              <div className="p-5 rounded-xl bg-[#141414] border border-white/[0.06] text-center text-xs text-gray-500 font-mono">
                                No {memberRoleFilter === "ALL" ? "" : memberRoleFilter.toLowerCase()} members listed in this workspace.
                              </div>
                            ) : (
                              displayedMembers.map((t) => (
                                <div
                                  key={t.membership_id}
                                  className="flex items-center justify-between p-3.5 rounded-xl bg-[#141414] border border-white/[0.06] hover:border-primary/30 transition-colors gap-3"
                                >
                                  <div className="flex items-center gap-3 min-w-0">
                                    <div className={`w-9 h-9 rounded-xl flex items-center justify-center text-xs font-mono font-bold flex-shrink-0 border ${
                                      t.role === "OWNER"
                                        ? "bg-primary/10 border-primary/20 text-primary"
                                        : t.role === "TEACHER"
                                        ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                                        : "bg-blue-500/10 border-blue-500/20 text-blue-300"
                                    }`}>
                                      {t.email.charAt(0).toUpperCase()}
                                    </div>
                                    <div className="min-w-0">
                                      <div className="text-xs sm:text-sm font-medium text-[#E1E0CC] truncate">
                                        {t.email}
                                      </div>
                                      <div className="text-[10px] text-gray-500 font-mono">
                                        Joined: {t.joined_at ? new Date(t.joined_at).toLocaleDateString() : "Active"}
                                      </div>
                                    </div>
                                  </div>

                                  <span
                                    className={`text-[10px] font-mono px-3 py-1 rounded-full border ${
                                      t.role === "OWNER"
                                        ? "bg-primary/20 border-primary/40 text-primary"
                                        : t.role === "TEACHER"
                                        ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-300"
                                        : "bg-blue-500/15 border-blue-500/30 text-blue-300"
                                    }`}
                                  >
                                    {t.role === "OWNER" ? "WORKSPACE HEAD" : t.role === "TEACHER" ? "FACULTY INSTRUCTOR" : "STUDENT SCHOLAR"}
                                  </span>
                                </div>
                              ))
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Footer Bar */}
            <footer className="relative z-20 p-4 sm:p-6 border-t border-white/[0.08] flex flex-wrap items-center justify-between gap-4 bg-black/40 backdrop-blur-md text-xs font-mono text-gray-500">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                <span>Gradify Academic Protocol Active</span>
              </div>
              <div className="flex items-center gap-4 text-primary/60">
                <span>FastAPI Engine</span>
                <span>&bull;</span>
                <span>Argon2 Security</span>
                <span>&bull;</span>
                <span>Live Membership Telemetry</span>
              </div>
            </footer>
          </motion.div>
        </motion.div>
      )}
      {activeClassroom && (
        <ClassroomDashboard
          isOpen={!!activeClassroom}
          onClose={handleCloseClassroom}
          classroomId={activeClassroom.id}
          classroomName={activeClassroom.name}
          userRole={userRole}
        />
      )}
    </AnimatePresence>
  );
};
