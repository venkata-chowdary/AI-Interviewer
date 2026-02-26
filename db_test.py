from database import engine, Base
from models import ResumeMetadata

print("Connecting to database and creating tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
except Exception as e:
    print(f"Error creating tables: {e}")
