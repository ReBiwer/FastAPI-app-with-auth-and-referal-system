from app.dao.base import BaseDAO
from app.referral_system.models import ReferralCode


class ReferralCodeDAO(BaseDAO):
    model = ReferralCode
