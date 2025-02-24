from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.dao.database import Base
from app.dao.database import str_uniq
from models.ref import ReferralCode


class User(Base):
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True, default=None)

    # Связь один-ко-многим: один пользователь может иметь много рефералов
    referrals: Mapped[list["User"]] = relationship("User", back_populates="referrer", remote_side="User.id", foreign_keys="User.referrer_id")
    # Связь многие-к-одному: каждый реферал ссылается на одного реферера
    referrer: Mapped["User"] = relationship("User", back_populates="referrals")
    # Связь один-к-одному с реферальным кодом
    referral_code: Mapped["ReferralCode"] = relationship("ReferralCode", back_populates="user", uselist=False)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
