"""
Enrollment service for EduVerse platform
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.core.logging import get_logger, log_performance
from app.models.enrollment import Enrollment
from app.models.course import Course
from app.models.user import User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse


class EnrollmentService:
    """Service for managing course enrollments"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = get_logger("enrollment_service")

    @log_performance
    async def enroll_user_in_course(self, user_id: str, course_id: str) -> Enrollment:
        """Enroll a user in a course"""
        try:
            # Check if course exists and is published
            course = await self._get_course_by_id(course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found"
                )

            if not course.is_published:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course is not available for enrollment"
                )

            # Check if user is already enrolled
            existing_enrollment = await self.get_enrollment(user_id, course_id)
            if existing_enrollment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already enrolled in this course"
                )

            # Create enrollment
            enrollment = Enrollment(
                id=str(uuid.uuid4()),
                user_id=user_id,
                course_id=course_id,
                total_lessons=course.duration_minutes // 10 if course.duration_minutes else 10,  # Estimate lessons
                enrolled_at=func.now()
            )

            self.db.add(enrollment)
            await self.db.commit()
            await self.db.refresh(enrollment)

            # Update course enrollment count
            await self.db.execute(
                update(Course)
                .where(Course.id == course_id)
                .values(enrollment_count=Course.enrollment_count + 1)
            )
            await self.db.commit()

            self.logger.info(f"User {user_id} enrolled in course {course_id}")
            return enrollment

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to enroll user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Enrollment failed: {str(e)}"
            )

    @log_performance
    async def get_enrollment(self, user_id: str, course_id: str) -> Optional[Enrollment]:
        """Get enrollment for a user and course"""
        try:
            result = await self.db.execute(
                select(Enrollment)
                .options(
                    selectinload(Enrollment.user),
                    selectinload(Enrollment.course)
                )
                .where(
                    and_(
                        Enrollment.user_id == user_id,
                        Enrollment.course_id == course_id
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting enrollment: {e}")
            return None

    @log_performance
    async def get_user_enrollments(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        include_completed: bool = True,
        include_active: bool = True
    ) -> Dict[str, Any]:
        """Get all enrollments for a user"""
        try:
            query = select(Enrollment).options(
                selectinload(Enrollment.course)
            ).where(Enrollment.user_id == user_id)

            # Apply status filters
            status_conditions = []
            if include_completed:
                status_conditions.append(Enrollment.is_completed == True)
            if include_active:
                status_conditions.append(
                    and_(
                        Enrollment.is_completed == False,
                        Enrollment.is_active == True
                    )
                )

            if status_conditions:
                query = query.where(or_(*status_conditions))

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Apply pagination and ordering
            query = query.order_by(Enrollment.enrolled_at.desc())
            query = query.offset(skip).limit(limit)

            result = await self.db.execute(query)
            enrollments = result.scalars().all()

            return {
                "enrollments": enrollments,
                "total": total,
                "skip": skip,
                "limit": limit
            }

        except Exception as e:
            self.logger.error(f"Error getting user enrollments: {e}")
            return {
                "enrollments": [],
                "total": 0,
                "skip": skip,
                "limit": limit
            }

    @log_performance
    async def get_course_enrollments(
        self,
        course_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get all enrollments for a course"""
        try:
            query = select(Enrollment).options(
                selectinload(Enrollment.user)
            ).where(Enrollment.course_id == course_id)

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Apply pagination and ordering
            query = query.order_by(Enrollment.enrolled_at.desc())
            query = query.offset(skip).limit(limit)

            result = await self.db.execute(query)
            enrollments = result.scalars().all()

            return {
                "enrollments": enrollments,
                "total": total,
                "skip": skip,
                "limit": limit
            }

        except Exception as e:
            self.logger.error(f"Error getting course enrollments: {e}")
            return {
                "enrollments": [],
                "total": 0,
                "skip": skip,
                "limit": limit
            }

    @log_performance
    async def update_enrollment_progress(
        self,
        user_id: str,
        course_id: str,
        progress_data: EnrollmentUpdate
    ) -> Enrollment:
        """Update enrollment progress"""
        try:
            enrollment = await self.get_enrollment(user_id, course_id)
            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Enrollment not found"
                )

            # Update progress
            if progress_data.progress_percentage is not None:
                enrollment.update_progress(progress_data.progress_percentage)

            # Update scores
            if hasattr(progress_data, 'quiz_score') and progress_data.quiz_score is not None:
                enrollment.update_scores(quiz_score=progress_data.quiz_score)

            if hasattr(progress_data, 'final_score') and progress_data.final_score is not None:
                enrollment.update_scores(final_score=progress_data.final_score)

            # Update time spent if provided
            if hasattr(progress_data, 'time_spent_minutes') and progress_data.time_spent_minutes:
                enrollment.add_time_spent(progress_data.time_spent_minutes)

            await self.db.commit()
            await self.db.refresh(enrollment)

            self.logger.info(f"Updated progress for enrollment {enrollment.id}: {enrollment.progress_percentage}%")
            return enrollment

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to update enrollment progress: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Progress update failed: {str(e)}"
            )

    @log_performance
    async def complete_enrollment(self, user_id: str, course_id: str) -> Enrollment:
        """Mark enrollment as completed"""
        try:
            enrollment = await self.get_enrollment(user_id, course_id)
            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Enrollment not found"
                )

            if enrollment.is_completed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Enrollment is already completed"
                )

            enrollment.is_completed = True
            enrollment.completed_at = func.now()
            enrollment.progress_percentage = 100.0

            await self.db.commit()
            await self.db.refresh(enrollment)

            self.logger.info(f"Completed enrollment {enrollment.id}")
            return enrollment

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to complete enrollment: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Completion failed: {str(e)}"
            )

    @log_performance
    async def unenroll_user(self, user_id: str, course_id: str) -> bool:
        """Unenroll a user from a course"""
        try:
            enrollment = await self.get_enrollment(user_id, course_id)
            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Enrollment not found"
                )

            # Soft delete by deactivating
            enrollment.is_active = False

            # Decrease course enrollment count
            await self.db.execute(
                update(Course)
                .where(Course.id == course_id)
                .values(enrollment_count=Course.enrollment_count - 1)
            )

            await self.db.commit()

            self.logger.info(f"Unenrolled user {user_id} from course {course_id}")
            return True

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to unenroll user: {e}")
            return False

    @log_performance
    async def issue_certificate(self, user_id: str, course_id: str, certificate_url: str) -> Enrollment:
        """Issue completion certificate"""
        try:
            enrollment = await self.get_enrollment(user_id, course_id)
            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Enrollment not found"
                )

            if not enrollment.is_completed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot issue certificate for incomplete enrollment"
                )

            enrollment.issue_certificate(certificate_url)

            await self.db.commit()
            await self.db.refresh(enrollment)

            self.logger.info(f"Issued certificate for enrollment {enrollment.id}")
            return enrollment

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to issue certificate: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Certificate issuance failed: {str(e)}"
            )

    @log_performance
    async def get_enrollment_statistics(self, course_id: Optional[str] = None) -> Dict[str, Any]:
        """Get enrollment statistics"""
        try:
            if course_id:
                # Course-specific statistics
                result = await self.db.execute(
                    select(
                        func.count(Enrollment.id).label('total_enrollments'),
                        func.avg(Enrollment.progress_percentage).label('avg_progress'),
                        func.count(func.nullif(Enrollment.is_completed, False)).label('completed_count'),
                        func.avg(Enrollment.final_score).label('avg_final_score')
                    ).where(
                        and_(
                            Enrollment.course_id == course_id,
                            Enrollment.is_active == True
                        )
                    )
                )
            else:
                # Global statistics
                result = await self.db.execute(
                    select(
                        func.count(Enrollment.id).label('total_enrollments'),
                        func.avg(Enrollment.progress_percentage).label('avg_progress'),
                        func.count(func.nullif(Enrollment.is_completed, False)).label('completed_count'),
                        func.avg(Enrollment.final_score).label('avg_final_score')
                    ).where(Enrollment.is_active == True)
                )

            stats = result.first()

            return {
                "total_enrollments": stats.total_enrollments or 0,
                "average_progress": round(stats.avg_progress or 0, 2),
                "completed_enrollments": stats.completed_count or 0,
                "average_final_score": round(stats.avg_final_score or 0, 2),
                "completion_rate": round(
                    (stats.completed_count or 0) / (stats.total_enrollments or 1) * 100, 2
                )
            }

        except Exception as e:
            self.logger.error(f"Error getting enrollment statistics: {e}")
            return {
                "total_enrollments": 0,
                "average_progress": 0,
                "completed_enrollments": 0,
                "average_final_score": 0,
                "completion_rate": 0
            }

    async def _get_course_by_id(self, course_id: str) -> Optional[Course]:
        """Helper method to get course by ID"""
        try:
            result = await self.db.execute(
                select(Course).where(Course.id == course_id)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
