import asyncio
from sqlmodel import select
from db import async_session_factory
from models.interview import Interview, InterviewQuestionAttempt
import json

session_id = "f9e4dd6d-0cc1-42cd-97a6-246aff96173f"

async def check():
    async with async_session_factory() as session:
        interview = await session.get(Interview, session_id)
        print(f"Status: {interview.status}")
        print(f"Overall Marks: {interview.marks}")
        print(f"Report: {json.dumps(interview.performance_report, indent=2)}")
        
        attempts = await session.exec(select(InterviewQuestionAttempt).where(InterviewQuestionAttempt.session_id == session_id))
        print("\n--- Question Feedback ---")
        for attempt in attempts:
            print(f"Q: {attempt.question_id}")
            print(f"Answer: {attempt.answer_text}")
            print(f"Score: {attempt.score}")
            print(f"Feedback: {attempt.feedback}\n")

if __name__ == "__main__":
    asyncio.run(check())
