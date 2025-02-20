from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.dao.database import Base, str_uniq
from app.referral_system.models import ReferralCode


class User(Base):
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Связь один-ко-многим: один пользователь может иметь много рефералов
    referrals: Mapped[list['User']] = relationship('User', back_populates='referrer', remote_side="users.id")
    # Связь многие-к-одному: каждый реферал ссылается на одного реферера
    referrer: Mapped['User'] = relationship('User', back_populates='referrals', remote_side="users.id")
    # Связь один-к-одному с реферальным кодом
    referral_code: Mapped['ReferralCode'] = relationship('ReferralCode', back_populates='user', uselist=False)


    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
