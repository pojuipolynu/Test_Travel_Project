from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str

class SignInRequest(BaseModel):
    email: str
    password: str