import json

from werkzeug.exceptions import HTTPException as _HTTPException


class HTTPException(_HTTPException):
    code = 0
    status = 'failed'

    def __init__(self, msg=None, response=None):
        if msg:
            self.msg = msg
        self.response = response

    def get_body(self, environ=None):
        body = dict(
            msg=self.msg,
            status=self.status
        )
        return json.dumps(body)

    def get_headers(self, environ=None):
        return [("Content-Type", "application/json")]


class ParameterException(HTTPException):
    code = 400
    msg = '参数错误'


class RepeatException(HTTPException):
    code = 400
    msg = '字段重复'


class ValidateCodeException(HTTPException):
    code = 400
    msg = '验证码错误或过期'


class AuthFailed(HTTPException):
    code = 401
    msg = '认证失败'


class UserHasRegister(HTTPException):
    code = 401
    msg = '用户已注册'


class Forbidden(HTTPException):
    code = 401
    msg = '权限不足'


# 用于邮箱验证
class EmailValidateException(HTTPException):
    code = 401
    msg = 'token 验证失败'


class NotFound(HTTPException):
    code = 404
    msg = '资源不存在'


class EmailNotFound(HTTPException):
    code = 404
    msg = '邮箱不存在'


class EmailHasAdd(HTTPException):
    code = 409
    msg = '邮件已添加'


# 文件太大
class RequestEntityTooLarge(HTTPException):
    code = 413
    msg = '文件过大'


class UnknownException(HTTPException):
    code = 500
    msg = '服务器未知错误'
