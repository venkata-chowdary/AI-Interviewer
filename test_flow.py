import time
import requests
from auth.security import create_access_token

BASE_URL = "http://localhost:8000"
RESUME_ID = "19af57d6-8414-40c5-a2ec-939c5b282e5b"

def run_test():
    print("Generating mock auth token...")
    token = create_access_token({"sub": "test_user_123"})
    headers = {"Authorization": f"Bearer {token}"}
    
    print("1. Starting interview...")
    payload = {
        "resume_id": RESUME_ID,
        "role": "frontend",
        "difficulty_level": "medium",
        "duration": 10
    }
    
    response = requests.post(f"{BASE_URL}/api/interview/start", json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Failed to start interview: {response.text}")
        return
        
    data = response.json()
    session_id = data["session_id"]
    print(f"Interview started! Session ID: {session_id}")
    
    is_completed = False
    question_count = 0
    
    while not is_completed:
        print(f"\n--- Fetching question {question_count + 1} ---")
        q_resp = requests.get(f"{BASE_URL}/api/interview/{session_id}/next-question", headers=headers)
        q_data = q_resp.json()
        
        if q_data.get("completed"):
            print("Interview marked as completed by GET endpoint!")
            is_completed = True
            break
            
        question = q_data.get("question")
        if not question:
            print("No question found in response", q_data)
            break
            
        print(f"Question: {question['question_text']}")
        
        answer_payload = {
            "question_id": question["id"],
            "answer_text": f"This is my test answer. I would evaluate this by making sure it uses React properly and avoids prop drilling by leveraging context.",
            "time_taken": 30
        }
        
        print(f"> Submitting answer for Q{question_count + 1}...")
        a_resp = requests.post(f"{BASE_URL}/api/interview/{session_id}/answer", json=answer_payload, headers=headers)
        if a_resp.status_code != 200:
            print(f"Failed to submit answer: {a_resp.text}")
            break
            
        a_data = a_resp.json()
        print(f"Answer response: {a_data}")
        
        if a_data.get("is_completed"):
            print("Answer endpoint stated interview is completed. Background evaluation should trigger on the server.")
            is_completed = True
            break
            
        question_count += 1
        
    print("\n--- Wait for evaluation to finish on the server ---")
    print("Wait 15 seconds for LLM logic to complete...")
    time.sleep(15)
    
    print("\n--- Test finished! Please check server logs for DB updates! ---")

if __name__ == "__main__":
    run_test()
