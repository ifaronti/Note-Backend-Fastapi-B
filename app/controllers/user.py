from prisma import Prisma
from ..utils.models import Register, Login, LoginResponse, MailLink, GenericResponse, PassReset, GitUser
from ..dependencies.password_manager import verify_password, hash_password
from ..dependencies.token import create_token, verify_token
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends, status, HTTPException, Request
import uuid
from ..dependencies.send_link import send_mail
from ..dependencies.git_oauth2 import git_user

prisma = Prisma()

user_id = str(uuid.uuid1())

exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail='Invalid credentials provided')



async def register(form_data:Register):
    try:
        await prisma.connect()
        hashed_pass = hash_password(password=form_data.password)
        await prisma.execute_raw(f"""
            INSERT INTO "user" (id, email, password)
            VALUES('{user_id}', '{form_data.email}', '{hashed_pass}')
        """)
        # For some reasons, prisma won't allow raw_sql and uuid auto generated unless I 
        # change the id's default value to autoincrement(). But I gotta practice my raw sql
        # though. Prisma wins cause it's easy but what of complex queries and team leads
        # that want raw sql only? Gotta be prepared for any outcome.
    except:
        raise 
    finally:
        await prisma.disconnect()






async def logon(formdata:Annotated[Login, Depends(OAuth2PasswordRequestForm)]):
    try:
        await prisma.connect()
        user = await prisma.query_raw(f"""
                SELECT 
                    id, password 
                FROM
                    "user"
                WHERE
                    "user".email = '{formdata.username}'
            """
        )

        isMatch = verify_password(formdata.password, user[0]["password"])
        if not isMatch:
            raise exception

        token = create_token(user_id=user[0]["id"], expiry=2)
    # except Exception:
    #     raise Exception
    finally:
        await prisma.disconnect()
    return token






async def send_link(body:MailLink)-> LoginResponse:
    email = body.email
    try:
        await prisma.connect()
        user_email = await prisma.query_raw(f"""
                SELECT email, id
                FROM "user"
                WHERE "user".email = '{email}' 
            """)
    
        if not user_email[0]["email"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found")
    
        token = create_token(user_email[0]["id"], 1)
        await send_mail(email, token)
    except:
        raise
    finally:
        await prisma.disconnect()






async def reset_password(password:PassReset, req:Request)->GenericResponse:
    hashed = hash_password(password.password)

    try:
        await prisma.connect()
        await prisma.query_raw(
                f"""
                    UPDATE "user"
                    SET password = COALESCE($1, password)
                    WHERE "user".id = $2
                """, f'{hashed}', f'{req.state.user_id}'
            )
    except:
        raise
    finally:
        await prisma.disconnect()


async def github_login(code:str):
    gitUser:GitUser = git_user(code)

    payload = {"git_id":gitUser["id"], "email":gitUser["email"]}

    try:
        await prisma.connect()
        user = await prisma.query_raw(
                f"""
                WITH inserted AS (
                    INSERT INTO "user" (id, email, git_id)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (email) DO NOTHING
                    RETURNING id
                    )
                    SELECT id FROM inserted
                    UNION ALL
                    SELECT id FROM "user" WHERE git_id = $4;
                """, user_id, str(payload["email"]), payload["git_id"], payload["git_id"] )
            
        print(user)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to fetch user details")
    finally:
        await prisma.disconnect()

    token = create_token(user[0]["id"], expiry=2)
    return token
