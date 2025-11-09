"""
AI Content Generator Service for EduVerse

Provides AI-powered content generation using OpenAI GPT models
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import get_logger, log_performance


class QuizQuestion(BaseModel):
    """Quiz question model"""
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    difficulty: str


class CourseContent(BaseModel):
    """Generated course content model"""
    title: str
    description: str
    learning_objectives: List[str]
    content_outline: List[Dict[str, Any]]
    prerequisites: List[str]
    target_audience: str
    estimated_duration: int


class PersonalizedRecommendation(BaseModel):
    """Personalized learning recommendation"""
    course_id: str
    reason: str
    confidence_score: float
    learning_path: List[str]


class AIContentGenerator:
    """AI-powered content generation service"""

    def __init__(self):
        self.logger = get_logger("ai_content_generator")
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        else:
            self.logger.warning("OpenAI API key not configured")

    @log_performance
    async def generate_course_content(
        self,
        topic: str,
        difficulty: str = "intermediate",
        target_audience: str = "professionals",
        duration_hours: int = 10
    ) -> CourseContent:
        """Generate comprehensive course content using AI"""
        try:
            prompt = f"""
            Generate a comprehensive course outline for: {topic}

            Requirements:
            - Difficulty level: {difficulty}
            - Target audience: {target_audience}
            - Estimated duration: {duration_hours} hours

            Please provide a JSON response with the following structure:
            {{
                "title": "Course Title",
                "description": "Detailed course description (200-300 words)",
                "learning_objectives": ["Objective 1", "Objective 2", "Objective 3", ...],
                "content_outline": [
                    {{
                        "module": "Module Title",
                        "topics": ["Topic 1", "Topic 2", "Topic 3"],
                        "duration_hours": 2,
                        "description": "Module description"
                    }}
                ],
                "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
                "target_audience": "Detailed audience description",
                "estimated_duration": {duration_hours}
            }}
            """

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert course designer and educator. Generate high-quality, engaging course content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )

            content_json = response.choices[0].message.content.strip()
            content_data = json.loads(content_json)

            return CourseContent(**content_data)

        except Exception as e:
            self.logger.error(f"Failed to generate course content: {e}")
            # Return fallback content
            return CourseContent(
                title=f"Introduction to {topic}",
                description=f"A comprehensive course on {topic} designed for {target_audience}.",
                learning_objectives=[
                    f"Understand the fundamentals of {topic}",
                    f"Apply {topic} concepts in practical scenarios",
                    f"Master advanced techniques in {topic}"
                ],
                content_outline=[
                    {
                        "module": f"Basics of {topic}",
                        "topics": [f"Introduction to {topic}", "Key Concepts", "Foundations"],
                        "duration_hours": duration_hours // 3,
                        "description": f"Fundamental concepts and principles of {topic}"
                    }
                ],
                prerequisites=["Basic computer skills"],
                target_audience=target_audience,
                estimated_duration=duration_hours
            )

    @log_performance
    async def generate_quiz_questions(
        self,
        topic: str,
        difficulty: str = "intermediate",
        num_questions: int = 10
    ) -> List[QuizQuestion]:
        """Generate quiz questions for a topic"""
        try:
            prompt = f"""
            Generate {num_questions} multiple-choice quiz questions for: {topic}

            Requirements:
            - Difficulty: {difficulty}
            - Each question must have 4 options (A, B, C, D)
            - Only one correct answer per question
            - Include detailed explanation for each answer
            - Questions should test understanding and application

            Return as JSON array with this structure:
            [
                {{
                    "question": "Question text here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "Detailed explanation why this is correct",
                    "difficulty": "{difficulty}"
                }}
            ]
            """

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educator creating high-quality assessment questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.6
            )

            questions_json = response.choices[0].message.content.strip()
            questions_data = json.loads(questions_json)

            return [QuizQuestion(**q) for q in questions_data]

        except Exception as e:
            self.logger.error(f"Failed to generate quiz questions: {e}")
            # Return sample questions
            return [
                QuizQuestion(
                    question=f"What is the most important concept in {topic}?",
                    options=["Option A", "Option B", "Option C", "Option D"],
                    correct_answer=0,
                    explanation=f"This is the fundamental concept in {topic}",
                    difficulty=difficulty
                )
            ]

    @log_performance
    async def generate_course_summary(
        self,
        course_content: str,
        max_length: int = 200
    ) -> str:
        """Generate a concise course summary"""
        try:
            prompt = f"""
            Create a compelling course summary (maximum {max_length} characters) for the following content:

            {course_content}

            The summary should:
            - Be engaging and informative
            - Highlight key learning outcomes
            - Include the target audience
            - Be suitable for course catalog display
            """

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a marketing copywriter specializing in educational content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            self.logger.error(f"Failed to generate course summary: {e}")
            return f"Comprehensive course on {course_content[:50]}..."

    @log_performance
    async def personalize_learning_path(
        self,
        user_profile: Dict[str, Any],
        completed_courses: List[str],
        interests: List[str]
    ) -> List[PersonalizedRecommendation]:
        """Generate personalized course recommendations"""
        try:
            prompt = f"""
            Based on the following user profile, recommend the next best courses:

            User Profile:
            - Experience Level: {user_profile.get('experience_level', 'beginner')}
            - Interests: {', '.join(interests)}
            - Completed Courses: {', '.join(completed_courses)}
            - Learning Goals: {user_profile.get('goals', 'General skill development')}

            Provide 5 course recommendations in JSON format:
            [
                {{
                    "course_id": "course_identifier",
                    "reason": "Why this course is recommended",
                    "confidence_score": 0.85,
                    "learning_path": ["Step 1", "Step 2", "Step 3"]
                }}
            ]

            Focus on logical progression and skill building.
            """

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert learning path designer and career counselor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )

            recommendations_json = response.choices[0].message.content.strip()
            recommendations_data = json.loads(recommendations_json)

            return [PersonalizedRecommendation(**r) for r in recommendations_data]

        except Exception as e:
            self.logger.error(f"Failed to generate personalized recommendations: {e}")
            return []

    @log_performance
    async def analyze_learning_pattern(
        self,
        user_id: str,
        learning_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user learning patterns and provide insights"""
        try:
            prompt = f"""
            Analyze the following learning history and provide insights:

            Learning History:
            {json.dumps(learning_history, indent=2)}

            Provide analysis in JSON format:
            {{
                "strengths": ["Strength 1", "Strength 2"],
                "weaknesses": ["Weakness 1", "Weakness 2"],
                "learning_style": "visual/auditory/kinesthetic/reading",
                "recommended_study_time": "2 hours daily",
                "suggested_improvements": ["Improvement 1", "Improvement 2"],
                "next_skill_focus": "Recommended next skill to learn"
            }}
            """

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a learning analytics expert analyzing student performance data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.6
            )

            analysis_json = response.choices[0].message.content.strip()
            return json.loads(analysis_json)

        except Exception as e:
            self.logger.error(f"Failed to analyze learning pattern: {e}")
            return {
                "strengths": ["Consistent learning"],
                "weaknesses": ["Need more practice"],
                "learning_style": "mixed",
                "recommended_study_time": "1-2 hours daily",
                "suggested_improvements": ["Practice regularly"],
                "next_skill_focus": "Advanced topics"
            }

    @log_performance
    async def generate_adaptive_content(
        self,
        topic: str,
        user_performance: Dict[str, Any],
        difficulty_adjustment: str
    ) -> Dict[str, Any]:
        """Generate adaptive content based on user performance"""
        try:
            prompt = f"""
            Generate adaptive learning content based on user performance:

            Topic: {topic}
            User Performance: {json.dumps(user_performance)}
            Difficulty Adjustment: {difficulty_adjustment}

            Provide adaptive content in JSON format:
            {{
                "adjusted_difficulty": "intermediate",
                "additional_resources": ["Resource 1", "Resource 2"],
                "practice_exercises": ["Exercise 1", "Exercise 2"],
                "remedial_content": "Additional explanation if needed",
                "advanced_challenges": ["Challenge 1", "Challenge 2"],
                "next_topic_suggestion": "Suggested next topic"
            }}
            """

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an adaptive learning specialist creating personalized content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            content_json = response.choices[0].message.content.strip()
            return json.loads(content_json)

        except Exception as e:
            self.logger.error(f"Failed to generate adaptive content: {e}")
            return {
                "adjusted_difficulty": difficulty_adjustment,
                "additional_resources": ["Practice exercises"],
                "practice_exercises": ["Review key concepts"],
                "remedial_content": "Review fundamentals",
                "advanced_challenges": ["Apply concepts"],
                "next_topic_suggestion": "Related advanced topics"
            }


# Global instance
ai_content_generator = AIContentGenerator()
