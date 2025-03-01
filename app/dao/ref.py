from app.models import ReferralCode

from app.dao.base import BaseDAO


class ReferralCodeDAO(BaseDAO):
    model = ReferralCode
