from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dao import UsersDAO
from app.auth.models import User
from app.auth.schemas import EmailModel
from app.auth.schemas import SUserAddDB
from app.auth.schemas import SUserAuth
from app.auth.schemas import SUserInfo
from app.auth.schemas import SUserRegister
from app.auth.schemas import ReferralCodeModel
from app.auth.utils import authenticate_user
from app.auth.utils import set_tokens
from app.auth.utils import check_referrer
from app.dependencies.auth_dep import check_refresh_token
from app.dependencies.auth_dep import get_current_admin_user
from app.dependencies.auth_dep import get_current_user
from app.dependencies.dao_dep import get_session_with_commit
from app.dependencies.dao_dep import get_session_without_commit
from app.exceptions import IncorrectEmailOrPasswordException
from app.exceptions import UserAlreadyExistsException
from app.exceptions import ReferralCodeNotFoundException

router = APIRouter()


@router.post("/register/")
async def register_user(user_data: SUserRegister, session: AsyncSession = Depends(get_session_with_commit)) -> dict:
    # Проверка существования пользователя
    user_dao = UsersDAO(session)

    existing_user = await user_dao.find_one_or_none(filters=EmailModel(email=user_data.email))
    if existing_user:
        raise UserAlreadyExistsException

    user_data_dict = user_data.model_dump()
    user_data_dict.pop("confirm_password", None)

    if user_data.referral_code:
        referrer = await check_referrer(user_data, session)
        if not referrer:
            raise ReferralCodeNotFoundException
        user_data_dict["referrer_id"] = referrer.id

    # Добавление пользователя
    await user_dao.add(values=SUserAddDB(**user_data_dict))

    return {"message": "Вы успешно зарегистрированы!"}


@router.post("/login/")
async def auth_user(
    response: Response, user_data: SUserAuth, session: AsyncSession = Depends(get_session_without_commit)
) -> dict:
    users_dao = UsersDAO(session)
    user = await users_dao.find_one_or_none(filters=EmailModel(email=user_data.email))

    if not (user and await authenticate_user(user=user, password=user_data.password)):
        raise IncorrectEmailOrPasswordException
    set_tokens(response, user.id)
    return {"ok": True, "message": "Авторизация успешна!"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("user_access_token")
    response.delete_cookie("user_refresh_token")
    return {"message": "Пользователь успешно вышел из системы"}


@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)) -> SUserInfo:
    return SUserInfo.model_validate(user_data)


@router.post("/refresh")
async def process_refresh_token(response: Response, user: User = Depends(check_refresh_token)):
    set_tokens(response, user.id)
    return {"message": "Токены успешно обновлены"}
