import requests
from fastapi import Request, HTTPException, status
from ..utils.settings import Settings
from ..utils.models import GitUser

settings = Settings()

def get_token(code:str):
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET
    token_queries = {"client_id":client_id, "client_secret":client_secret, "code":code}
    token_url = f"https://github.com/login/oauth/access_token"
    header={"Content-Type":"application/json"}
    
    response = requests.post(url=token_url, params=token_queries, headers=header)

    if response.status_code == 200:
        token = response.text.split("=")[1].split("&")[0]
    else:
        return {'success':False, "message":'Could not get authorization. Please try again'}
    
    return token
    

def get_email(token:str):
    url = "https://github.com/user/email"
    header = {"Content-Type":"application/json", "Authorization":f"Bearer {token}"}

    response = requests.get(url=url, headers=header)

    if response.status_code == 200:
        emails = response.json()
    
    primary_email = list(filter(lambda a:a["primary"] == True, list(emails)))[0]["email"]

    return primary_email

def git_user(code:str):
    token = get_token(code)
    url = "https://api.github.com/user"
    header = {"Authorization":f"Bearer {token}", "Content-Type":"application/json"}

    response = requests.get(url=url, headers=header)

    if response.status_code == 200:
        res = response.json()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unable to fetch user')

    user_copy = dict(res)

    if user_copy["email"] == None:
        email = get_email(token)
        user_copy.update({"email":email})

    return user_copy