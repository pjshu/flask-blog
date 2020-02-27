from flask import request, url_for

from app.exception import AuthFailed
from app.model.db import User
from app.model.view_model import UserInfoView
from app.utils import generate_res, login_required, send_email
from app.validate.validate import RegisterValidate, UserValidate, LoginValidate
from .blueprint import admin
from app import blacklist
from flask_jwt_extended import get_raw_jwt, create_refresh_token, decode_token, get_jwt_identity


@admin.route('/auth/register', methods=['POST'])
def register_view():
    form = RegisterValidate().validate_api()
    user = User.create(form.data)
    if form.email.data:
        send_email(
            to=form.email.data,
            subject='账号注册',
            content=url_for('admin.auth_email_view', token=user.generate_access_token())
        )
    return generate_res(data={'id': user.id})


# 修改获取用户信息
@admin.route('/auth/user/info', methods=["GET", "PUT"])
@login_required
def user_info_view():
    uid = request.headers.get('identify')
    user = User.query.get_or_404(uid)
    if request.method == 'PUT':
        form = UserValidate().validate_api()
        if form.email.data and form.email.data != user.email:
            user.email_is_validate = False
            user.email = form.email.data
            send_email(
                to=form.email.data,
                subject='账户邮件修改确认',
                content=url_for('admin.auth_email_view', token=user.generate_access_token())
            )
        user.update(form.data)
        return generate_res()
    return generate_res(data=UserInfoView(user))


@admin.route('/auth/register/<string:token>')
def auth_email_view(token):
    User.confirm_email_token(token)
    return generate_res()


@admin.route('/auth/login', methods=['POST'])
def login_view():
    form = LoginValidate().validate_api()
    user = User.query.filter_by(username=form.username.data).first_or_404()
    if not user.check_password(form.password.data):
        raise AuthFailed()
    user.update(is_active=True)
    return generate_res(data={
        'id': user.id,
        'token': create_refresh_token(identity=user.id)
    })


@admin.route('/auth/logout', methods=["DELETE"])
@login_required
def logout_view():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return generate_res()


# 用于登录验证
@admin.route('/auth')
@login_required
def auth_view():
    return generate_res()

#
# @admin.route('/generate_token')
# def generate_token():
#     from flask_jwt_extended import create_access_token
#     return generate_res(data={
#         'token': create_access_token(identity=1)
#     })
#
#
# @admin.route("/auth_token/<token>")
# def auth_token(token):
#     from flask_jwt_extended import decode_token
#     res = decode_token(token)
#     res.get('identity')
#     return generate_res()
