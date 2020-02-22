from wtforms import PasswordField, StringField, IntegerField, FieldList
from wtforms.validators import DataRequired, EqualTo, Regexp, Email, Length, AnyOf

from app.utils import time2stamp
from .base import JsonValidate


class LoginValidate(JsonValidate):
    username = StringField('用户名', validators=[
        DataRequired(message="用户名不可为空"),
        Length(min=0, max=128, message="用户名或密码错误")
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message="密码不可为空"),
        Regexp(r'^^[a-zA-Z0-9!@#$%^&*()_+]{6,20}$',
               message='用户名或密码错误'),
    ])


class RegisterValidate(JsonValidate):
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=0, max=128, message="用户名长度在0-128字符间")
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不可为空'),
        Regexp(r'^[a-zA-Z0-9!@#$%^&*()_+]{6,20}$',
               message='密码长度为6-20个字符,可以为字母,数字,!@#$%^&*()_+'),
        EqualTo('confirm_password', message='两次输入密码不一致')
    ])
    email = StringField('邮件', validators=[
        Email(message='请输入有效的邮箱地址，比如：username@domain.com')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码')
    ])
    excerpt = StringField('摘要', validators=[
        DataRequired(message='文章摘要不可为空'),
        Length(max=300, message="摘要最大长度为300")
    ])


class PostValidate(JsonValidate):
    id = IntegerField('文章id', validators=[
        DataRequired(message='id不能为空'),
    ])
    title = StringField('文章标题', validators=[
        Length(0, 128, message="文章标题在0~128字符之间")
    ])
    tags = FieldList(StringField('标签'), min_entries=0)
    visibility = StringField('文章可见性', validators=[
        DataRequired(message='visibility不能为空'),
        AnyOf(['私密', '公开'], message="visibility只能为私密或公开")
    ])
    change_date = IntegerField('文章修改日期', validators=[
        DataRequired(message='change_date不能为空'),
    ], filters=[time2stamp])
    create_date = IntegerField('文章创建日期', validators=[
        DataRequired(message='change_date不能为空'),
    ], filters=[time2stamp])
    article = StringField('文章内容')


class UserValidate(JsonValidate):
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空')])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不可为空'),
        Regexp(r'^[a-zA-Z0-9!@#$%^&*()_+]{6-20}$',
               message='密码长度为6-20个字符,可以为字母,数字,!@#$%^&*()_+')
    ])
    email = StringField('邮件', validators=[
        Email(message='请输入有效的邮箱地址，比如：username@domain.com')
    ])
    avatar = StringField('头像')
    about = StringField('关于')


class TagValidate(JsonValidate):
    id = IntegerField('标签id', validators=[
        DataRequired(message="id不能为空")])
    name = StringField('标签名', validators=[
        DataRequired(message='标签名不可为空'),
        Length(max=64, message="标签名最大长度为字符")])
    describe = StringField('描述', validators=[Length(min=0, max=128, message="描述长度为0-128字符之间")])
