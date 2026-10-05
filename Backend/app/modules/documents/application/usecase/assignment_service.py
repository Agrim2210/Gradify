"""AssignmentService — teacher creates/lists assignments; students submit; teacher views submissions by roll number."""
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.domain.repositories.storage_service import StorageService
from app.modules.workspace.domain.enums.classroom_role import ClassroomRole
from app.modules.workspace.infra.database.classroom_models import (
    AssignmentGradeModel,
    AssignmentModel,
    AssignmentSubmissionModel,
    ClassroomMembershipModel,
    ClassroomModel,
)
from app.infra.database.uow import uow_contract
from app.modules.auth.infra.persistent.models.models import UserModel


class AssignmentService:
    def __init__(self, session: AsyncSession, storage: StorageService, uow: uow_contract):
        self._session = session
        self._storage = storage
        self._uow = uow

    # ─── Helpers ──────────────────────────────────────────────────────────────

    async def _require_owner(self, classroom_id: UUID, user_id: UUID):
        classroom = await self._session.get(ClassroomModel, classroom_id)
        if classroom is None:
            from app.modules.documents.domain.exception.exception import ClassroomNotFound
            raise ClassroomNotFound()

        from app.modules.workspace.infra.database.membership_sql import WorkspaceMembershipModel
        from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole
        ws_mem = (
            await self._session.execute(
                select(WorkspaceMembershipModel).where(
                    WorkspaceMembershipModel.workspace_id == classroom.workspace_id,
                    WorkspaceMembershipModel.user_id == user_id,
                )
            )
        ).scalar_one_or_none()
        if ws_mem is None:
            from app.modules.documents.domain.exception.exception import ClassroomAccessDenied
            raise ClassroomAccessDenied()

        # Workspace Head (OWNER) always has full permissions
        if ws_mem.role == WorkspaceRole.OWNER:
            return

        # Teachers can only act as owner if created by them or assigned to them
        if ws_mem.role == WorkspaceRole.TEACHER:
            if classroom.created_by_user_id == user_id or classroom.assigned_teacher_id == user_id:
                return
            mem = (
                await self._session.execute(
                    select(ClassroomMembershipModel).where(
                        ClassroomMembershipModel.classroom_id == classroom_id,
                        ClassroomMembershipModel.user_id == user_id,
                        ClassroomMembershipModel.role == ClassroomRole.OWNER,
                    )
                )
            ).scalar_one_or_none()
            if mem is not None:
                return

        from app.modules.documents.domain.exception.exception import ClassroomAccessDenied
        raise ClassroomAccessDenied()

    async def _require_member(self, classroom_id: UUID, user_id: UUID):
        classroom = await self._session.get(ClassroomModel, classroom_id)
        if classroom is None:
            from app.modules.documents.domain.exception.exception import ClassroomNotFound
            raise ClassroomNotFound()

        # Check if already a direct classroom member (e.g. accepted classroom invite)
        cls_mem = (
            await self._session.execute(
                select(ClassroomMembershipModel).where(
                    ClassroomMembershipModel.classroom_id == classroom_id,
                    ClassroomMembershipModel.user_id == user_id,
                )
            )
        ).scalar_one_or_none()
        if cls_mem is not None and cls_mem.role == ClassroomRole.STUDENT:
            return cls_mem

        from app.modules.workspace.infra.database.membership_sql import WorkspaceMembershipModel
        from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole
        ws_mem = (
            await self._session.execute(
                select(WorkspaceMembershipModel).where(
                    WorkspaceMembershipModel.workspace_id == classroom.workspace_id,
                    WorkspaceMembershipModel.user_id == user_id,
                )
            )
        ).scalar_one_or_none()
        if ws_mem is None:
            if cls_mem is not None:
                return cls_mem
            from app.modules.documents.domain.exception.exception import ClassroomAccessDenied
            raise ClassroomAccessDenied()

        # Workspace Head (OWNER) has full access
        if ws_mem.role == WorkspaceRole.OWNER:
            return

        # Teachers can ONLY enter classrooms created by or assigned to them
        if ws_mem.role == WorkspaceRole.TEACHER:
            if classroom.created_by_user_id == user_id or classroom.assigned_teacher_id == user_id:
                return
            if cls_mem is not None and cls_mem.role == ClassroomRole.OWNER:
                return
            from app.modules.documents.domain.exception.exception import ClassroomAccessDenied
            raise ClassroomAccessDenied()

        # For STUDENTS in workspace: auto-enroll in classroom if not already enrolled
        if cls_mem is not None:
            return cls_mem


        now = datetime.now(timezone.utc)
        auto_mem = ClassroomMembershipModel(
            id=uuid4(),
            classroom_id=classroom_id,
            user_id=user_id,
            role=ClassroomRole.STUDENT,
            roll_number=None,
            created_at=now,
        )
        self._session.add(auto_mem)
        await self._uow.commit()
        return auto_mem

    # ─── Create Assignment ─────────────────────────────────────────────────────

    async def create_assignment(
        self,
        classroom_id: UUID,
        teacher_user_id: UUID,
        title: str,
        description: str | None,
        due_at: str | None,
        file=None,
    ) -> dict:
        await self._require_owner(classroom_id, teacher_user_id)

        now = datetime.now(timezone.utc)
        assignment_id = uuid4()
        file_key = None
        file_name = None
        file_size = None

        if file is not None:
            clean = (file.filename or "assignment.pdf").replace(" ", "_")
            file_key = f"classrooms/{classroom_id}/assignments/{assignment_id}/{clean}"
            file_name = file.filename or "assignment.pdf"
            file_size = file.size or 0
            await self._storage.upload_file(
                file_obj=file.file,
                file_key=file_key,
                content_type=file.content_type or "application/pdf",
            )

        due_parsed: datetime | None = None
        if due_at:
            try:
                due_parsed = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
            except ValueError:
                pass

        assignment = AssignmentModel(
            id=assignment_id,
            classroom_id=classroom_id,
            created_by_user_id=teacher_user_id,
            title=title,
            description=description,
            due_at=due_parsed,
            file_key=file_key,
            file_name=file_name,
            file_size=file_size,
            created_at=now,
        )
        self._session.add(assignment)
        await self._uow.commit()

        return self._assignment_to_dict(assignment)

    # ─── List Assignments ──────────────────────────────────────────────────────

    async def list_assignments(self, classroom_id: UUID, user_id: UUID) -> list[dict]:
        await self._require_member(classroom_id, user_id)
        rows = (
            await self._session.execute(
                select(AssignmentModel)
                .where(AssignmentModel.classroom_id == classroom_id)
                .order_by(AssignmentModel.created_at.desc())
            )
        ).scalars().all()
        return [self._assignment_to_dict(a) for a in rows]

    # ─── Submit Assignment ─────────────────────────────────────────────────────

    async def submit_assignment(
        self,
        classroom_id: UUID,
        assignment_id: UUID,
        student_user_id: UUID,
        file,
        roll_number: str | None = None,
    ) -> dict:
        # Verify student is a classroom member and update roll number if supplied
        mem = await self._require_member(classroom_id, student_user_id)
        if roll_number and hasattr(mem, "roll_number") and mem.roll_number != roll_number.strip().upper():
            mem.roll_number = roll_number.strip().upper()

        assignment = await self._session.get(AssignmentModel, assignment_id)
        if assignment is None or assignment.classroom_id != classroom_id:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Assignment not found")

        clean = (file.filename or "submission.pdf").replace(" ", "_")
        file_key = f"classrooms/{classroom_id}/assignments/{assignment_id}/submissions/{student_user_id}/{clean}"
        now = datetime.now(timezone.utc)

        # Check for existing submission → update
        existing = (
            await self._session.execute(
                select(AssignmentSubmissionModel).where(
                    AssignmentSubmissionModel.assignment_id == assignment_id,
                    AssignmentSubmissionModel.student_user_id == student_user_id,
                )
            )
        ).scalar_one_or_none()

        await self._storage.upload_file(
            file_obj=file.file,
            file_key=file_key,
            content_type=file.content_type or "application/pdf",
        )

        if existing is not None:
            existing.file_key = file_key
            existing.file_name = file.filename or "submission.pdf"
            existing.file_size = file.size or 0
            existing.submitted_at = now
            submission = existing
        else:
            submission = AssignmentSubmissionModel(
                id=uuid4(),
                assignment_id=assignment_id,
                student_user_id=student_user_id,
                file_key=file_key,
                file_name=file.filename or "submission.pdf",
                file_size=file.size or 0,
                submitted_at=now,
            )
            self._session.add(submission)

        await self._uow.commit()
        return self._submission_to_dict(submission)

    # ─── List Submissions (teacher, sorted by roll number) ────────────────────

    async def list_submissions(self, classroom_id: UUID, assignment_id: UUID, requester_id: UUID) -> list[dict]:
        await self._require_owner(classroom_id, requester_id)

        rows = (
            await self._session.execute(
                select(AssignmentSubmissionModel, ClassroomMembershipModel, UserModel)
                .join(
                    ClassroomMembershipModel,
                    (ClassroomMembershipModel.classroom_id == classroom_id)
                    & (ClassroomMembershipModel.user_id == AssignmentSubmissionModel.student_user_id),
                )
                .join(UserModel, UserModel.id == AssignmentSubmissionModel.student_user_id)
                .where(AssignmentSubmissionModel.assignment_id == assignment_id)
                .order_by(ClassroomMembershipModel.roll_number)
            )
        ).all()

        result = []
        for sub, mem, user in rows:
            d = self._submission_to_dict(sub)
            d["email"] = user.email
            d["roll_number"] = mem.roll_number
            d["download_url"] = self._storage.generate_presigned_download_url(sub.file_key, sub.file_name)
            result.append(d)
        return result

    # ─── Serializers ──────────────────────────────────────────────────────────

    def _assignment_to_dict(self, a: AssignmentModel) -> dict:
        view_url = None
        download_url = None
        if a.file_key:
            view_url = self._storage.generate_presigned_view_url(a.file_key)
            download_url = self._storage.generate_presigned_download_url(a.file_key, a.file_name or "assignment.pdf")
        return {
            "id": str(a.id),
            "classroom_id": str(a.classroom_id),
            "title": a.title,
            "description": a.description,
            "due_at": a.due_at.isoformat() if a.due_at else None,
            "file_name": a.file_name,
            "file_size": a.file_size,
            "created_at": a.created_at.isoformat(),
            "view_url": view_url,
            "download_url": download_url,
        }

    def _submission_to_dict(self, s: AssignmentSubmissionModel) -> dict:
        return {
            "id": str(s.id),
            "assignment_id": str(s.assignment_id),
            "student_user_id": str(s.student_user_id),
            "file_name": s.file_name,
            "file_size": s.file_size,
            "submitted_at": s.submitted_at.isoformat(),
        }

    def _grade_to_dict(self, g: AssignmentGradeModel) -> dict:
        return {
            "id": str(g.id),
            "assignment_id": str(g.assignment_id),
            "student_user_id": str(g.student_user_id),
            "score": g.score,
            "feedback": g.feedback,
            "is_auto_zero": g.is_auto_zero,
            "graded_by_user_id": str(g.graded_by_user_id) if g.graded_by_user_id else None,
            "graded_at": g.graded_at.isoformat(),
        }

    # ─── Student Overview (To-Do, Completed, Scores) ───────────────────────────

    async def get_student_overview(self, classroom_id: UUID, student_user_id: UUID) -> dict:
        await self._require_member(classroom_id, student_user_id)
        assignments = (
            await self._session.execute(
                select(AssignmentModel)
                .where(AssignmentModel.classroom_id == classroom_id)
                .order_by(AssignmentModel.due_at.asc().nulls_last(), AssignmentModel.created_at.desc())
            )
        ).scalars().all()

        assignment_ids = [a.id for a in assignments]
        subs_map: dict[UUID, AssignmentSubmissionModel] = {}
        grades_map: dict[UUID, AssignmentGradeModel] = {}

        if assignment_ids:
            subs = (
                await self._session.execute(
                    select(AssignmentSubmissionModel).where(
                        AssignmentSubmissionModel.assignment_id.in_(assignment_ids),
                        AssignmentSubmissionModel.student_user_id == student_user_id,
                    )
                )
            ).scalars().all()
            for s in subs:
                subs_map[s.assignment_id] = s

            grades = (
                await self._session.execute(
                    select(AssignmentGradeModel).where(
                        AssignmentGradeModel.assignment_id.in_(assignment_ids),
                        AssignmentGradeModel.student_user_id == student_user_id,
                    )
                )
            ).scalars().all()
            for g in grades:
                grades_map[g.assignment_id] = g

        now = datetime.now(timezone.utc)
        todo_list = []
        completed_list = []
        scores_list = []

        for a in assignments:
            a_dict = self._assignment_to_dict(a)
            sub = subs_map.get(a.id)
            grd = grades_map.get(a.id)

            sub_dict = None
            if sub:
                sub_dict = self._submission_to_dict(sub)
                sub_dict["download_url"] = self._storage.generate_presigned_download_url(sub.file_key, sub.file_name)
                is_late = a.due_at is not None and sub.submitted_at > a.due_at
                status = "COMPLETED_LATE" if is_late else "COMPLETED_ON_TIME"
            else:
                is_overdue = a.due_at is not None and a.due_at < now
                status = "MISSED_DEADLINE" if is_overdue else "TO_DO"

            # Grade resolution
            if grd is not None:
                grade_info = {
                    "score": grd.score,
                    "feedback": grd.feedback,
                    "is_auto_zero": grd.is_auto_zero,
                    "graded_at": grd.graded_at.isoformat(),
                }
            elif status == "MISSED_DEADLINE":
                # Automatically 0 if deadline missed with no submission
                grade_info = {
                    "score": 0.0,
                    "feedback": "Missed deadline — Automatic 0",
                    "is_auto_zero": True,
                    "graded_at": None,
                }
            else:
                grade_info = {
                    "score": None,
                    "feedback": None,
                    "is_auto_zero": False,
                    "graded_at": None,
                }

            item = {
                "assignment": a_dict,
                "submission": sub_dict,
                "status": status,
                "grade": grade_info,
            }

            scores_list.append(item)
            if status in {"COMPLETED_ON_TIME", "COMPLETED_LATE"}:
                completed_list.append(item)
            else:
                todo_list.append(item)

        scored_scores = [item["grade"]["score"] for item in scores_list if item["grade"]["score"] is not None]
        avg_score = round(sum(scored_scores) / len(scored_scores), 1) if scored_scores else None

        return {
            "todo": todo_list,
            "completed": completed_list,
            "scores": scores_list,
            "stats": {
                "total_assignments": len(assignments),
                "completed_count": len(completed_list),
                "todo_count": sum(1 for item in scores_list if item["status"] == "TO_DO"),
                "missed_count": sum(1 for item in scores_list if item["status"] == "MISSED_DEADLINE"),
                "average_score": avg_score,
            },
        }

    # ─── Categorized Submissions (Teacher) ────────────────────────────────────

    async def get_categorized_submissions(self, classroom_id: UUID, assignment_id: UUID, requester_id: UUID) -> dict:
        await self._require_owner(classroom_id, requester_id)
        assignment = await self._session.get(AssignmentModel, assignment_id)
        if assignment is None or assignment.classroom_id != classroom_id:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Assignment not found")

        students = (
            await self._session.execute(
                select(ClassroomMembershipModel, UserModel)
                .join(UserModel, UserModel.id == ClassroomMembershipModel.user_id)
                .where(
                    ClassroomMembershipModel.classroom_id == classroom_id,
                    ClassroomMembershipModel.role == ClassroomRole.STUDENT,
                )
                .order_by(ClassroomMembershipModel.roll_number.asc().nulls_last(), UserModel.email.asc())
            )
        ).all()

        subs = (
            await self._session.execute(
                select(AssignmentSubmissionModel).where(AssignmentSubmissionModel.assignment_id == assignment_id)
            )
        ).scalars().all()
        subs_map = {s.student_user_id: s for s in subs}

        grades = (
            await self._session.execute(
                select(AssignmentGradeModel).where(AssignmentGradeModel.assignment_id == assignment_id)
            )
        ).scalars().all()
        grades_map = {g.student_user_id: g for g in grades}

        now = datetime.now(timezone.utc)
        on_time = []
        late = []
        missed = []
        pending = []

        for mem, user in students:
            sub = subs_map.get(user.id)
            grd = grades_map.get(user.id)

            sub_info = None
            if sub:
                sub_info = self._submission_to_dict(sub)
                sub_info["download_url"] = self._storage.generate_presigned_download_url(sub.file_key, sub.file_name)

            if grd:
                grade_info = {
                    "score": grd.score,
                    "feedback": grd.feedback,
                    "is_auto_zero": grd.is_auto_zero,
                    "graded_at": grd.graded_at.isoformat(),
                }
            else:
                grade_info = None

            record = {
                "student_user_id": str(user.id),
                "email": user.email,
                "roll_number": mem.roll_number,
                "submission": sub_info,
                "grade": grade_info,
            }

            if sub:
                is_late = assignment.due_at is not None and sub.submitted_at > assignment.due_at
                if is_late:
                    record["status"] = "LATE"
                    late.append(record)
                else:
                    record["status"] = "ON_TIME"
                    on_time.append(record)
            else:
                is_overdue = assignment.due_at is not None and assignment.due_at < now
                if is_overdue:
                    record["status"] = "MISSED"
                    if not record["grade"]:
                        record["grade"] = {
                            "score": 0.0,
                            "feedback": "Missed deadline",
                            "is_auto_zero": True,
                            "graded_at": None,
                        }
                    missed.append(record)
                else:
                    record["status"] = "PENDING"
                    pending.append(record)

        return {
            "assignment": self._assignment_to_dict(assignment),
            "on_time": on_time,
            "late": late,
            "missed": missed,
            "pending": pending,
            "summary": {
                "total_enrolled": len(students),
                "on_time_count": len(on_time),
                "late_count": len(late),
                "missed_count": len(missed),
                "pending_count": len(pending),
            },
        }

    # ─── Grade Submission (Teacher) ───────────────────────────────────────────

    async def grade_submission(
        self,
        classroom_id: UUID,
        assignment_id: UUID,
        requester_id: UUID,
        student_user_id: UUID,
        score: float,
        feedback: str | None = None,
    ) -> dict:
        await self._require_owner(classroom_id, requester_id)
        assignment = await self._session.get(AssignmentModel, assignment_id)
        if assignment is None or assignment.classroom_id != classroom_id:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Assignment not found")

        existing = (
            await self._session.execute(
                select(AssignmentGradeModel).where(
                    AssignmentGradeModel.assignment_id == assignment_id,
                    AssignmentGradeModel.student_user_id == student_user_id,
                )
            )
        ).scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if existing:
            existing.score = score
            existing.feedback = feedback
            existing.is_auto_zero = False
            existing.graded_by_user_id = requester_id
            existing.graded_at = now
            grade_obj = existing
        else:
            grade_obj = AssignmentGradeModel(
                id=uuid4(),
                assignment_id=assignment_id,
                student_user_id=student_user_id,
                score=score,
                feedback=feedback,
                is_auto_zero=False,
                graded_by_user_id=requester_id,
                graded_at=now,
            )
            self._session.add(grade_obj)

        await self._uow.commit()
        return self._grade_to_dict(grade_obj)

    # ─── Classroom Gradebook (Teacher Academic Record) ─────────────────────────

    async def get_classroom_gradebook(self, classroom_id: UUID, requester_id: UUID) -> dict:
        await self._require_owner(classroom_id, requester_id)

        assignments = (
            await self._session.execute(
                select(AssignmentModel)
                .where(AssignmentModel.classroom_id == classroom_id)
                .order_by(AssignmentModel.created_at.asc())
            )
        ).scalars().all()

        students = (
            await self._session.execute(
                select(ClassroomMembershipModel, UserModel)
                .join(UserModel, UserModel.id == ClassroomMembershipModel.user_id)
                .where(
                    ClassroomMembershipModel.classroom_id == classroom_id,
                    ClassroomMembershipModel.role == ClassroomRole.STUDENT,
                )
                .order_by(ClassroomMembershipModel.roll_number.asc().nulls_last(), UserModel.email.asc())
            )
        ).all()

        assignment_ids = [a.id for a in assignments]
        subs_map: dict[tuple[UUID, UUID], AssignmentSubmissionModel] = {}
        grades_map: dict[tuple[UUID, UUID], AssignmentGradeModel] = {}

        if assignment_ids:
            subs = (
                await self._session.execute(
                    select(AssignmentSubmissionModel).where(AssignmentSubmissionModel.assignment_id.in_(assignment_ids))
                )
            ).scalars().all()
            for s in subs:
                subs_map[(s.assignment_id, s.student_user_id)] = s

            grades = (
                await self._session.execute(
                    select(AssignmentGradeModel).where(AssignmentGradeModel.assignment_id.in_(assignment_ids))
                )
            ).scalars().all()
            for g in grades:
                grades_map[(g.assignment_id, g.student_user_id)] = g

        now = datetime.now(timezone.utc)
        student_records = []
        all_student_scores = []

        for mem, user in students:
            grades_for_student = []
            student_total = 0.0
            graded_count = 0
            completed_count = 0
            missed_count = 0

            for a in assignments:
                sub = subs_map.get((a.id, user.id))
                grd = grades_map.get((a.id, user.id))

                if sub:
                    is_late = a.due_at is not None and sub.submitted_at > a.due_at
                    status = "LATE" if is_late else "ON_TIME"
                    completed_count += 1
                else:
                    is_overdue = a.due_at is not None and a.due_at < now
                    if is_overdue:
                        status = "MISSED"
                        missed_count += 1
                    else:
                        status = "PENDING"

                if grd:
                    score = grd.score
                    feedback = grd.feedback
                    is_auto_zero = grd.is_auto_zero
                    student_total += score
                    graded_count += 1
                    all_student_scores.append(score)
                elif status == "MISSED":
                    score = 0.0
                    feedback = "Missed deadline — Auto 0"
                    is_auto_zero = True
                    student_total += 0.0
                    graded_count += 1
                    all_student_scores.append(0.0)
                else:
                    score = None
                    feedback = None
                    is_auto_zero = False

                grades_for_student.append({
                    "assignment_id": str(a.id),
                    "assignment_title": a.title,
                    "status": status,
                    "score": score,
                    "feedback": feedback,
                    "is_auto_zero": is_auto_zero,
                    "has_submission": sub is not None,
                })

            student_avg = round(student_total / graded_count, 1) if graded_count > 0 else None

            student_records.append({
                "student_user_id": str(user.id),
                "email": user.email,
                "roll_number": mem.roll_number,
                "total_score": round(student_total, 1),
                "average_score": student_avg,
                "completed_count": completed_count,
                "missed_count": missed_count,
                "grades": grades_for_student,
            })

        class_average = (
            round(sum(all_student_scores) / len(all_student_scores), 1)
            if all_student_scores
            else None
        )

        return {
            "assignments": [self._assignment_to_dict(a) for a in assignments],
            "students": student_records,
            "stats": {
                "total_students": len(students),
                "total_assignments": len(assignments),
                "class_average": class_average,
            },
        }

