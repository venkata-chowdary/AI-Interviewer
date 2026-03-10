from pydantic import BaseModel, ConfigDict, Field
from typing import List, Literal


class ResumeAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skills: List[str] = Field(default_factory=list, max_length=100)
    experience_level: str
    years_of_experience: int = Field(ge=0, le=80)
    summary: str = Field(min_length=1, max_length=2500)


class QuestionEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str = Field(min_length=1, max_length=128)
    score: float = Field(ge=0, le=100)
    feedback: str = Field(min_length=1, max_length=4000)


class InterviewDimensions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    technical_depth: float = Field(ge=0, le=100)
    communication: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=100)


class PerformanceReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strengts: List[str] = Field(default_factory=list, max_length=20)
    weakness: List[str] = Field(default_factory=list, max_length=20)
    suggestions: List[str] = Field(default_factory=list, max_length=20)
    summary: str = Field(min_length=1, max_length=2500)


class InterviewEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_evaluations: List[QuestionEvaluation] = Field(default_factory=list, max_length=300)
    overall_marks: float = Field(ge=0, le=100)
    performance_report: PerformanceReport
    selected_status: Literal["selected", "rejected"]
    dimensions: InterviewDimensions
