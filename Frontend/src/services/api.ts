// Gradify Backend API Service Client

export interface WorkspaceResponse {
  id: string;
  name: string;
  slug: string;
}

export interface WorkspaceItem {
  id: string;
  name: string;
  slug: string;
  role: string;
  description?: string | null;
  created_at?: string | null;
}

export interface GetMeResponse {
  workspace_name: string;
  slug: string;
  role: string;
  workspaces?: WorkspaceItem[];
}

export interface WorkspaceMember {
  membership_id: string;
  user_id: string;
  email: string;
  role: "OWNER" | "TEACHER" | "STUDENT";
  status: string;
  joined_at: string | null;
}

export interface VerifyEmailResponse {
  message: string;
  access_token: string;
  refresh_token: string;
  email: string;
  user_id: string;
}

export interface ClassroomResponse {
  id: string;
  name: string;
  created_at: string;
  created_by_user_id?: string;
  assigned_teacher_id?: string | null;
  assigned_teacher_email?: string | null;
}

export interface AssignmentResponse {
  id: string;
  classroom_id: string;
  title: string;
  description: string | null;
  due_at: string | null;
  file_name: string | null;
  file_size: number | null;
  created_at: string;
  view_url: string | null;
  download_url: string | null;
}

export interface SubmissionResponse {
  id: string;
  assignment_id: string;
  student_user_id: string;
  file_name: string;
  file_size: number;
  submitted_at: string;
  email?: string;
  roll_number?: string;
  download_url?: string;
}

export interface AssignmentGradeInfo {
  score: number | null;
  feedback: string | null;
  is_auto_zero: boolean;
  graded_at: string | null;
}

export interface StudentOverviewItem {
  assignment: AssignmentResponse;
  submission: (SubmissionResponse & { download_url?: string }) | null;
  status: "TO_DO" | "COMPLETED_ON_TIME" | "COMPLETED_LATE" | "MISSED_DEADLINE";
  grade: AssignmentGradeInfo;
}

export interface StudentOverviewResponse {
  todo: StudentOverviewItem[];
  completed: StudentOverviewItem[];
  scores: StudentOverviewItem[];
  stats: {
    total_assignments: number;
    completed_count: number;
    todo_count: number;
    missed_count: number;
    average_score: number | null;
  };
}

export interface CategorizedSubmissionItem {
  student_user_id: string;
  email: string;
  roll_number: string | null;
  submission: (SubmissionResponse & { download_url?: string }) | null;
  grade: AssignmentGradeInfo | null;
  status: "ON_TIME" | "LATE" | "MISSED" | "PENDING";
}

export interface CategorizedSubmissionsResponse {
  assignment: AssignmentResponse;
  on_time: CategorizedSubmissionItem[];
  late: CategorizedSubmissionItem[];
  missed: CategorizedSubmissionItem[];
  pending: CategorizedSubmissionItem[];
  summary: {
    total_enrolled: number;
    on_time_count: number;
    late_count: number;
    missed_count: number;
    pending_count: number;
  };
}

export interface StudentGradebookRecord {
  student_user_id: string;
  email: string;
  roll_number: string | null;
  total_score: number;
  average_score: number | null;
  completed_count: number;
  missed_count: number;
  grades: {
    assignment_id: string;
    assignment_title: string;
    status: "ON_TIME" | "LATE" | "MISSED" | "PENDING";
    score: number | null;
    feedback: string | null;
    is_auto_zero: boolean;
    has_submission: boolean;
  }[];
}

export interface GradebookResponse {
  assignments: AssignmentResponse[];
  students: StudentGradebookRecord[];
  stats: {
    total_students: number;
    total_assignments: number;
    class_average: number | null;
  };
}

const API_BASE = "/api";

export const api = {
  // 1. Identity & Registration
  async signup(email: string, password: string): Promise<{ message: string; email?: string; raw_token?: string }> {
    localStorage.setItem("gradify_pending_email", email);
    const res = await fetch(`${API_BASE}/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || error.error || "Signup failed");
    }
    return await res.json();
  },

  // 2. Email Verification
  async verifyEmail(token: string): Promise<VerifyEmailResponse> {
    const res = await fetch(`${API_BASE}/verify-email?token=${encodeURIComponent(token)}`);
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || error.error || error.message || "Verification failed");
    }
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem("gradify_token", data.access_token);
      if (data.email) {
        localStorage.setItem("gradify_user_email", data.email);
      }
    }
    return data;
  },

  // 2b. Resend Verification Email
  async resendVerification(email: string): Promise<{ message: string; raw_token?: string }> {
    const res = await fetch(`${API_BASE}/resend-verification`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || error.error || "Failed to resend verification email");
    }
    return await res.json();
  },

  // 3. Login
  async login(email: string, password: string): Promise<{ access_token: string; refresh_token: string }> {
    const res = await fetch(`${API_BASE}/Login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      const err: any = new Error(error.detail || error.error || "Login failed");
      err.code = error.code;
      err.email = error.email;
      err.status = res.status;
      throw err;
    }
    const data = await res.json();
    localStorage.setItem("gradify_token", data.access_token);
    localStorage.setItem("gradify_user_email", email);
    return data;
  },

  // 4. Workspace Management
  async createWorkspace(name: string, description?: string): Promise<WorkspaceResponse> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/create_workspace`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ name, description: description || null }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || "Workspace creation failed");
    }
    return await res.json();
  },

  async getMyWorkspace(slug?: string): Promise<GetMeResponse | null> {
    const token = localStorage.getItem("gradify_token");
    if (!token) return null;
    try {
      const url = slug ? `${API_BASE}/Me?slug=${encodeURIComponent(slug)}` : `${API_BASE}/Me`;
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  },

  // 5. Invite Teacher (Owner Exclusive)
  async inviteTeacher(slug: string, email: string): Promise<{ message: string; invitation_url?: string }> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/workspaces/${slug}/invitations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ email, role: "TEACHER" }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || "Invitation failed");
    }
    return await res.json();
  },

  // 5b. Invite Student to Workspace (Owner or Faculty Teacher)
  async inviteWorkspaceStudent(slug: string, email: string): Promise<{ message: string; invitation_url?: string }> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/workspaces/${slug}/invitations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ email, role: "STUDENT" }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || "Student invitation failed");
    }
    return await res.json();
  },

  // 6. Accept Workspace Invitation (Sets password only and automatically signs in)
  async acceptInvitation(token: string, password: string): Promise<any> {
    const res = await fetch(`${API_BASE}/invitations/${encodeURIComponent(token)}/accept`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || error.message || "Failed to accept invitation");
    }
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem("gradify_token", data.access_token);
      if (data.user?.email) {
        localStorage.setItem("gradify_user_email", data.user.email);
      }
    }
    return data;
  },

  // 7. Get Workspace Members (For Admin/Owner view)
  async getWorkspaceMembers(slug: string): Promise<WorkspaceMember[]> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/workspaces/${slug}/members`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || "Failed to load members");
    }
    return await res.json();
  },

  // 8. Update Member Role (Owner feature)
  async updateMemberRole(slug: string, userId: string, role: string): Promise<any> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/workspaces/${slug}/members/${userId}/role`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ role }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || "Failed to update member role");
    }
    return await res.json();
  },

  // 9. Create Classroom
  async createClassroom(slug: string, name: string, assignedTeacherId?: string): Promise<{ id: string; name: string }> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/workspaces/${slug}/classrooms`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        name,
        assigned_teacher_id: assignedTeacherId || null,
      }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || "Classroom creation failed");
    }
    return await res.json();
  },

  // 10. List Classrooms
  async listClassrooms(slug: string): Promise<ClassroomResponse[]> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/workspaces/${slug}/classrooms`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return [];
    return await res.json();
  },

  // 11. Invite Student to Classroom
  async inviteStudent(classroomId: string, email: string): Promise<{ message: string }> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/invitations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ email }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || "Failed to invite student");
    }
    return await res.json();
  },

  // 12. Accept Classroom Invitation (public â€” sets password + roll number, auto sign-in)
  async acceptClassroomInvitation(token: string, password: string, rollNumber: string): Promise<any> {
    const res = await fetch(`${API_BASE}/classroom-invitations/${encodeURIComponent(token)}/accept`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password, roll_number: rollNumber }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || error.message || "Failed to accept classroom invitation");
    }
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem("gradify_token", data.access_token);
      if (data.email) {
        localStorage.setItem("gradify_user_email", data.email);
      }
    }
    return data;
  },

  // 13. List Assignments
  async listAssignments(classroomId: string): Promise<AssignmentResponse[]> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/assignments`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return [];
    return await res.json();
  },

  // 14. Create Assignment (Teacher)
  async createAssignment(classroomId: string, formData: FormData): Promise<AssignmentResponse> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/assignments`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || "Failed to create assignment");
    }
    return await res.json();
  },

  // 15. Submit Assignment (Student)
  async submitAssignment(classroomId: string, assignmentId: string, formData: FormData): Promise<SubmissionResponse> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/assignments/${assignmentId}/submissions`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || "Failed to submit assignment");
    }
    return await res.json();
  },

  // 16. List Submissions (Teacher — sorted by roll number)
  async listSubmissions(classroomId: string, assignmentId: string): Promise<SubmissionResponse[]> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/assignments/${assignmentId}/submissions`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return [];
    return await res.json();
  },

  // 17. Batch Invite Students (Workspace Head)
  async batchInviteStudents(
    slug: string,
    emails: string[]
  ): Promise<{ message: string; total_invited: number; invited: string[]; skipped: string[] }> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/workspaces/${slug}/students/batch-invite`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ emails }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || "Failed to batch invite students");
    }
    return await res.json();
  },

  // 18. Get Workspace Teachers (Accessible by all members including Students)
  async getWorkspaceTeachers(slug: string): Promise<WorkspaceMember[]> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/workspaces/${slug}/teachers`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return [];
    return await res.json();
  },

  // 19. List Classroom Notes
  async listClassroomNotes(classroomId: string): Promise<any[]> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/notes`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return [];
    return await res.json();
  },

  // 20. Student Overview (To-Do, Completed, Scores)
  async getStudentOverview(classroomId: string): Promise<StudentOverviewResponse> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/student-overview`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      throw new Error("Failed to load student overview");
    }
    return await res.json();
  },

  // 21. Categorized Submissions (Teacher)
  async getCategorizedSubmissions(classroomId: string, assignmentId: string): Promise<CategorizedSubmissionsResponse> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/assignments/${assignmentId}/categorized-submissions`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      throw new Error("Failed to load categorized submissions");
    }
    return await res.json();
  },

  // 22. Grade Submission (Teacher)
  async gradeSubmission(
    classroomId: string,
    assignmentId: string,
    payload: { student_user_id: string; score: number; feedback?: string }
  ): Promise<any> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/assignments/${assignmentId}/grade`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to submit grade");
    }
    return await res.json();
  },

  // 23. Classroom Gradebook / Academic Record (Teacher)
  async getClassroomGradebook(classroomId: string): Promise<GradebookResponse> {
    const token = localStorage.getItem("gradify_token") || "";
    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/gradebook`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      throw new Error("Failed to load classroom gradebook");
    }
    return await res.json();
  },
};

