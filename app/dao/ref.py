from app.models.ref import ReferralCode

from app.dao.base import BaseDAO


class ReferralCodeDAO(BaseDAO):
    model = ReferralCode
