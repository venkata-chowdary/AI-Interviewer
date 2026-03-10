from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class StartInterviewRequest(BaseModel):
    resume_id: str
    role: str
    difficulty_level: str
    duration: int


class RecentInterviewResponse(BaseModel):
    id: str
    role: str
    difficulty_level: str
    status: str
    score: Optional[float] = None
    selected_status: Optional[str] = None
    time_taken: Optional[int] = None
    created_at: datetime
    questions_total: int
    questions_answered: int
    progress_percent: int


class InterviewAttemptReportItem(BaseModel):
    question_id: str
    question_order: int
    question_text: Optional[str] = None
    max_score: Optional[float] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    time_taken: Optional[int] = None
    primary_skill: Optional[str] = None


class TechSkillScore(BaseModel):
    name: str
    score: float


class InterviewReportResponse(BaseModel):
    id: str
    role: str
    difficulty_level: str
    duration: Optional[int] = None
    status: str
    marks: Optional[float] = None
    selected_status: Optional[str] = None
    time_taken: Optional[int] = None
    created_at: datetime
    questions_total: int
    questions_answered: int
    progress_percent: int
    performance_report: Optional[dict] = None
    attempts: List[InterviewAttemptReportItem]
    tech_skill_radar: Optional[List[TechSkillScore]] = None
    top_tech_skills: Optional[List[TechSkillScore]] = None


class SubmitAnswerRequest(BaseModel):
    question_id: str
    answer_text: str
    time_taken: int

