from datetime import datetime, timedelta
from sqlalchemy import text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.dao.database import Base, str_uniq


class User(Base):
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
