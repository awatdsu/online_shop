import bcrypt
from fastapi import Request

import jwt

from datetime import datetime, timedelta, timezone

from backend.settings import settings

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_password_bytes)

def generate_fingerprint(request: Request):
    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host
    return f"{user_agent}:{ip_address}"


def create_token(data: dict, expire_time_minutes: int) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_time_minutes)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, key=settings.jwt_settings.secret_key.get_secret_value(), algorithm=settings.jwt_settings.algorithm)
    return encode_jwt
