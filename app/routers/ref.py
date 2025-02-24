import datetime

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from models.auth import User
from app.dependencies.auth_dep import get_current_user
from app.dependencies.dao_dep import get_session_with_commit
from dao.ref import ReferralCodeDAO
from models.ref import ReferralCode
from schemas.ref import CreateReferralCode
from schemas.ref import ReferralCode
from schemas.ref import Referrer
from utils.ref import get_ref_code
from utils.ref import send_code_to_mail

router = APIRouter()


@router.post("create/")
async def create_ref_code(
    data: CreateReferralCode, session: AsyncSession = Depends(get_session_with_commit)
) -> ReferralCode:
    ref_code = ReferralCode(code=get_ref_code(), action_time_day=data.action_time_day)
    ref_code_dao = ReferralCodeDAO(session)
    await ref_code_dao.add(ref_code)
    return ref_code


@router.delete("delete/")
async def delete_ref_code(code: ReferralCode, session: AsyncSession = Depends(get_session_with_commit)):
    ref_code_dao = ReferralCodeDAO(session)
    await ref_code_dao.delete(code)
    return JSONResponse(status_code=204, content={"success": True, "description": f"referral code {code.code} deleted"})


@router.get("get_on_mail/")
async def get_ref_code(background_tasks: BackgroundTasks, user_data: User = Depends(get_current_user)):
    action_time_code = datetime.datetime.now() - user_data.referral_code.action_time
    ref_code = ReferralCode(code=user_data.referral_code.code, action_time_day=action_time_code.days)
    send_code_to_mail(user_data, ref_code, background_tasks)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})


@router.get("get_all_refers/")
async def get_all_refers(
    user_data: User = Depends(get_current_user),
) -> Referrer:
    return Referrer.model_validate(user_data)
