from fastapi import APIRouter, status, Depends, Request
from ..utils.models import LoginResponse, Login, PassReset, GenericResponse, Register, MailLink
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from ..controllers.user import register, logon, send_link, reset_password
from ..dependencies.token import verify_token

router = APIRouter(
    prefix="/api/auth",
    tags=['Authentication']
)

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_202_ACCEPTED)
async def Signin(formdata:Annotated[Login, Depends(OAuth2PasswordRequestForm)]):
    token = await logon(formdata)
    return {"access_token":token, "success":True, "token_type":"Bearer"}

@router.post("/signup", response_model=GenericResponse, status_code=status.HTTP_201_CREATED)
async def Signup(body:Register):
    await register(body)
    return {"success":True, "message":"User created"}

@router.post("/login/forgot", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def Email(email:MailLink):
    token = await send_link(email)
    return {
            "success":True, 
            "access_token":token, 
            "token_type":"Bearer", 
            "message":'Password reset link sent. Check your inbox. Link expires within an hour'
        }

@router.patch("/login/reset", dependencies=[Depends(verify_token)], response_model=GenericResponse, status_code=status.HTTP_200_OK)
async def Reset_Password(password:PassReset, req:Request):
    await reset_password(password, req=req)
    return {"message":"User updated successfully", "success":True}