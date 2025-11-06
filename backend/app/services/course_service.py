"""
Course service for EduVerse platform
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.core.logging import get_logger, log_performance
from app.models.course import Course
from app.models.category import Category
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate, CourseFilter


class CourseService:
    """Service for managing courses"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = get_logger("course_service")

    @log_performance
    async def create_course(self, course_data: CourseCreate, instructor_id: str) -> Course:
        """Create a new course"""
        try:
            # Generate slug from title
            slug = self._generate_slug(course_data.title)

            # Check if slug already exists
            existing_course = await self.get_course_by_slug(slug)
            if existing_course:
                slug = f"{slug}-{uuid.uuid4().hex[:8]}"

            course = Course(
                id=str(uuid.uuid4()),
                title=course_data.title,
                slug=slug,
                description=course_data.description,
                short_description=course_data.short_description,
                thumbnail_url=course_data.thumbnail_url,
                trailer_video_url=course_data.trailer_video_url,
                duration_minutes=course_data.duration_minutes,
                difficulty_level=course_data.difficulty_level,
                instructor_id=instructor_id,
                category_id=course_data.category_id,
                price=course_data.price,
                currency=course_data.currency,
                is_free=course_data.is_free,
                supports_vr=course_data.supports_vr,
                supports_ar=course_data.supports_ar,
                vr_environment_url=course_data.vr_environment_url,
                ar_markers=course_data.ar_markers,
                tags=course_data.tags,
                learning_objectives=course_data.learning_objectives,
                prerequisites=course_data.prerequisites,
                ai_generated_content=course_data.ai_generated_content,
                personalization_enabled=course_data.personalization_enabled,
                is_published=False
            )

            self.db.add(course)
            await self.db.commit()
            await self.db.refresh(course)

            self.logger.info(f"Course created: {course.title} by instructor {instructor_id}")
            return course

        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to create course: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course creation failed: {str(e)}"
            )

    @log_performance
    async def get_course_by_id(self, course_id: str) -> Optional[Course]:
        """Get course by ID with related data"""
        try:
            result = await self.db.execute(
                select(Course)
                .options(
                    selectinload(Course.instructor),
                    selectinload(Course.category)
                )
                .where(Course.id == course_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting course by ID: {e}")
            return None

    @log_performance
    async def get_course_by_slug(self, slug: str) -> Optional[Course]:
        """Get course by slug"""
        try:
            result = await self.db.execute(
                select(Course).where(Course.slug == slug)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting course by slug: {e}")
            return None

    @log_performance
    async def get_courses(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[CourseFilter] = None,
        include_unpublished: bool = False
    ) -> Dict[str, Any]:
        """Get courses with filtering and pagination"""
        try:
            query = select(Course).options(
                selectinload(Course.instructor),
                selectinload(Course.category)
            )

            # Apply filters
            if filters:
                conditions = []

                if filters.category_id:
                    conditions.append(Course.category_id == filters.category_id)

                if filters.difficulty_level:
                    conditions.append(Course.difficulty_level == filters.difficulty_level)

                if filters.instructor_id:
                    conditions.append(Course.instructor_id == filters.instructor_id)

                if filters.is_free is not None:
                    conditions.append(Course.is_free == filters.is_free)

                if filters.supports_vr is not None:
                    conditions.append(Course.supports_vr == filters.supports_vr)

                if filters.supports_ar is not None:
                    conditions.append(Course.supports_ar == filters.supports_ar)

                if filters.min_price is not None:
                    conditions.append(Course.price >= filters.min_price)

                if filters.max_price is not None:
                    conditions.append(Course.price <= filters.max_price)

                if filters.search_query:
                    search_term = f"%{filters.search_query}%"
                    conditions.append(
                        or_(
                            Course.title.ilike(search_term),
                            Course.description.ilike(search_term),
                            Course.short_description.ilike(search_term)
                        )
                    )

                if not include_unpublished:
                    conditions.append(Course.is_published == True)

                if conditions:
                    query = query.where(and_(*conditions))

            # Apply sorting
            if filters and filters.sort_by:
                sort_column = getattr(Course, filters.sort_by, Course.created_at)
                if filters.sort_order == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(Course.created_at.desc())

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Apply pagination
            query = query.offset(skip).limit(limit)

            # Execute query
            result = await self.db.execute(query)
            courses = result.scalars().all()

            return {
                "courses": courses,
                "total": total,
                "skip": skip,
                "limit": limit
            }

        except Exception as e:
            self.logger.error(f"Error getting courses: {e}")
            return {
                "courses": [],
                "total": 0,
                "skip": skip,
                "limit": limit
            }

    @log_performance
    async def update_course(self, course_id: str, course_data: CourseUpdate, instructor_id: str) -> Course:
        """Update course"""
        try:
            course = await self.get_course_by_id(course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found"
                )

            # Check if user is the instructor
            if course.instructor_id != instructor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to update this course"
                )

            # Update fields
            update_data = course_data.model_dump(exclude_unset=True)

            # Regenerate slug if title changed
            if "title" in update_data:
                new_slug = self._generate_slug(update_data["title"])
                if new_slug != course.slug:
                    existing_course = await self.get_course_by_slug(new_slug)
                    if existing_course and existing_course.id != course_id:
                        new_slug = f"{new_slug}-{uuid.uuid4().hex[:8]}"
                    update_data["slug"] = new_slug

            await self.db.execute(
                update(Course)
                .where(Course.id == course_id)
                .values(**update_data)
            )

            await self.db.commit()
            await self.db.refresh(course)

            self.logger.info(f"Course updated: {course.title}")
            return course

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to update course: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course update failed: {str(e)}"
            )

    @log_performance
    async def delete_course(self, course_id: str, instructor_id: str) -> bool:
        """Delete course"""
        try:
            course = await self.get_course_by_id(course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found"
                )

            # Check if user is the instructor
            if course.instructor_id != instructor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete this course"
                )

            await self.db.execute(
                delete(Course).where(Course.id == course_id)
            )

            await self.db.commit()

            self.logger.info(f"Course deleted: {course.title}")
            return True

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to delete course: {e}")
            return False

    @log_performance
    async def publish_course(self, course_id: str, instructor_id: str) -> Course:
        """Publish course"""
        try:
            course = await self.get_course_by_id(course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found"
                )

            if course.instructor_id != instructor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to publish this course"
                )

            await self.db.execute(
                update(Course)
                .where(Course.id == course_id)
                .values(
                    is_published=True,
                    published_at=func.now()
                )
            )

            await self.db.commit()
            await self.db.refresh(course)

            self.logger.info(f"Course published: {course.title}")
            return course

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to publish course: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course publish failed: {str(e)}"
            )

    @log_performance
    async def increment_enrollment_count(self, course_id: str) -> None:
        """Increment course enrollment count"""
        try:
            await self.db.execute(
                update(Course)
                .where(Course.id == course_id)
                .values(enrollment_count=Course.enrollment_count + 1)
            )
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to increment enrollment count: {e}")

    @log_performance
    async def update_course_rating(self, course_id: str, new_rating: float) -> None:
        """Update course average rating"""
        try:
            # Get current course data
            course = await self.get_course_by_id(course_id)
            if not course:
                return

            # Calculate new average rating
            total_ratings = course.total_ratings + 1
            current_total = course.average_rating * course.total_ratings
            new_average = (current_total + new_rating) / total_ratings

            await self.db.execute(
                update(Course)
                .where(Course.id == course_id)
                .values(
                    average_rating=new_average,
                    total_ratings=total_ratings
                )
            )
            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to update course rating: {e}")

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = slug.strip('-')
        return slug
