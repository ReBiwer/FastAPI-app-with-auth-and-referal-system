from datetime import datetime
from datetime import timezone

from app.dao.auth import UsersDAO
from fastapi import Depends
from fastapi import Request
from jose import ExpiredSignatureError
from jose import JWTError
from jose import jwt
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies.dao_dep import get_session_without_commit
from app.exceptions import NoJwtException
from app.exceptions import NoUserIdException
from app.exceptions import TokenExpiredException
from app.exceptions import TokenNoFound
from app.exceptions import UserNotFoundException


def get_access_token(request: Request) -> str:
    """Извлекаем access_token из кук."""
    # request.headers.get("Authroization")
    token = request.cookies.get("user_access_token")
    if not token:
        raise TokenNoFound
    return token


def get_refresh_token(request: Request) -> str:
    """Извлекаем refresh_token из кук."""
    token = request.cookies.get("user_refresh_token")
    if not token:
        raise TokenNoFound
    return token


async def check_refresh_token(
    token: str = Depends(get_refresh_token), session: AsyncSession = Depends(get_session_without_commit)
) -> User:
    """Проверяем refresh_token и возвращаем пользователя."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise NoJwtException

        user = await UsersDAO(session).find_one_or_none_by_id(data_id=int(user_id))
        if not user:
            raise NoJwtException

        return user
    except JWTError:
        raise NoJwtException


async def get_current_user(
    token: str = Depends(get_access_token), session: AsyncSession = Depends(get_session_without_commit)
) -> User:
    """Проверяем access_token и возвращаем пользователя."""
    try:
        # Декодируем токен
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError:
        # Общая ошибка для токенов
        raise NoJwtException

    expire: str = payload.get("exp")
    try:
        expire_sec = int(expire)
    except ValueError:
        raise TokenExpiredException
    expire_time = datetime.fromtimestamp(expire_sec, tz=timezone.utc)
    if expire_time < datetime.now(timezone.utc):
        raise TokenExpiredException

    str_user_id: str = payload.get("sub")
    try:
        user_id = int(str_user_id)
    except ValueError:
        raise NoUserIdException

    user = await UsersDAO(session).find_one_or_none_by_id(data_id=user_id)
    if not user:
        raise UserNotFoundException
    return user
