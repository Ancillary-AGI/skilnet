"""
Advanced AI Service with Multi-Modal Content Generation and Intelligent Tutoring
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import numpy as np
import torch
import transformers
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification,
    pipeline, BlipProcessor, BlipForConditionalGeneration
)
import openai
import anthropic
from diffusers import StableDiffusionPipeline, AudioLDMPipeline
import cv2
import librosa
import soundfile as sf
from PIL import Image
import base64
import io
import aiohttp
import asyncpg
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

logger = logging.getLogger(__name__)


class AIModelType(str, Enum):
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    AUDIO_GENERATION = "audio_generation"
    VIDEO_GENERATION = "video_generation"
    MULTIMODAL = "multimodal"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    TRANSLATION = "translation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CONTENT_MODERATION = "content_moderation"


class ContentDifficulty(str, Enum):
    ELEMENTARY = "elementary"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    PROFESSIONAL = "professional"


class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MULTIMODAL = "multimodal"


@dataclass
class AIGenerationRequest:
    content_type: str
    subject: str
    topic: str
    difficulty: ContentDifficulty
    learning_style: LearningStyle
    duration_minutes: int
    language: str
    accessibility_requirements: List[str]
    user_preferences: Dict[str, Any]
    context: Dict[str, Any]


@dataclass
class GeneratedContent:
    content_id: str
    content_type: str
    title: str
    description: str
    content_data: Dict[str, Any]
    metadata: Dict[str, Any]
    quality_score: float
    generation_time_seconds: float
    model_used: str
    created_at: datetime


class AdvancedAIService:
    """Comprehensive AI service for content generation and intelligent tutoring"""
    
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.executor = ThreadPoolExecutor(max_workers=mp.cpu_count())
        
        # API clients
        self.openai_client = None
        self.anthropic_client = None
        
        # Model configurations
        self.model_configs = {
            "text_generation": {
                "primary": "microsoft/DialoGPT-large",
                "fallback": "microsoft/DialoGPT-medium",
                "creative": "EleutherAI/gpt-neo-2.7B"
            },
            "image_generation": {
                "primary": "runwayml/stable-diffusion-v1-5",
                "artistic": "stabilityai/stable-diffusion-2-1",
                "realistic": "stabilityai/stable-diffusion-xl-base-1.0"
            },
            "audio_generation": {
                "primary": "cvssp/audioldm-s-full-v2",
                "music": "facebook/musicgen-medium",
                "speech": "microsoft/speecht5_tts"
            },
            "multimodal": {
                "vision": "Salesforce/blip-image-captioning-large",
                "vqa": "dandelin/vilt-b32-finetuned-vqa"
            }
        }
    
    async def initialize(self):
        """Initialize all AI models and services"""
        try:
            logger.info("Initializing Advanced AI Service...")
            
            # Initialize API clients
            await self._initialize_api_clients()
            
            # Load core models
            await self._load_core_models()
            
            # Initialize specialized pipelines
            await self._initialize_pipelines()
            
            # Warm up models
            await self._warm_up_models()
            
            logger.info("Advanced AI Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            # Initialize fallback models
            await self._initialize_fallback_models()
    
    async def generate_complete_lesson(
        self, 
        request: AIGenerationRequest
    ) -> Dict[str, Any]:
        """Generate a complete lesson with all components"""
        
        start_time = datetime.now()
        lesson_id = f"lesson_{int(start_time.timestamp())}"
        
        try:
            # Generate lesson structure
            lesson_structure = await self._generate_lesson_structure(request)
            
            # Generate content for each component
            components = {}
            
            # Text content
            if request.learning_style in [LearningStyle.READING_WRITING, LearningStyle.MULTIMODAL]:
                components['text'] = await self._generate_text_content(request, lesson_structure)
            
            # Visual content
            if request.learning_style in [LearningStyle.VISUAL, LearningStyle.MULTIMODAL]:
                components['images'] = await self._generate_visual_content(request, lesson_structure)
                components['diagrams'] = await self._generate_diagrams(request, lesson_structure)
            
            # Audio content
            if request.learning_style in [LearningStyle.AUDITORY, LearningStyle.MULTIMODAL]:
                components['audio'] = await self._generate_audio_content(request, lesson_structure)
                components['narration'] = await self._generate_narration(request, lesson_structure)
            
            # Interactive content
            if request.learning_style in [LearningStyle.KINESTHETIC, LearningStyle.MULTIMODAL]:
                components['interactive'] = await self._generate_interactive_content(request, lesson_structure)
                components['simulations'] = await self._generate_simulations(request, lesson_structure)
            
            # VR/AR content
            if 'vr_enabled' in request.user_preferences:
                components['vr_scenes'] = await self._generate_vr_content(request, lesson_structure)
            
            if 'ar_enabled' in request.user_preferences:
                components['ar_objects'] = await self._generate_ar_content(request, lesson_structure)
            
            # Assessment content
            components['quizzes'] = await self._generate_quiz_content(request, lesson_structure)
            components['assignments'] = await self._generate_assignment_content(request, lesson_structure)
            
            # Accessibility enhancements
            if request.accessibility_requirements:
                components['accessibility'] = await self._generate_accessibility_content(
                    request, components
                )
            
            # Generate lesson metadata
            metadata = await self._generate_lesson_metadata(request, components)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'lesson_id': lesson_id,
                'title': lesson_structure['title'],
                'description': lesson_structure['description'],
                'structure': lesson_structure,
                'components': components,
                'metadata': metadata,
                'generation_time_seconds': generation_time,
                'quality_score': await self._calculate_quality_score(components),
                'created_at': start_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate complete lesson: {e}")
            return await self._generate_fallback_lesson(request)
    
    async def generate_adaptive_content(
        self, 
        user_id: str,
        current_performance: Dict[str, Any],
        learning_history: List[Dict[str, Any]],
        target_skills: List[str]
    ) -> Dict[str, Any]:
        """Generate adaptive content based on user performance and history"""
        
        # Analyze user learning patterns
        learning_patterns = await self._analyze_learning_patterns(learning_history)
        
        # Determine optimal difficulty level
        optimal_difficulty = await self._calculate_optimal_difficulty(
            current_performance, learning_patterns
        )
        
        # Identify knowledge gaps
        knowledge_gaps = await self._identify_knowledge_gaps(
            current_performance, target_skills
        )
        
        # Generate personalized content
        adaptive_content = {}
        
        for gap in knowledge_gaps:
            content_request = AIGenerationRequest(
                content_type="adaptive_lesson",
                subject=gap['subject'],
                topic=gap['topic'],
                difficulty=optimal_difficulty,
                learning_style=learning_patterns['preferred_style'],
                duration_minutes=learning_patterns['optimal_duration'],
                language=learning_patterns['language'],
                accessibility_requirements=learning_patterns['accessibility_needs'],
                user_preferences=learning_patterns['preferences'],
                context={'knowledge_gap': gap, 'user_id': user_id}
            )
            
            gap_content = await self.generate_complete_lesson(content_request)
            adaptive_content[gap['topic']] = gap_content
        
        # Generate practice exercises
        practice_exercises = await self._generate_adaptive_exercises(
            knowledge_gaps, optimal_difficulty, learning_patterns
        )
        
        # Generate progress tracking
        progress_tracking = await self._generate_progress_tracking(
            target_skills, knowledge_gaps
        )
        
        return {
            'user_id': user_id,
            'adaptive_content': adaptive_content,
            'practice_exercises': practice_exercises,
            'progress_tracking': progress_tracking,
            'learning_patterns': learning_patterns,
            'optimal_difficulty': optimal_difficulty,
            'knowledge_gaps': knowledge_gaps,
            'generated_at': datetime.now().isoformat()
        }
    
    async def generate_realtime_tutoring_response(
        self,
        user_id: str,
        question: str,
        context: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate intelligent tutoring response in real-time"""
        
        start_time = datetime.now()
        
        try:
            # Analyze question intent and complexity
            question_analysis = await self._analyze_question(question, context)
            
            # Determine response strategy
            response_strategy = await self._determine_response_strategy(
                question_analysis, conversation_history, context
            )
            
            # Generate response based on strategy
            if response_strategy['type'] == 'direct_answer':
                response = await self._generate_direct_answer(question, context)
            elif response_strategy['type'] == 'socratic_method':
                response = await self._generate_socratic_response(question, context)
            elif response_strategy['type'] == 'visual_explanation':
                response = await self._generate_visual_explanation(question, context)
            elif response_strategy['type'] == 'step_by_step':
                response = await self._generate_step_by_step_solution(question, context)
            else:
                response = await self._generate_exploratory_response(question, context)
            
            # Add multimodal elements if beneficial
            if response_strategy['add_visuals']:
                response['visuals'] = await self._generate_supporting_visuals(question, response)
            
            if response_strategy['add_audio']:
                response['audio'] = await self._generate_audio_explanation(response['text'])
            
            if response_strategy['add_interactive']:
                response['interactive'] = await self._generate_interactive_demo(question, context)
            
            # Calculate confidence and provide alternatives
            confidence_score = await self._calculate_response_confidence(response, question_analysis)
            
            if confidence_score < 0.8:
                response['alternatives'] = await self._generate_alternative_explanations(question, context)
            
            # Generate follow-up questions
            response['follow_up_questions'] = await self._generate_follow_up_questions(
                question, response, context
            )
            
            # Track tutoring effectiveness
            await self._track_tutoring_interaction(
                user_id, question, response, context, confidence_score
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'response': response,
                'confidence_score': confidence_score,
                'response_strategy': response_strategy,
                'question_analysis': question_analysis,
                'response_time_ms': int(response_time * 1000),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate tutoring response: {e}")
            return await self._generate_fallback_response(question, context)
    
    async def generate_multimodal_content(
        self,
        content_request: Dict[str, Any],
        modalities: List[str]
    ) -> Dict[str, Any]:
        """Generate synchronized multimodal content"""
        
        content = {}
        
        # Generate base content
        base_content = await self._generate_base_content(content_request)
        
        # Generate for each requested modality
        for modality in modalities:
            if modality == 'text':
                content['text'] = await self._generate_text_from_base(base_content, content_request)
            elif modality == 'image':
                content['images'] = await self._generate_images_from_base(base_content, content_request)
            elif modality == 'audio':
                content['audio'] = await self._generate_audio_from_base(base_content, content_request)
            elif modality == 'video':
                content['video'] = await self._generate_video_from_base(base_content, content_request)
            elif modality == 'interactive':
                content['interactive'] = await self._generate_interactive_from_base(base_content, content_request)
            elif modality == 'vr':
                content['vr'] = await self._generate_vr_from_base(base_content, content_request)
            elif modality == 'ar':
                content['ar'] = await self._generate_ar_from_base(base_content, content_request)
        
        # Synchronize content across modalities
        synchronized_content = await self._synchronize_multimodal_content(content)
        
        # Generate accessibility alternatives
        accessibility_content = await self._generate_accessibility_alternatives(synchronized_content)
        
        return {
            'base_content': base_content,
            'multimodal_content': synchronized_content,
            'accessibility_content': accessibility_content,
            'synchronization_map': await self._create_synchronization_map(synchronized_content),
            'quality_metrics': await self._evaluate_multimodal_quality(synchronized_content)
        }
    
    async def generate_assessment_content(
        self,
        learning_objectives: List[str],
        difficulty_level: ContentDifficulty,
        assessment_type: str,
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive assessment content"""
        
        assessments = {}
        
        # Generate different types of assessments
        if assessment_type in ['quiz', 'all']:
            assessments['quiz'] = await self._generate_adaptive_quiz(
                learning_objectives, difficulty_level, user_preferences
            )
        
        if assessment_type in ['assignment', 'all']:
            assessments['assignment'] = await self._generate_project_assignment(
                learning_objectives, difficulty_level, user_preferences
            )
        
        if assessment_type in ['practical', 'all']:
            assessments['practical'] = await self._generate_practical_assessment(
                learning_objectives, difficulty_level, user_preferences
            )
        
        if assessment_type in ['peer_review', 'all']:
            assessments['peer_review'] = await self._generate_peer_review_assessment(
                learning_objectives, difficulty_level, user_preferences
            )
        
        # Generate VR/AR assessments if supported
        if user_preferences.get('vr_enabled'):
            assessments['vr_assessment'] = await self._generate_vr_assessment(
                learning_objectives, difficulty_level, user_preferences
            )
        
        if user_preferences.get('ar_enabled'):
            assessments['ar_assessment'] = await self._generate_ar_assessment(
                learning_objectives, difficulty_level, user_preferences
            )
        
        # Generate rubrics and scoring guides
        for assessment_name, assessment_data in assessments.items():
            assessment_data['rubric'] = await self._generate_assessment_rubric(
                assessment_data, learning_objectives
            )
            assessment_data['scoring_guide'] = await self._generate_scoring_guide(
                assessment_data, difficulty_level
            )
        
        # Generate automated feedback templates
        feedback_templates = await self._generate_feedback_templates(
            assessments, learning_objectives
        )
        
        return {
            'assessments': assessments,
            'feedback_templates': feedback_templates,
            'learning_objectives': learning_objectives,
            'difficulty_level': difficulty_level,
            'estimated_completion_time': await self._estimate_assessment_time(assessments),
            'accessibility_accommodations': await self._generate_assessment_accommodations(assessments)
        }
    
    # Helper methods for content generation
    async def _initialize_api_clients(self):
        """Initialize external API clients"""
        try:
            # OpenAI client
            if hasattr(self, 'openai_api_key'):
                self.openai_client = openai.AsyncOpenAI(api_key=self.openai_api_key)
            
            # Anthropic client
            if hasattr(self, 'anthropic_api_key'):
                self.anthropic_client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)
            
        except Exception as e:
            logger.warning(f"Failed to initialize some API clients: {e}")
    
    async def _load_core_models(self):
        """Load core AI models"""
        try:
            # Text generation model
            self.tokenizers['text'] = AutoTokenizer.from_pretrained(
                self.model_configs['text_generation']['primary']
            )
            self.models['text'] = AutoModelForCausalLM.from_pretrained(
                self.model_configs['text_generation']['primary'],
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
            
            # Image generation model
            self.models['image'] = StableDiffusionPipeline.from_pretrained(
                self.model_configs['image_generation']['primary'],
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
            
            # Multimodal model for image understanding
            self.models['vision_processor'] = BlipProcessor.from_pretrained(
                self.model_configs['multimodal']['vision']
            )
            self.models['vision'] = BlipForConditionalGeneration.from_pretrained(
                self.model_configs['multimodal']['vision']
            ).to(self.device)
            
            logger.info("Core models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load core models: {e}")
            await self._load_lightweight_models()
    
    async def _initialize_pipelines(self):
        """Initialize specialized AI pipelines"""
        try:
            # Text classification pipeline
            self.pipelines['sentiment'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if self.device == "cuda" else -1
            )
            
            # Translation pipeline
            self.pipelines['translation'] = pipeline(
                "translation",
                model="Helsinki-NLP/opus-mt-en-mul",
                device=0 if self.device == "cuda" else -1
            )
            
            # Speech-to-text pipeline
            self.pipelines['speech_to_text'] = pipeline(
                "automatic-speech-recognition",
                model="openai/whisper-base",
                device=0 if self.device == "cuda" else -1
            )
            
            # Text-to-speech pipeline
            self.pipelines['text_to_speech'] = pipeline(
                "text-to-speech",
                model="microsoft/speecht5_tts",
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info("AI pipelines initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize pipelines: {e}")
    
    async def _generate_lesson_structure(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Generate comprehensive lesson structure"""
        
        prompt = f"""
        Create a detailed lesson structure for:
        Subject: {request.subject}
        Topic: {request.topic}
        Difficulty: {request.difficulty}
        Duration: {request.duration_minutes} minutes
        Learning Style: {request.learning_style}
        Language: {request.language}
        
        Include:
        1. Learning objectives
        2. Prerequisites
        3. Lesson outline with timing
        4. Key concepts
        5. Activities and exercises
        6. Assessment methods
        7. Resources needed
        """
        
        if self.openai_client:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            structure_text = response.choices[0].message.content
        else:
            # Use local model
            structure_text = await self._generate_with_local_model(prompt)
        
        # Parse and structure the response
        return await self._parse_lesson_structure(structure_text, request)
    
    async def _generate_text_content(
        self, 
        request: AIGenerationRequest, 
        lesson_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive text content"""
        
        content_sections = {}
        
        for section in lesson_structure['sections']:
            section_prompt = f"""
            Write detailed educational content for:
            Section: {section['title']}
            Topic: {request.topic}
            Difficulty: {request.difficulty}
            Duration: {section['duration_minutes']} minutes
            
            Requirements:
            - Clear explanations with examples
            - Engaging and interactive tone
            - Appropriate for {request.difficulty} level
            - Include real-world applications
            - Add reflection questions
            """
            
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": section_prompt}],
                    temperature=0.7
                )
                section_content = response.choices[0].message.content
            else:
                section_content = await self._generate_with_local_model(section_prompt)
            
            content_sections[section['id']] = {
                'title': section['title'],
                'content': section_content,
                'word_count': len(section_content.split()),
                'reading_time_minutes': len(section_content.split()) / 200,  # Average reading speed
                'key_terms': await self._extract_key_terms(section_content),
                'complexity_score': await self._calculate_text_complexity(section_content)
            }
        
        return {
            'sections': content_sections,
            'total_word_count': sum(s['word_count'] for s in content_sections.values()),
            'estimated_reading_time': sum(s['reading_time_minutes'] for s in content_sections.values()),
            'language': request.language,
            'difficulty_level': request.difficulty
        }
    
    async def _generate_visual_content(
        self, 
        request: AIGenerationRequest, 
        lesson_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate visual content including images and diagrams"""
        
        visual_content = {}
        
        for section in lesson_structure['sections']:
            # Generate concept illustrations
            illustration_prompt = f"""
            Educational illustration for {request.subject}: {section['title']}.
            Style: Clean, educational, professional.
            Content: {section.get('key_concepts', [])}
            Difficulty: {request.difficulty}
            """
            
            try:
                if self.models.get('image'):
                    image = self.models['image'](
                        illustration_prompt,
                        num_inference_steps=50,
                        guidance_scale=7.5
                    ).images[0]
                    
                    # Convert to base64 for storage
                    buffer = io.BytesIO()
                    image.save(buffer, format='PNG')
                    image_base64 = base64.b64encode(buffer.getvalue()).decode()
                    
                    visual_content[f"{section['id']}_illustration"] = {
                        'type': 'illustration',
                        'title': f"Illustration for {section['title']}",
                        'image_data': image_base64,
                        'alt_text': await self._generate_alt_text(illustration_prompt),
                        'description': await self._generate_image_description(illustration_prompt)
                    }
            
            except Exception as e:
                logger.error(f"Failed to generate illustration: {e}")
                # Generate placeholder or use fallback
                visual_content[f"{section['id']}_illustration"] = await self._generate_placeholder_visual(section)
        
        return visual_content
    
    async def _generate_audio_content(
        self, 
        request: AIGenerationRequest, 
        lesson_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate audio content including narration and sound effects"""
        
        audio_content = {}
        
        for section in lesson_structure['sections']:
            # Generate narration script
            narration_script = await self._create_narration_script(section, request)
            
            try:
                if self.pipelines.get('text_to_speech'):
                    # Generate audio narration
                    audio_data = self.pipelines['text_to_speech'](narration_script)
                    
                    # Convert to base64 for storage
                    audio_base64 = base64.b64encode(audio_data['audio']).decode()
                    
                    audio_content[f"{section['id']}_narration"] = {
                        'type': 'narration',
                        'title': f"Narration for {section['title']}",
                        'audio_data': audio_base64,
                        'duration_seconds': len(audio_data['audio']) / audio_data['sampling_rate'],
                        'transcript': narration_script,
                        'language': request.language
                    }
            
            except Exception as e:
                logger.error(f"Failed to generate audio: {e}")
                # Store script for manual audio generation
                audio_content[f"{section['id']}_script"] = {
                    'type': 'script',
                    'title': f"Audio Script for {section['title']}",
                    'script': narration_script,
                    'estimated_duration': len(narration_script.split()) / 150  # Average speaking speed
                }
        
        return audio_content
    
    async def _generate_interactive_content(
        self, 
        request: AIGenerationRequest, 
        lesson_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate interactive content and activities"""
        
        interactive_content = {}
        
        for section in lesson_structure['sections']:
            # Generate interactive activities
            activities = []
            
            # Drag and drop activity
            if section.get('key_concepts'):
                drag_drop = await self._create_drag_drop_activity(section, request)
                activities.append(drag_drop)
            
            # Interactive simulation
            if section.get('processes') or section.get('systems'):
                simulation = await self._create_simulation_activity(section, request)
                activities.append(simulation)
            
            # Virtual lab experiment
            if request.subject in ['chemistry', 'physics', 'biology']:
                lab_experiment = await self._create_virtual_lab(section, request)
                activities.append(lab_experiment)
            
            # Interactive timeline
            if section.get('historical_events') or section.get('sequence'):
                timeline = await self._create_interactive_timeline(section, request)
                activities.append(timeline)
            
            # Gamified quiz
            quiz_game = await self._create_gamified_quiz(section, request)
            activities.append(quiz_game)
            
            interactive_content[section['id']] = {
                'section_title': section['title'],
                'activities': activities,
                'total_activities': len(activities),
                'estimated_time_minutes': sum(a.get('estimated_time', 5) for a in activities)
            }
        
        return interactive_content
    
    async def _generate_quiz_content(
        self, 
        request: AIGenerationRequest, 
        lesson_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive quiz content"""
        
        quiz_content = {}
        
        # Generate different types of questions
        question_types = [
            'multiple_choice',
            'true_false',
            'short_answer',
            'essay',
            'matching',
            'fill_in_blank',
            'ordering',
            'hotspot'  # For image-based questions
        ]
        
        for section in lesson_structure['sections']:
            section_quiz = {
                'section_id': section['id'],
                'section_title': section['title'],
                'questions': []
            }
            
            # Generate questions for each type
            for question_type in question_types:
                try:
                    questions = await self._generate_questions_by_type(
                        section, request, question_type, count=2
                    )
                    section_quiz['questions'].extend(questions)
                except Exception as e:
                    logger.error(f"Failed to generate {question_type} questions: {e}")
            
            # Add adaptive difficulty questions
            adaptive_questions = await self._generate_adaptive_questions(section, request)
            section_quiz['questions'].extend(adaptive_questions)
            
            # Generate explanations for each question
            for question in section_quiz['questions']:
                question['explanation'] = await self._generate_question_explanation(
                    question, section, request
                )
                question['hints'] = await self._generate_question_hints(question, request.difficulty)
            
            quiz_content[section['id']] = section_quiz
        
        # Generate final assessment
        final_quiz = await self._generate_comprehensive_quiz(lesson_structure, request)
        quiz_content['final_assessment'] = final_quiz
        
        return quiz_content
    
    async def _calculate_quality_score(self, components: Dict[str, Any]) -> float:
        """Calculate overall quality score for generated content"""
        
        scores = []
        
        # Text quality
        if 'text' in components:
            text_score = await self._evaluate_text_quality(components['text'])
            scores.append(text_score * 0.3)
        
        # Visual quality
        if 'images' in components:
            visual_score = await self._evaluate_visual_quality(components['images'])
            scores.append(visual_score * 0.2)
        
        # Interactive quality
        if 'interactive' in components:
            interactive_score = await self._evaluate_interactive_quality(components['interactive'])
            scores.append(interactive_score * 0.2)
        
        # Assessment quality
        if 'quizzes' in components:
            assessment_score = await self._evaluate_assessment_quality(components['quizzes'])
            scores.append(assessment_score * 0.15)
        
        # Accessibility score
        if 'accessibility' in components:
            accessibility_score = await self._evaluate_accessibility_quality(components['accessibility'])
            scores.append(accessibility_score * 0.15)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    async def cleanup(self):
        """Cleanup AI service resources"""
        try:
            # Clear model cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Close executor
            self.executor.shutdown(wait=True)
            
            logger.info("Advanced AI Service cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during AI service cleanup: {e}")


# Global AI service instance
ai_service = None

async def get_ai_service() -> AdvancedAIService:
    """Get AI service instance"""
    global ai_service
    if ai_service is None:
        ai_service = AdvancedAIService()
        await ai_service.initialize()
    return ai_service

async def close_ai_service():
    """Close AI service"""
    global ai_service
    if ai_service:
        await ai_service.cleanup()
        ai_service = None