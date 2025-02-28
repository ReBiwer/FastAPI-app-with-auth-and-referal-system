import random
import string
from datetime import datetime
from datetime import timedelta

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig
from fastapi_mail import FastMail
from fastapi_mail import MessageSchema
from fastapi_mail import MessageType
from app.models.auth import User
from app.schemas.ref import ReferralCodeInfo

from app.config import settings


def create_get_ref_code(len_code: int = 6):
    characters = string.digits + string.ascii_uppercase
    random_string = "".join(random.choice(characters) for _ in range(len_code))
    return random_string


def _get_conn_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.USE_CREDENTIALS,
        VALIDATE_CERTS=settings.VALIDATE_CERTS,
    )


def send_code_to_mail(user: User, ref_code: ReferralCodeInfo, background_tasks: BackgroundTasks):
    mail_conf = _get_conn_config()
    end_action_date_code = datetime.now() + timedelta(days=ref_code.action_time_day)
    text = f"Ваш реферальный код: {ref_code.code}\n" f"Действителен до {end_action_date_code.strftime("%d.%m.%Y")}"
    msg = MessageSchema(
        subject="Реферальный код",
        recipients=[user.email],
        body=text,
        subtype=MessageType.plain,
    )
    fm = FastMail(config=mail_conf)
    background_tasks.add_task(fm.send_message, msg)
