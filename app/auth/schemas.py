import re
from typing import Self, Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator

from app.auth.utils import get_password_hash


class ReferralCodeModel(BaseModel):
    referral_code: Optional[str] = Field(description="Если есть реферальный код, введите его", default=None)
    model_config = ConfigDict(from_attributes=True)


class EmailModel(ReferralCodeModel):
    email: EmailStr = Field(description="Электронная почта")


class UserBase(EmailModel):
    phone_number: str = Field(description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    last_name: str = Field(min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов")

    @field_validator("phone_number")
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r"^\+\d{5,15}$", value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 5 до 15 цифр')
        return value


class SUserRegister(UserBase):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    confirm_password: str = Field(min_length=5, max_length=50, description="Повторите пароль")

    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        self.password = get_password_hash(self.password)  # хешируем пароль до сохранения в базе данных
        return self


class SUserAddDB(UserBase):
    password: str = Field(min_length=5, description="Пароль в формате HASH-строки")
    referrer_id: int


class SUserAuth(EmailModel):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")


class SUserInfo(UserBase):
    id: int = Field(description="Идентификатор пользователя")
