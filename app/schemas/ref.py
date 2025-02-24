from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field


class CreateReferralCode(BaseModel):
    action_time_day: int | None = Field(description="Количество дней которое будет действовать код")
    model_config = ConfigDict(from_attributes=True)


class ReferralCode(CreateReferralCode):
    code: str = Field(description="Реферальный код")


class Referrer(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    referrals: list["Referrer"]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


Referrer.model_rebuild()
