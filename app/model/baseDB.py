from abc import abstractmethod
from contextlib import contextmanager
from enum import Enum, unique

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery

from app.exception import UnknownException, NotFound
from app.utils import get_now_timestamp


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise UnknownException(e.args)

    def apply_pool_defaults(self, app, options):
        super().apply_pool_defaults(app, options)
        # options["pool_pre_ping"] = True


class Query(BaseQuery):
    def get_or_404(self, ident, description=None, error=True):
        rv = self.get(ident)
        if rv is None:
            if error:
                raise NotFound()
            else:
                return None
        return rv

    def first_or_404(self, description=None, error=True):
        rv = self.first()
        if rv is None:
            if error:
                raise NotFound()
            else:
                return None
        return rv

    def total(self):
        return self.count()

    @classmethod
    def search_by(cls, **kwargs):
        return cls.filter_by(**kwargs)


db = SQLAlchemy(query_class=Query)


class Base(db.Model):
    """
    该类基本封装增删改查
    :param blacklist: 不能用_set_attrs方法直接设置的字段列表
    :param create_date: 创建日期,实例化时自动添加
    """
    __abstract__ = True
    blacklist = ['id']
    create_date = db.Column(db.BigInteger, index=True)

    def __init__(self, *args, **kwargs):
        self.create_date = get_now_timestamp()
        super().__init__(*args, **kwargs)

    @classmethod
    def search_by(cls, **kwargs) -> db.Model:
        error = kwargs.pop('error', True)
        return cls.query.filter_by(**kwargs).first_or_404(error=error)

    def delete(self):
        with db.auto_commit():
            db.session.delete(self)

    @classmethod
    def delete_by(cls, **kwargs):
        one = cls.search_by(**kwargs)
        with db.auto_commit():
            db.session.delete(one)

    @classmethod
    def delete_all_by_id(cls, ids):
        for identify in ids:
            cls.delete_by(id=identify)

    def update(self, **kwargs):
        with db.auto_commit():
            self._set_attrs(kwargs)

    @classmethod
    def update_by_id(cls, identify: int, **kwargs):
        one = cls.search_by(id=identify)
        with db.auto_commit():
            one._set_attrs(kwargs)
            db.session.add(one)

    @classmethod
    def create(cls, **kwargs):
        one = cls()
        with db.auto_commit():
            one._set_attrs(kwargs)
            db.session.add(one)
        return one

    # 获取表的记录数
    @classmethod
    def total(cls):
        return cls.query.total()

    @abstractmethod
    def _set_attrs(self, attrs: dict):
        for key, value in attrs.items():
            self._set_attr(key, value)

    def _set_attr(self, key, value):
        if hasattr(self, key) and key not in self.blacklist:
            setattr(self, key, value)


@unique
class Visibility(Enum):
    privacy = '私密'
    public = '公开'


@unique
class CommentEnum(Enum):
    replay = '回复'
    comment = '评论'


# 提供分页查询功能
class Searchable(Base):
    __abstract__ = True

    # 可排序字段
    sortable = ['create_date', 'id', 'change_date']

    @classmethod
    @abstractmethod
    def paging_search(cls, page: int, per_page: int, order_by: dict = None, query: Query = None):
        order_by = cls._get_order_by(order_by)
        query = query if query else cls.query
        return query.order_by(*order_by).paginate(page=page, per_page=per_page, error_out=False)

    @classmethod
    def _get_order_by(cls, order_by):
        """
        order_by: [{field:'id',desc:True},{field:'create_date'}]
        """
        res = []
        if not order_by:
            res.append(cls.id.desc())
        else:
            for item in order_by:
                field = item.get('field')
                if field in cls.sortable:
                    res.append(
                        getattr(cls, field).desc()
                        if item.get('desc', None)
                        else getattr(cls, field).asc()
                    )
        return res
