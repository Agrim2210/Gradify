import { useState, useEffect } from "react";
import { Hero } from "./components/Hero";
import { About } from "./components/About";
import { AuthSection } from "./components/AuthSection";
import { Footer } from "./components/Footer";
import { ContactModal } from "./components/ContactModal";
import { WorkspaceCard } from "./components/WorkspaceCard";
import { EmailVerificationModal } from "./components/EmailVerificationModal";
import { AcceptInvitationModal } from "./components/AcceptInvitationModal";
import { AcceptClassroomInvitationModal } from "./components/AcceptClassroomInvitationModal";
import { CinematicVideo } from "./components/CinematicVideo";
import { api } from "./services/api";

export function App() {
  const [authTab, setAuthTab] = useState<"signup" | "signin">("signup");
  const [contactOpen, setContactOpen] = useState(false);
  const [workspaceOpen, setWorkspaceOpen] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    // If an invitation token or verification token is present, never open workspace card directly
    if (params.get("invite_token") || params.get("classroom_invite_token") || params.get("token")) {
      return false;
    }
    const token = localStorage.getItem("gradify_token");
    const navState = localStorage.getItem("gradify_nav_state");
    if (params.get("classroom") || params.get("workspace")) return true;
    return !!token && navState !== "landing";
  });

  // Email verification modal state
  const [verificationOpen, setVerificationOpen] = useState(false);
  const [verifyEmailAddress, setVerifyEmailAddress] = useState("");
  const [simToken, setSimToken] = useState<string | undefined>(undefined);

  // Teacher Invitation Modal state
  const [acceptInviteOpen, setAcceptInviteOpen] = useState(false);
  const [inviteToken, setInviteToken] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("TEACHER");

  // Student Classroom Invitation Modal state
  const [acceptClassroomInviteOpen, setAcceptClassroomInviteOpen] = useState(false);
  const [classroomInviteToken, setClassroomInviteToken] = useState("");
  const [classroomInviteEmail, setClassroomInviteEmail] = useState("");

  const [userRole, setUserRole] = useState(() => {
    return localStorage.getItem("gradify_user_role") || "OWNER";
  });

  // Active authenticated user
  const [currentUserEmail, setCurrentUserEmail] = useState<string>(() => {
    return localStorage.getItem("gradify_user_email") || "head.scholar@university.edu";
  });

  // Global Video URL
  const VIDEO_URL =
    "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260405_170732_8a9ccda6-5cff-4628-b164-059c500a2b41.mp4";

  // Check URL parameters for email verification link or invitation link
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const verifyToken = params.get("token");
    const inviteTokenParam = params.get("invite_token");
    const classroomInviteTokenParam = params.get("classroom_invite_token");
    const emailParam = params.get("email");
    const roleParam = params.get("role");

    // Case 1: Student Classroom Invitation Link (?classroom_invite_token=...&email=...)
    if (classroomInviteTokenParam) {
      setWorkspaceOpen(false);
      setClassroomInviteToken(classroomInviteTokenParam);
      setClassroomInviteEmail(emailParam || "");
      setAcceptClassroomInviteOpen(true);
      return;
    }

    // Case 2: Workspace Invitation Link (?invite_token=...&email=...&role=...)
    if (inviteTokenParam) {
      setWorkspaceOpen(false);
      setInviteToken(inviteTokenParam);
      setInviteEmail(emailParam || "");
      if (roleParam) {
        setInviteRole(roleParam.toUpperCase());
      }
      setAcceptInviteOpen(true);
      return;
    }

    // Case 3: Direct Email Verification Link (?token=...&email=...)
    if (verifyToken) {
      api
        .verifyEmail(verifyToken)
        .then((res) => {
          const verifiedEmail = res.email || emailParam || "scholar@university.edu";
          setCurrentUserEmail(verifiedEmail);
          localStorage.setItem("gradify_user_email", verifiedEmail);
          localStorage.setItem("gradify_nav_state", "workspace");
          window.history.replaceState({}, document.title, window.location.pathname);
          setVerificationOpen(false);
          setWorkspaceOpen(true);
        })
        .catch((err) => {
          console.error("Verification error:", err);
        });
      return;
    }

    // Case 4: Verify active session for logged-in user on refresh
    const token = localStorage.getItem("gradify_token");
    if (token) {
      api
        .getMyWorkspace()
        .then((myWs) => {
          if (myWs) {
            if (myWs.role) {
              setUserRole(myWs.role);
              localStorage.setItem("gradify_user_role", myWs.role);
            }
          } else {
            // Token is invalid/expired
            localStorage.removeItem("gradify_token");
            localStorage.removeItem("gradify_active_classroom");
            localStorage.setItem("gradify_nav_state", "landing");
            setWorkspaceOpen(false);
          }
        })
        .catch(() => {
          // ignore transient network glitch
        });
    }
  }, []);

  const handleOpenWorkspace = () => {
    localStorage.setItem("gradify_nav_state", "workspace");
    const url = new URL(window.location.href);
    url.searchParams.set("workspace", "true");
    window.history.replaceState({}, document.title, url.toString());
    setWorkspaceOpen(true);
  };

  const handleCloseWorkspace = () => {
    localStorage.setItem("gradify_nav_state", "landing");
    localStorage.removeItem("gradify_active_classroom");
    localStorage.removeItem("gradify_active_workspace_slug");
    const url = new URL(window.location.href);
    url.searchParams.delete("classroom");
    url.searchParams.delete("workspace");
    window.history.replaceState({}, document.title, url.toString());
    setWorkspaceOpen(false);
  };

  const handleSignOut = () => {
    localStorage.removeItem("gradify_token");
    localStorage.removeItem("gradify_user_email");
    localStorage.removeItem("gradify_user_role");
    localStorage.removeItem("gradify_active_classroom");
    localStorage.removeItem("gradify_active_workspace_slug");
    localStorage.setItem("gradify_nav_state", "landing");
    const url = new URL(window.location.href);
    url.searchParams.delete("classroom");
    url.searchParams.delete("workspace");
    window.history.replaceState({}, document.title, url.toString());
    setWorkspaceOpen(false);
  };

  const handleSelectAuthTab = (tab: "signup" | "signin") => {
    setAuthTab(tab);
    const el = document.getElementById("auth-section");
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleJoinLab = () => {
    setAuthTab("signup");
    const el = document.getElementById("auth-section");
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  // Called when signup initiates email verification
  const handleOpenVerificationModal = (email: string, token?: string) => {
    setVerifyEmailAddress(email);
    setSimToken(token);
    setVerificationOpen(true);
  };

  // Called when verification succeeds
  const handleVerificationSuccess = (email: string) => {
    setCurrentUserEmail(email);
    localStorage.setItem("gradify_user_email", email);
    localStorage.setItem("gradify_nav_state", "workspace");
    setWorkspaceOpen(true);
  };

  // Called when member (Teacher or Student) successfully accepts invitation and sets password
  const handleInviteAccepted = (data: any) => {
    if (data.user?.email) {
      setCurrentUserEmail(data.user.email);
    } else if (inviteEmail) {
      setCurrentUserEmail(inviteEmail);
    }
    const resolvedRole = (data.workspace?.role || inviteRole || "STUDENT").toUpperCase();
    setUserRole(resolvedRole);
    localStorage.setItem("gradify_user_role", resolvedRole);
    localStorage.setItem("gradify_nav_state", "workspace");
    window.history.replaceState({}, document.title, window.location.pathname);
    setAcceptInviteOpen(false);
    setWorkspaceOpen(true);
  };

  // Called when student accepts classroom invitation and sets password/roll number
  const handleClassroomInviteSuccess = (_classroomId: string) => {
    if (classroomInviteEmail) {
      setCurrentUserEmail(classroomInviteEmail);
    }
    setUserRole("STUDENT");
    localStorage.setItem("gradify_user_role", "STUDENT");
    localStorage.setItem("gradify_nav_state", "workspace");
    window.history.replaceState({}, document.title, window.location.pathname);
    setAcceptClassroomInviteOpen(false);
    setWorkspaceOpen(true);
  };

  return (
    <div className="min-h-screen bg-black text-[#E1E0CC] relative selection:bg-primary/20 selection:text-primary">
      {/* Background Video */}
      <div className="fixed inset-0 w-full h-full -z-10 overflow-hidden pointer-events-none">
        <CinematicVideo
          src={VIDEO_URL}
          className="w-full h-full object-cover scale-105 filter brightness-[0.45] contrast-[1.1]"
        />
        <div className="noise-overlay absolute inset-0 opacity-[0.45] mix-blend-overlay pointer-events-none" />
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/75 to-black/90 pointer-events-none" />
      </div>

      {/* Main Content Layout */}
      <main className="relative z-10 flex flex-col">
        <Hero
          onJoinLabClick={handleJoinLab}
          onSelectAuthTab={handleSelectAuthTab}
          onOpenContact={() => setContactOpen(true)}
          onOpenWorkspace={handleOpenWorkspace}
        />

        <About />

        <AuthSection
          initialTab={authTab}
          onOpenWorkspace={handleOpenWorkspace}
          onOpenVerificationModal={handleOpenVerificationModal}
        />
      </main>

      <Footer />

      <ContactModal
        isOpen={contactOpen}
        onClose={() => setContactOpen(false)}
      />

      <EmailVerificationModal
        isOpen={verificationOpen}
        onClose={() => setVerificationOpen(false)}
        email={verifyEmailAddress}
        simulatedToken={simToken}
        onVerified={handleVerificationSuccess}
      />

      {/* Member Invitation Password Setup Modal (Teacher or Student) */}
      <AcceptInvitationModal
        isOpen={acceptInviteOpen}
        onClose={() => setAcceptInviteOpen(false)}
        token={inviteToken}
        email={inviteEmail}
        role={inviteRole}
        onAccepted={handleInviteAccepted}
      />

      {/* Student Classroom Invitation Password & Roll Number Setup Modal */}
      <AcceptClassroomInvitationModal
        isOpen={acceptClassroomInviteOpen}
        onClose={() => setAcceptClassroomInviteOpen(false)}
        inviteToken={classroomInviteToken}
        inviteEmail={classroomInviteEmail}
        onSuccess={handleClassroomInviteSuccess}
      />

      {/* Workspace Card with live roles and member management */}
      <WorkspaceCard
        isOpen={workspaceOpen}
        onClose={handleCloseWorkspace}
        onSignOut={handleSignOut}
        currentUserEmail={currentUserEmail}
        initialRole={userRole}
      />
    </div>
  );
}

export default App;
