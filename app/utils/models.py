from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class Register(BaseModel):
    password:str
    email:EmailStr

class Login(BaseModel):
    username:EmailStr
    password:str

class LoginResponse(BaseModel):
    success:bool
    access_token:str
    token_type:str
    message:Optional[str]=None

class UserUpdate(BaseModel):
    email: Optional[EmailStr]=None
    password:Optional[str] = None

class TokenPayload(BaseModel):
    exp:datetime
    userId:str

class GitToken(BaseModel):
    access_token:str

class GitUser(BaseModel):
    id:int
    email: Optional[EmailStr] = None

    class Config:
        from_attributes=True
        
class GenericResponse(BaseModel):
    success:bool
    message:str

class MailLink(BaseModel):
    email: EmailStr

class PassReset(BaseModel):
    password:str

class NewNote(BaseModel):  
    title :str
    content:str
    tags:list

class EditNote(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list] = None
    is_archived: Optional[bool]=False


class GetResponse(BaseModel):
    data: list | dict
    success: bool

class Note(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]
    is_archived: bool
    last_edited: datetime
    
class GetNotes(BaseModel):
    data: list[Note]
    success:bool