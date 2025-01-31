from fastapi import APIRouter, status, Depends, Request, Query
from ..utils.models import LoginResponse, Login, PassReset, GenericResponse, Register, MailLink
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from ..controllers.user import register, logon, send_link, reset_password, github_login
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




@router.post("/login/forgot", response_model=GenericResponse, status_code=status.HTTP_200_OK)
async def Email(email:MailLink):
    await send_link(email)
    return {
        "success":True,  
        "message":'Password reset link sent. Check your inbox. Link expires within an hour'
    }




@router.patch("/login/reset", dependencies=[Depends(verify_token)], response_model=GenericResponse, status_code=status.HTTP_200_OK)
async def Password_Reset(password:PassReset, req:Request):
    await reset_password(password, req=req)
    return {"message":"User updated successfully", "success":True}




@router.post('/login/git')
async def git_user(code:Annotated[str, Query()]):
    token:str = await github_login(code)
    if token == None:
        return {"success":False, 'message':'Github login failed'}
    
    return {
                "access_token":token, 
                "success":True, 
                "token_type":"Bearer", 
                "message":'Login successful'
            }