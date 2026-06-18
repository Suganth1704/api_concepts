from pydantic import BaseModel, ConfigDict, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from bson import ObjectId
from typing import Annotated

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


class AppUserIn(BaseModel):
    user_name: str = Field(..., min_length=2, max_length=50, description="Full name of the user")
    email: EmailStr = Field(..., description="Unique email address")
    password: str = Field(...,  min_length=8, description="Password (hashed before saving)")

class AppUserOut(BaseModel):
    id: PyObjectId = Field(alias="_id")
    user_name: str = Field(..., min_length=2, max_length=50, description="Full name of the user")
    email: EmailStr = Field(..., description="Unique email address")

    class Config:
        json_encoders = {ObjectId: str}
        validate_by_name = True
    
