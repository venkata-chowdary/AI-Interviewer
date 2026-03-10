from __future__ import annotations

from models.interview import Interview


def build_resume_analysis_system_prompt(resume_text: str) -> str:
    return f"""
You are an expert technical recruiter and resume analyst.
Your task is to thoroughly analyze the provided candidate resume and reliably extract structured professional information.

Please extract the following data points with high accuracy:
1. Technical skills: Extract all relevant technical hard skills (e.g., programming languages, frameworks, databases, cloud providers, tools). Normalize the names where appropriate (e.g., "React.js" to "React").
2. Experience level: Categorize the candidate as strictly one of: 'entry', 'mid', or 'senior'.
   - Entry: 0-2 years
   - Mid: 3-5 years
   - Senior: 6+ years
3. Estimated years of experience: Calculate the total years of professional experience based on the dates provided in the work history. If explicit dates are missing, make your best conservative estimate based on the content. Return as an integer.
4. Professional summary: Write a concise, impactful 2-3 sentence summary highlighting the candidate's core expertise, primary domain, and standout achievements. Do not simply copy their summary verbatim; synthesize it into a recruiter-friendly format.

Resume text:
{resume_text}
""".strip()


def build_interview_evaluation_system_prompt(interview: Interview) -> str:
    return f"""
You are an expert technical interviewer evaluating a candidate's interview performance.
The candidate applied for a {interview.role} role at {interview.difficulty_level} difficulty.

You will be provided with a list of questions asked during the interview, the expected concepts, scoring guidelines, and the candidate's actual answers.

Your task is to:
1. Evaluate each individual answer and provide a score (out of the max_score) and constructive feedback.
2. Provide a single overall score for the entire interview out of 100.
3. Generate `performance_report` with exactly these keys and no extras:
   - strengts: list of key strengths
   - weakness: list of key weaknesses
   - suggestions: list of actionable improvement suggestions
   - summary: concise overall summary
4. Provide selected_status strictly as either "selected" or "rejected".
5. Populate the `dimensions` object with three numeric fields on a 0–100 scale:
   - technical_depth: depth and accuracy of the candidate's technical knowledge and reasoning.
   - communication: clarity and coherence of how the candidate communicated their thinking and answers.
   - confidence: your overall confidence in the candidate as a hire for this role based on the entire interview.

Return the result as a structured JSON object matching the InterviewEvaluation schema.
""".strip()

