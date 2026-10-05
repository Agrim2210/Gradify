from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.database.base import Base
from app.modules.workspace.domain.enums.classroom_role import ClassroomRole
from app.modules.workspace.domain.enums.invitation_status import InvitationStatus


class ClassroomModel(Base):
    __tablename__ = "classrooms"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspace.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_teacher_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ClassroomMembershipModel(Base):
    __tablename__ = "classroom_memberships"
    __table_args__ = (UniqueConstraint("classroom_id", "user_id", name="uq_classroom_membership_classroom_user"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    classroom_id: Mapped[UUID] = mapped_column(ForeignKey("classrooms.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[ClassroomRole] = mapped_column(Enum(ClassroomRole, name="classroom_role"), nullable=False)
    roll_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ClassroomInvitationModel(Base):
    __tablename__ = "classroom_invitations"
    __table_args__ = (UniqueConstraint("classroom_id", "email", name="uq_classroom_invitation_classroom_email"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    classroom_id: Mapped[UUID] = mapped_column(ForeignKey("classrooms.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    invited_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[InvitationStatus] = mapped_column(Enum(InvitationStatus, name="invitation_status"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AssignmentModel(Base):
    __tablename__ = "assignments"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    classroom_id: Mapped[UUID] = mapped_column(ForeignKey("classrooms.id"), nullable=False)
    created_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    file_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AssignmentSubmissionModel(Base):
    __tablename__ = "assignment_submissions"
    __table_args__ = (UniqueConstraint("assignment_id", "student_user_id", name="uq_submission_assignment_student"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    assignment_id: Mapped[UUID] = mapped_column(ForeignKey("assignments.id"), nullable=False)
    student_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    file_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AssignmentGradeModel(Base):
    __tablename__ = "assignment_grades"
    __table_args__ = (UniqueConstraint("assignment_id", "student_user_id", name="uq_grade_assignment_student"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    assignment_id: Mapped[UUID] = mapped_column(ForeignKey("assignments.id"), nullable=False)
    student_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_auto_zero: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    graded_by_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    graded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

