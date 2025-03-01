from app.models.auth import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.dao.base import BaseDAO


class UsersDAO(BaseDAO):
    model = User

    def _get_query_find_one(self, data_id):
        return select(self.model).options(selectinload(self.model.referral_code)).filter_by(id=data_id)