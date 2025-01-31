from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)


class ResetPassword(BaseModel):
    model_config = ConfigDict(extra='forbid')
    login: str = Field(..., description="Логин")
    email: str = Field(..., description="Email")
