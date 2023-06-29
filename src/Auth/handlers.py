import ssl
from src.utils import create_access_token
from typing import Dict, Any
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

PORT = 465
PASSWORD = "jumavic@9118"
SENDER_MAIL = "info@mouseinc.net"
MAIL_SERVER='mail.mouseinc.net'
MAIL_TLS=False
MAIL_SSL=True

class PasswordHandler:
    def __init__(self):
        self.mail_context = ssl.create_default_context()
        self.PORT = PORT
        self.PASSWORD = PASSWORD
        self.SENDER_MAIL = SENDER_MAIL
        self.MAIL_SERVER='mail.mouseinc.net',
        self.MAIL_TLS=False,
        self.MAIL_SSL=True

    def generate_mail_reset_token(self, User: Dict[str, Any]):
        return create_access_token(
                    subject = User['id']
                )

    def send_mail(self, recepient, message):
        with smtplib.SMTP_SSL(MAIL_SERVER, self.PORT, context=self.mail_context) as server:
            server.login(self.SENDER_MAIL, self.PASSWORD)
            server.sendmail(self.SENDER_MAIL, recepient, str(message))

    def reset_password(self, User) -> None:
        reset_html = f"""
            <html>
                <body>
                    <h1>Request for Password Reset</h1>
                    <p>
                        Click the link below to reset your password <a href="http://141.95.42.124/reset/password?token={self.generate_mail_reset_token(User)}">reset password</a>
                    </p>
                </body>
            </html>
        """
        message = MIMEMultipart()
        message['From'] = self.SENDER_MAIL
        message['To'] = User['email']
        message['Subject'] = "Request for Password reset"

        message.attach(
                MIMEText(
                    reset_html, "html"
                )
            )
        self.send_mail(
               User['email'],
               message
            )

    def set_password(self, user: Dict[str, Any]):
        print(user)
        set_html = f"""

        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>StudyAllies Account Confirmation</title>
        </head>
        <body style="font-family: Arial, sans-serif; font-size: 14px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <img src="https://studyallies.com/logo_study-1.png" alt="Logo" style="max-width: 150px;">
            </div>
            <p>Hello {user['username']},</p><br />
            <p>You've recently registered a new StudyAllies account.</p>
            <p>Before your account is activated, we need you to confirm your email address.</p>
            <p style="margin-bottom: 10px;">Please click this link to complete your registration:</p>
            <p style="margin-bottom: 10px;"><a href="http://127.0.0.1:8000/account/user/verify/{self.generate_mail_reset_token(user)}">http://127.0.0.1:8000/create/password/{self.generate_mail_reset_token(user)}</a></p><br /><br />
            <p>You can log into your account using your details:</p>
            <p><strong>Username</strong>: {user['username']}</p>
            <p><strong>Password</strong>: {user['password']}</p>
            <p>If you have any questions, please contact us for assistance.</p>
            <p>Best Regards,</p>
            <p>StudyDaddy</p><br /><br /><br />
            <p>To ensure that our messages get to you (and don't go to your junk or bulk email folders), please add <a href="mailto:support@studyallies.com">support@studyallies.com</a> to your address book.</p>
        </body>
        </html>
        """
        message = MIMEMultipart()
        message['From'] = self.SENDER_MAIL
        message['To'] = user['email']
        message['Subject'] = "Request for Password reset"

        message.attach(
                MIMEText(
                    set_html, "html"
                )
            )
        self.send_mail(
               user['email'],
               message
            )