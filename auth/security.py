import bcrypt

def hash_password(password: str) -> str:
    # Hash the password using bcrypt directly
    salt = bcrypt.gensalt()
    # bcrypt.hashpw expects bytes, so we encode the string to utf-8 first
    # and then decode the hashed result back to a string for storage
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    # Verify the plain text password against the hashed one
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "CHANGE_THIS_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
