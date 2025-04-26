import aiosmtplib
from email.message import EmailMessage

from backend.settings import settings

async def send_confirm_email(to_email: str, token:str) -> None:
    confirm_url = f"http://127.0.0.1:8000/api/v1/auth/register-confirm?token={token}"
    print(confirm_url)
    text = f"""Thank you for registration! For verification, follow the link: {confirm_url}"""

    message = EmailMessage()
    message.set_content(text)
    message["From"] = settings.email_settings.email_username
    print(settings.email_settings.email_username)
    message["To"] = to_email
    print(to_email)
    message["Subject"] = "Email confirmation"


    async with aiosmtplib.SMTP(
        hostname=settings.email_settings.email_host, 
        port=settings.email_settings.email_port,
        use_tls=True
    ) as smtp:
        try:
            resp = await smtp.login(
                settings.email_settings.email_username,
                settings.email_settings.email_password.get_secret_value(),
            )
            print(resp.code)
        except Exception as err:
            raise aiosmtplib.SMTPException("Couldnt login") from err
        await smtp.send_message(message)


async def send_passw_recovery_email(to_email: str, token:str) -> None:
    confirm_url = f"http://127.0.0.1:8000/api/v1/auth/password-recovery-confirm?token={token}"
    print(confirm_url)
    text = f"""For password recovery follow the link: {confirm_url}"""

    message = EmailMessage()
    message.set_content(text)
    message["From"] = settings.email_settings.email_username
    print(settings.email_settings.email_username)
    message["To"] = to_email
    print(to_email)
    message["Subject"] = "Password recovery"


    async with aiosmtplib.SMTP(
        hostname=settings.email_settings.email_host, 
        port=settings.email_settings.email_port,
        use_tls=True
    ) as smtp:
        try:
            resp = await smtp.login(
                settings.email_settings.email_username,
                settings.email_settings.email_password.get_secret_value(),
            )
            print(resp.code)
        except Exception as err:
            raise aiosmtplib.SMTPException("Couldnt login") from err
        await smtp.send_message(message)
        