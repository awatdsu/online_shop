import email
from fastapi import APIRouter, Depends, HTTPException, Response, status

from backend.auth.schemas import UserRegisterSchema
from backend.users.dao_users import UsersDao

router = APIRouter(prefix="/auth")

@router.post("/register")
async def register_new_user(user_data: UserRegisterSchema):
    user = await UsersDao.find_one_or_none(username=user_data.username, email=user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    user_dict = user_data.model_dump()
    user_dict.pop("repeat_password")
    print(user_dict)
    #ДОБАВИТЬ ХЕШИРОВАНИЕ ПАРОЛЯ
    await UsersDao.add_new_user(**user_dict)
    return {'message': "Registration successfull"}