from pydantic import BaseModel, Field, ConfigDict


class CreateReferralCode(BaseModel):
    action_time_day: int | None = Field(description="Количество дней которое будет действовать код")
    model_config = ConfigDict(from_attributes=True)

class ReferralCode(CreateReferralCode):
    code: str = Field(description="Реферальный код")

