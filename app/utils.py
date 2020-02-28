import time

from flask import jsonify, current_app
from app.exception import ParameterException


def time2stamp(time_, format_='%Y/%m/%d %H:%M'):
    from wtforms.validators import StopValidation
    try:
        return int(time.mktime(time.strptime(time_, format_)))
    except:
        # 停止验证
        raise StopValidation(message="日期格错误")


def format_time(timestamp, format_='%Y/%m/%d %H:%M'):
    return time.strftime(format_, time.localtime(timestamp))


def generate_res(status='success', **kwargs):
    from app.model.view_model import BaseView
    for key, value in kwargs.items():
        if isinstance(value, BaseView):
            kwargs[key] = value.__dict__
    status = {
        'status': status,
    }
    status.update(kwargs)
    return jsonify(status)


def get_attr(keys: list, data: dict):
    return [data.get(key) for key in keys]


def send_register_email():
    pass


def filters_filename(filename):
    from uuid import uuid1
    from werkzeug.utils import secure_filename
    from os import path
    filename = secure_filename(filename)
    ext_name = path.splitext(filename)[-1]
    if ext_name not in current_app.config['ALLOWED_EXTENSIONS']:
        raise ParameterException('扩展名错误')
    return str(uuid1()) + ext_name
