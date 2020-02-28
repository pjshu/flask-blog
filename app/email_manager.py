from flask import url_for, current_app
from flask_jwt_extended import decode_token, create_access_token
from flask_mail import Message
from app.exception import EmailValidateException
from enum import Enum, unique
from flask_mail import Mail

mail = Mail()


@unique
class MailType(Enum):
    CHANGE_EMAIL = 'change email'
    NEW_EMAIL = 'new email'


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, content):
    from threading import Thread
    app = current_app._get_current_object()
    msg = Message(
        subject=subject,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[to]
    )
    msg.body = content
    # msg.html = "<b>testing</b>"
    t = Thread(target=send_async_email, args=[app, msg])
    t.start()


def send_validate_email_email(user=None, uid=None, form=None, addr=None):
    email = addr if addr else form.email.data
    uid = uid if uid else user.id
    send_email(
        to=email,
        subject='新邮件确认',
        content=url_for(
            'admin.auth_email_view',
            token=create_access_token(identity=uid, user_claims={
                'type': MailType.NEW_EMAIL.value,
                'email': email
            })
        ))


def send_change_email_email(user=None, uid=None, form=None, addr=None):
    uid = uid if uid else user.id
    email = addr if addr else form.email.data
    send_email(
        to=email,
        subject='邮箱地址修改确认',
        content=url_for(
            'admin.auth_email_view',
            token=create_access_token(identity=uid, user_claims={
                'type': MailType.CHANGE_EMAIL.value,
                'email': email
            })
        ))


def send_change_password_email(user=None, uid=None, addr=None):
    uid = uid if uid else user.id
    send_email(
        to=addr,
        subject='修改密码确认',
        content=url_for(
            'admin.auth_email_view',
            token=create_access_token(identity=uid)
        ))
