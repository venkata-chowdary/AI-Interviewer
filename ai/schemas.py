from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Literal

class ResumeAnalysis(BaseModel):
    skills: List[str]
    experience_level: str
    years_of_experience: int
    summary: str

class QuestionEvaluation(BaseModel):
    question_id: str
    score: float
    feedback: str

class PerformanceReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strengts: List[str]
    weakness: List[str]
    suggestions: List[str]
    summary: str

class InterviewEvaluation(BaseModel):
    question_evaluations: List[QuestionEvaluation]
    overall_marks: float
    performance_report: PerformanceReport
    selected_status: Optional[Literal["selected", "rejected"]] = None
