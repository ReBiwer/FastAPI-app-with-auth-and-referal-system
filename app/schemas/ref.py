import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field
from pydantic import computed_field
from pydantic import field_validator

from app.models.auth import User


class CreateReferralCode(BaseModel):
    action_time_day: int | None = Field(description="Количество дней которое будет действовать код", exclude=True)
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    def action_time(self) -> datetime.datetime:
        return datetime.datetime.now() + datetime.timedelta(days=self.action_time_day)


class ReferralCodeInfo(CreateReferralCode):
    user_id: int
    code: str = Field(description="Реферальный код")


class DeleteReferralCode(BaseModel):
    code: str = Field(description="Реферальный код")
    model_config = ConfigDict(from_attributes=True)


class Referrer(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    referrals: list["Referrer"] | None = Field(exclude=True)

    @field_validator("referrals", mode="before")
    def validate_referrals(cls, value: list["User"] | None) -> list["Referrer"] | None:
        if value:
            validating_referrals = []
            for user in value:
                referral = Referrer(
                    first_name=user.first_name, last_name=user.last_name, email=user.email, referrals=user.referrals
                )
                validating_referrals.append(referral)
            return validating_referrals
        return None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


Referrer.model_rebuild()
