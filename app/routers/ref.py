import datetime

from dao.ref import ReferralCodeDAO
from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from models.auth import User
from schemas.ref import CreateReferralCode
from schemas.ref import DeleteReferralCode
from schemas.ref import ReferralCodeInfo
from schemas.ref import Referrer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from utils.ref import create_get_ref_code
from utils.ref import send_code_to_mail

from app.dependencies.auth_dep import get_current_user
from app.dependencies.dao_dep import get_session_with_commit
from app.exceptions import RefCodeNotFoundException

router = APIRouter()


@router.post("/create/")
async def create_ref_code(
    data: CreateReferralCode,
    session: AsyncSession = Depends(get_session_with_commit),
    user_data: User = Depends(get_current_user),
) -> ReferralCodeInfo:
    new_code = create_get_ref_code()
    ref_code = ReferralCodeInfo(code=new_code, action_time_day=data.action_time_day, user_id=user_data.id)
    ref_code_dao = ReferralCodeDAO(session)
    await ref_code_dao.add(ref_code)
    return ref_code


@router.delete("/delete/")
async def delete_ref_code(code: DeleteReferralCode, session: AsyncSession = Depends(get_session_with_commit)) -> dict:
    ref_code_dao = ReferralCodeDAO(session)
    try:
        await ref_code_dao.delete(code)
        return {"status_code": 204, "success": True, "description": f"referral code {code.code} deleted"}
    except SQLAlchemyError:
        raise RefCodeNotFoundException


@router.get("/get_on_mail/")
async def get_ref_code(background_tasks: BackgroundTasks, user_data: User = Depends(get_current_user)) -> dict:
    action_time_code = user_data.referral_code.action_time - datetime.datetime.now()
    ref_code = ReferralCodeInfo(
        code=user_data.referral_code.code, action_time_day=action_time_code.days, user_id=user_data.id
    )
    send_code_to_mail(user_data, ref_code, background_tasks)
    return {"message": "email has been sent"}


@router.get("/get_all_refers/")
async def get_all_refers(
    user_data: User = Depends(get_current_user),
) -> Referrer | dict:
    referrer = Referrer(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        referrals=user_data.referrals,
    )
    if referrer.referrals:
        return referrer
    return {"message": "You don't have any referrals"}
