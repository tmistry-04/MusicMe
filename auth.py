# hash passwords, verify passwords, create/read JWT tokens
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# use bcrypt for password hashing
pwd_context = CryptContext(schemes=["bcrypt"])

SECRET_KEY = os.getenv("SECRET_KEY_JWT")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

# 2 password functions - hash and verify, 2 token functions - create and decode:

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# data will be a dictionary containing user email and an expiry 30 min from current time
def create_token(data):
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])