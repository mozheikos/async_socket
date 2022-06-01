from pydantic import BaseModel
from typing import Optional, Union


class User(BaseModel):
    login: str
    password: Optional[str]


class Response(BaseModel):
    status: int
    message: str


class Message(BaseModel):
    sender: str
    recipient: str
    message: str


class Request(BaseModel):
    user: User
    to: Optional[User]
    action: str
    message: Optional[Union[str, Message]]