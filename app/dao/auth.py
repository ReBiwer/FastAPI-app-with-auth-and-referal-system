from models.auth import User
from app.dao.base import BaseDAO
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger


class UsersDAO(BaseDAO):
    model = User
    async def find_one_or_none_by_id(self, data_id: int):
        try:
            query = (select(self.model)
                     .options(selectinload(self.model.referral_code))
                     .filter_by(id=data_id))
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {self.model.__name__} с ID {data_id} {'найдена' if record else 'не найдена'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {data_id}: {e}")
            raise
