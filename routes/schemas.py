from pydantic import BaseModel


class User(BaseModel):
    username:str
    user_id:str
    Address:str
    Phone:int
    isActive:bool