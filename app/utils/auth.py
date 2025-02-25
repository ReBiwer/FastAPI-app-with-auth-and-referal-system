from datetime import datetime
from datetime import timedelta
from datetime import timezone

from dao.auth import UsersDAO
from fastapi.responses import Response
from jose import jwt
from models.auth import User
from passlib.context import CryptContext
from schemas.auth import ReferralCodeModel
from schemas.auth import SUserRegister
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings


def create_tokens(data: dict) -> dict:
    # Текущее время в UTC
    now = datetime.now(timezone.utc)

    # AccessToken - 30 минут
    access_expire = now + timedelta(days=1)
    access_payload = data.copy()
    access_payload.update({"exp": int(access_expire.timestamp()), "type": "access"})
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # RefreshToken - 7 дней
    refresh_expire = now + timedelta(days=7)
    refresh_payload = data.copy()
    refresh_payload.update({"exp": int(refresh_expire.timestamp()), "type": "refresh"})
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {"access_token": access_token, "refresh_token": refresh_token}


async def authenticate_user(user, password):
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        return None
    return user


def set_tokens(response: Response, user_id: int):
    new_tokens = create_tokens(data={"sub": str(user_id)})
    access_token = new_tokens.get("access_token")
    refresh_token = new_tokens.get("refresh_token")

    response.set_cookie(key="user_access_token", value=access_token, httponly=True, secure=True, samesite="lax")

    response.set_cookie(key="user_refresh_token", value=refresh_token, httponly=True, secure=True, samesite="lax")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def check_referrer(user_info: SUserRegister, session: AsyncSession) -> User | None:
    ref_code = ReferralCodeModel(referral_code=user_info.referral_code)
    user_dao = UsersDAO(session)
    return await user_dao.find_one_or_none(ref_code)
