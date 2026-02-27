import requests
import time

url = "http://localhost:8000/upload-resume"
pdf_path = "venkata_immanni_full_stack_gen_ai_feb_2026.pdf"

print(f"Uploading {pdf_path}...")
with open(pdf_path, "rb") as f:
    files = {"file": (pdf_path, f, "application/pdf")}
    data = {"user_id": "test_user_456"}
    response = requests.post(url, files=files, data=data)

print(f"Response Status Code: {response.status_code}")
print(f"Response JSON: {response.json()}")

resume_id = response.json().get("resume_id")
if resume_id:
    print(f"Got resume_id: {resume_id}, waiting for background task to complete...")
    time.sleep(1)
