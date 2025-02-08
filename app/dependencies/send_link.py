from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from ..utils.settings import Settings

settings = Settings()

conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = 587,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_mail(email:str, token:str):
    html = f"""<a target=_blank href="https://note-obhp313k5-ifarontis-projects.vercel.app/login/reset?token={token}">Click Here To Reset Password</a>"""

    fm = FastMail(conf)
    message = MessageSchema(
        subject="Password reset",
        recipients=[email],
        body=html,
        subtype=MessageType.html)
    
    await fm.send_message(message=message)


def background_send(email:str, background_tasks:BackgroundTasks):
    html = """<a target=_blank href="https://note-obhp313k5-ifarontis-projects.vercel.app/login/reset">Click Here To Reset Password</a>"""

    fm = FastMail(conf)
    message = MessageSchema(
        subject="Password rese",
        recipients=email,
        body=html,
        subtype=MessageType.html)
    
    background_tasks.add_task(fm.send_message, message)