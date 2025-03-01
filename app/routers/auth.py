from app.dao.auth import UsersDAO
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from app.models import User
from app.schemas.auth import EmailModel
from app.schemas.auth import SUserAddDB
from app.schemas.auth import SUserAuth
from app.schemas.auth import SUserInfo
from app.schemas.auth import SUserRegister
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.auth import verify_password
from app.utils.auth import get_referrer
from app.utils.auth import set_tokens

from app.dependencies.auth_dep import check_refresh_token
from app.dependencies.auth_dep import get_current_user
from app.dependencies.dao_dep import get_session_with_commit
from app.dependencies.dao_dep import get_session_without_commit
from app.exceptions import IncorrectEmailOrPasswordException
from app.exceptions import ReferralCodeNotFoundException
from app.exceptions import UserAlreadyExistsException

router = APIRouter()


@router.post("/register/")
async def register_user(user_data: SUserRegister, session: AsyncSession = Depends(get_session_with_commit)) -> dict:
    # Проверка существования пользователя
    user_dao = UsersDAO(session)

    existing_user = await user_dao.find_one_or_none(filters=EmailModel(email=user_data.email))
    if not existing_user:
        raise UserAlreadyExistsException

    user_data_dict = user_data.model_dump()
    user_data_dict.pop("confirm_password", None)

    if user_data.referral_code:
        referrer = await get_referrer(user_data, session)
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
    if not user:
        raise IncorrectEmailOrPasswordException
    if not verify_password(user_data.password, user.password):
        raise IncorrectEmailOrPasswordException
    set_tokens(response, user.id)
    # Authorization: Bearer токен_в_base64
    # return {"auth_token": "", "refresh_token": ""}
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
