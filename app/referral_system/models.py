from datetime import datetime, timedelta
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.dao.database import Base
from app.auth.models import User


class ReferralCode(Base):
    code: Mapped[str]
    action_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now() + timedelta(days=7))
    user_ud: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    user: Mapped['User'] = relationship("User", back_populates="referral_code")

    def __repr__(self):
        return f"{self.__class__.__name__}(code={self.code})"
