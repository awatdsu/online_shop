import os
import bcrypt
import jwt

from dotenv import load_dotenv

from datetime import datetime, timedelta, timezone

from backend.users.dao_users import UsersDao

load_dotenv()

# Hash a password using bcrypt
def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')

# Check if the provided password matches the stored password (hashed)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_password_bytes)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encode_jwt

async def authenticate_user(username: str, password: str):
    user = await UsersDao.find_one_or_none(username=username)
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        return False
    return user

