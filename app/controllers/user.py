from ..utils.models import Register, Login, LoginResponse, MailLink, GenericResponse, PassReset, GitUser
from ..dependencies.password_manager import verify_password, hash_password
from ..dependencies.token import create_token
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends, status, HTTPException, Request
import uuid
from ..dependencies.send_link import send_mail
from ..dependencies.git_oauth2 import git_user
from ..pyscopg_connect import Connect
from psycopg2 import InterfaceError, OperationalError

user_id = str(uuid.uuid1())

exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail='Invalid credentials provided')



async def register(form_data:Register):
    try:
        dbconnect = Connect().dbconnect()
        cursor = dbconnect.cursor()

        hashed_pass = hash_password(password=form_data.password)

        cursor.execute(f"""
            INSERT INTO "user" (id, email, password)
            VALUES(%s, %s, %s)
        """,(user_id, form_data.email, hashed_pass))
        
        dbconnect.commit()

    except InterfaceError as i:
        raise i
    except OperationalError as o:
        raise o 
    finally:
        cursor.close()
        dbconnect.close()






async def logon(formdata:Annotated[Login, Depends(OAuth2PasswordRequestForm)]):
    try:
        dbconnect = Connect().dbconnect()
        cursor = dbconnect.cursor()
        cursor.execute(f"""
                SELECT 
                    id, password 
                FROM
                    "user"
                WHERE
                    "user".email = '{formdata.username}'
            """
        )
        
        user = (cursor.fetchone())

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

        isMatch = verify_password(formdata.password, dict(user)["password"])

        if not isMatch:
            raise exception

        token = create_token(user_id=user["id"], expiry=2)
    except InterfaceError as i:
        raise i
    except OperationalError as o:
        raise o
    finally:
        cursor.close()
        dbconnect.close()
    return token






async def send_link(body:MailLink)-> LoginResponse:
    try:
        dbconnect = Connect().dbconnect()
        cursor = dbconnect.cursor()
        cursor.execute(f"""
                SELECT email, id
                FROM "user"
                WHERE "user".email = %s 
            """, (body.email,))
        
        user_email = cursor.fetchone()
    
        if not dict(user_email)["email"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found")
    
        token = create_token(user_email["id"], 1)

        await send_mail(body.email, token)
    except InterfaceError as i:
        raise i
    except OperationalError as o:
        raise o
    finally:
        cursor.close()
        dbconnect.close()






async def reset_password(password:PassReset, req:Request)->GenericResponse:
    hashed = hash_password(password.password)

    try:
        dbconnect = Connect().dbconnect()
        cursor = dbconnect.cursor()
        cursor.execute(f"""
                    SELECT password
                    FROM "user"
                    WHERE "user".id = %s 
                """, (req.state.user_id,)
        )

        user = dict((cursor.fetchone()))

        isMatch = verify_password(password.old_pass, user["password"])

        if not isMatch:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credential')

        cursor.execute(
                f"""
                    UPDATE "user"
                    SET password = COALESCE(%s, password)
                    WHERE "user".id = %s
                """, (hashed, req.state.user_id)
        )
        dbconnect.commit()
    except InterfaceError as i:
        raise i
    except OperationalError as o:
        raise o
    finally:
        cursor.close()
        dbconnect.close()


async def github_login(code:str):
    gitUser:GitUser = git_user(code)

    payload = {"git_id":gitUser["id"], "email":gitUser["email"]}

    try:
        dbconnect = Connect().dbconnect()
        cursor = dbconnect.cursor()
        cursor.execute(
                f"""
                WITH inserted AS (
                    INSERT INTO "user" (id, email, git_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (email) DO NOTHING
                    RETURNING id
                    )
                    SELECT id FROM inserted
                    UNION ALL
                    SELECT id FROM "user" WHERE git_id = %s;
                """, (user_id, payload["email"], payload["git_id"], payload["git_id"]) )
        
        dbconnect.commit()
        user = dict(cursor.fetchone())
        
    except InterfaceError as i:
        raise i
    except OperationalError as o:
        raise o
    finally:
        cursor.close()
        dbconnect.close()

    token = create_token(user["id"], expiry=2)
    return token
