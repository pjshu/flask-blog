from sqlalchemy.dialects.mysql import LONGTEXT
from werkzeug.security import check_password_hash, generate_password_hash
from app.exception import AuthFailed, ValidateCodeException, RepeatException, UserHasRegister
from .baseDb import Base, db, BaseSearch
from flask_jwt_extended import create_refresh_token, get_jwt_identity
from app.utils import generate_verification_code, get_code_exp_stamp, get_now_timestamp

tags_to_post = db.Table(
    'tags_to_post',
    db.Column('tags_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

# 文章链接(图片/...)
link_to_post = db.Table(
    'link_to_post',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('link_id', db.Integer, db.ForeignKey('link.id'), primary_key=True)
)


class Post(BaseSearch):
    # 不能用set_attrs方法直接设置的字段列表
    blacklist = ['id', 'comments']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), default='')
    article = db.Column(LONGTEXT, comment='文章内容', default='')
    excerpt = db.Column(db.TEXT, comment="文章摘要", default='')
    change_date = db.Column(db.BigInteger, index=True)
    visibility = db.Column(db.String(16), default="私密", comment='文章可见性:私密/公开')
    comments = db.Column(db.Integer, default=0, comment="评论数量")

    tags = db.relationship('Tag', secondary=tags_to_post, backref=db.backref('posts', lazy=True))
    links = db.relationship('Link', secondary=link_to_post, backref=db.backref('posts', lazy=True))

    def __init__(self, *args, **kwargs):
        if 'comments' not in kwargs:
            kwargs['comments'] = self.__table__.c.comments.default.arg
        super().__init__(*args, **kwargs)

    def _set_attrs(self, attrs: dict):
        for key, value in attrs.items():
            if key == 'tags':
                self._set_tags(value)
                continue
            if key == 'links':
                self._set_links(value)
                continue
            self._set_attr(key, value)

    def _set_links(self, url):
        self.links.append(Link(url=url))

    def _set_tags(self, tags):
        for tag in tags:
            tag = Tag.search_by(name=tag, error=False) or Tag(name=tag)
            if tag in self.tags:
                continue
            self.tags.append(tag)
            tag.count += 1

    @classmethod
    def delete_by_id(cls, identify):
        one = cls.search_by(id=identify)
        with db.auto_commit():
            for tag in one.tags:
                tag.count -= 1
            db.session.delete(one)

    @classmethod
    def paging_search(cls, page, per_page, order_by, **kwargs):
        # TODO: 支持按日期...查找,暂时只支持按文章标题查找
        return super().paging_search(page, per_page, order_by, filters=cls.title.like, **kwargs)


class Tag(BaseSearch):
    blacklist = ['id', 'count']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    describe = db.Column(db.String(128), default='')
    # 使用标签的文章数量
    count = db.Column(db.Integer, default=0)

    # 图片链接(用于图床)或图片名(本地)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id'))

    def __init__(self, *args, **kwargs):
        if 'count' not in kwargs:
            kwargs['count'] = self.__table__.c.count.default.arg
        super().__init__(*args, **kwargs)

    @classmethod
    def paging_search(cls, page, per_page, order_by, **kwargs):
        # TODO: 暂时只支持按标签名查找
        return super().paging_search(page, per_page, order_by, filters=cls.name.like, **kwargs)

    # 更新标签名时查重
    @classmethod
    def check_repeat(cls, **kwargs):
        one = cls.search_by(**kwargs, error=False)
        if one:
            raise RepeatException(msg='标签名已存在')

    def _set_links(self, url):
        self.links = Link(url=url)

    def _set_attrs(self, attrs: dict):
        for key, value in attrs.items():
            if key == 'links':
                self._set_links(value)
                continue
            self._set_attr(key, value)


class User(Base):
    blacklist = ['id', 'password_hash']
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(128))
    username = db.Column(db.String(128))
    email = db.Column(db.String(128), nullable=True)
    password_hash = db.Column(db.String(128))
    about = db.Column(LONGTEXT, comment="关于用户")
    avatar = db.Column(LONGTEXT)
    # 保留字段
    email_is_validate = db.Column(db.Boolean, default=False)
    # 验证码
    code = db.relationship('Code', backref=db.backref('user', lazy=True), uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not check_password_hash(self.password_hash, password):
            raise AuthFailed("密码错误")

    def generate_login_token(self):
        return create_refresh_token(identity=self.id)

    def _set_attrs(self, attrs: dict):
        for key, value in attrs.items():
            if key == 'password':
                self.set_password(value)
                continue
            self._set_attr(key, value)

    @classmethod
    def reset_password(cls, form):
        """
            登录状态下调用
        """
        uid = get_jwt_identity()
        user = cls.search_by(id=uid)
        user.update(password=form.password.data)
        return user

    @classmethod
    def validate_code_by(cls, code, **kwargs):
        user = cls.search_by(**kwargs)
        user.code.validate_code(code)
        return user

    def set_code(self):
        code = Code()
        self.update(code=code)
        return code.code

    @classmethod
    def set_code_by_id(cls):
        identify = get_jwt_identity()
        user = cls.search_by(id=identify)
        return user.set_code()

    # 登录状态调用
    @classmethod
    def get_user(cls):
        uid = get_jwt_identity()
        return cls.search_by(id=uid)

    @classmethod
    def check_register(cls):
        user = cls.query.all()
        if user:
            raise UserHasRegister('用户已注册')


# 验证码
class Code(Base):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16))
    expire_date = db.Column(db.BigInteger, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, *args, **kwargs):
        self.code = generate_verification_code()
        self.expire_date = get_code_exp_stamp()
        super(Code, self).__init__(*args, **kwargs)

    @property
    def _is_expire(self):
        now = get_now_timestamp()
        return now > self.expire_date

    def _set_code_expire(self):
        expire_date = get_now_timestamp() - 1
        self.update(expire_date=expire_date)

    def validate_code(self, code):
        if self.code != code:
            raise ValidateCodeException("验证码错误")
        if self._is_expire:
            raise ValidateCodeException("验证码已过期")
        self._set_code_expire()

    def _set_attrs(self, attrs: dict):
        super()._set_attrs(attrs)


# 用于储存图片链接
class Link(BaseSearch):
    id = db.Column(db.Integer, primary_key=True)
    describe = db.Column(db.String(255), comment="链接描述")
    # 图片链接(用于图床)或图片名(本地)
    url = db.Column(db.String(255))
    tags = db.relationship('Tag', backref=db.backref('links', lazy=True))

    @classmethod
    def paging_search(cls, page, per_page, order_by, **kwargs):
        # TODO: 暂时只支持describe查找
        return super().paging_search(page, per_page, order_by, filters=cls.describe.like, **kwargs)

    def _set_attrs(self, attrs: dict):
        super()._set_attrs(attrs)
