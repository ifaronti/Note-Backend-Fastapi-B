import jwt
from typing import Annotated
from datetime import datetime, timedelta, timezone
from ..utils.settings import Settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, Depends, HTTPException, status


settings = Settings()
token_scheme = OAuth2PasswordBearer(tokenUrl='api/auth/login')


the_except = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                           detail='Missing and or inaccurate parameters' 
                           )


def create_token(user_id:str, expiry:int):
    token_values = {"user_id":user_id}
    expire = datetime.now(timezone.utc) + timedelta(hours=expiry)
    token_values.update({"exp":expire})

    return jwt.encode(token_values, settings.JWT_ASHIRI, settings.ALGORITHM)

def verify_token(token:Annotated[str, Depends(token_scheme)], req:Request):
    try:
        payload = jwt.decode(token, settings.JWT_ASHIRI, settings.ALGORITHM)
        if not payload["user_id"]:
            raise the_except
    except jwt.exceptions.InvalidTokenError:
        raise the_except
    finally:
        req.state.user_id=payload["user_id"]
    return