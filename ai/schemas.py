from pydantic import BaseModel
from typing import List

class ResumeAnalysis(BaseModel):
    skills: List[str]
    experience_level: str
    years_of_experience: int
    summary: str