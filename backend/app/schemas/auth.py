from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, email: str) -> str:
        return email.lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
