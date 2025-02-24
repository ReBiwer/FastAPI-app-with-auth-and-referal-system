from datetime import datetime
from datetime import timedelta

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.dao.database import Base


class ReferralCode(Base):
    code: Mapped[str]
    action_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now() + timedelta(days=7))
    user_ud: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    user: Mapped["User"] = relationship("User", back_populates="referral_code")

    def __repr__(self):
        return f"{self.__class__.__name__}(code={self.code})"
