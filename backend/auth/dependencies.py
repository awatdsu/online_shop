import os
from dotenv import load_dotenv
from datetime import datetime, timezone

from backend.auth.schemas import TokenData
from backend.users.dao_users import UsersDao

load_dotenv()

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/oauth/token", auto_error=False)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    blocked_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Blocked"
    )

    try:
        payload = jwt.decode(jwt=token, key=os.getenv("SECRET_KEY"), algorithms=os.getenv("ALGORITHM"))
        username = payload.get("sub")
        if not username:
            raise credentials_exception
        
        expire = payload.get("exp")
        expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
        if (not expire) or (expire_time < datetime.now(timezone.utc)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Token is no longer valid!')
        
        token_data = TokenData(username=username)
    except InvalidTokenError as exc:
        raise credentials_exception from exc
    
    user = await UsersDao.find_one_or_none(username=token_data.username)

    if user is None:
        raise credentials_exception
    if user.is_blocked:
        raise blocked_exception
    
    return user

# async def generate_csrf_token(jwt_token: str)