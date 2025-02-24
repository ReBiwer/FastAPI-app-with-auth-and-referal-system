from app.dao.base import BaseDAO
from models.ref import ReferralCode


class ReferralCodeDAO(BaseDAO):
    model = ReferralCode
