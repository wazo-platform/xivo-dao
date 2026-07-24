# Copyright 2012-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from sqlalchemy.types import String, TypeDecorator
from xivo.config_helper import ConfigParser, ErrorHandler

DEFAULT_DB_URI = (
    'postgresql://asterisk:proformatique@localhost/asterisk?application_name=xivo-dao'
)
DEFAULT_POOL_SIZE = 16
DB_POOL_SPARE_CONN = 10

logger = logging.getLogger(__name__)
Session = scoped_session(sessionmaker())


class BaseMixin:
    def __repr__(self):
        attrs = {
            col.name: getattr(self, col.name)
            for col in self.__table__.columns
            if col.primary_key
        }
        attrs_fmt = ", ".join(f"{k}={v}" for k, v in attrs.items())
        return f"{self.__class__.__name__}({attrs_fmt})"


Base = declarative_base(cls=BaseMixin)


# http://docs.sqlalchemy.org/en/rel_0_9/_modules/examples/join_conditions/cast.html
class IntAsString(TypeDecorator):
    """Coerce integer->string type.

    This is needed only if the relationship() from
    string to int is writable, as SQLAlchemy will copy
    the int parent values into the string attribute
    on the child during a flush.

    """

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = str(value)
        return value


class UUIDAsString(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = str(value)
        return value


def todict(self, exclude=None):
    exclude = exclude or []
    d = {}
    for c in self.__table__.columns:
        name = c.name.replace('-', '_')
        if name not in exclude:
            value = getattr(self, name)
            d[c.name] = value

    return d


Base.todict = todict


def daosession(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        session = Session()
        return func(session, *args, **kwargs)

    return wrapped


def init_db(db_uri, pool_size=DEFAULT_POOL_SIZE, max_overflow=10):
    engine = create_engine(
        db_uri, pool_size=pool_size, max_overflow=max_overflow, pool_pre_ping=True
    )
    Session.configure(bind=engine)
    Base.metadata.bind = engine


def init_db_from_config(config=None):
    config = config or default_config()
    url = config.get('db_uri', DEFAULT_DB_URI)
    try:
        min_threads = config['rest_api']['min_threads']
        max_threads = config['rest_api']['max_threads']
    except KeyError:
        # Consumers without a REST API (agid, purge-db, ...)
        init_db(url)
        return

    # Dynamic HTTP thread pool: retain connections only for the always-alive
    # threads. Bursts borrow overflow connections, which SQLAlchemy closes on
    # return — mirroring the thread pool shrinking back after the burst.
    init_db(
        url,
        pool_size=min_threads,
        max_overflow=max_threads - min_threads + DB_POOL_SPARE_CONN,
    )


def default_config():
    config = {
        'config_file': '/etc/xivo-dao/config.yml',
        'extra_config_files': '/etc/xivo-dao/conf.d',
    }
    config_parser = ConfigParser(ErrorHandler())
    return config_parser.read_config_file_hierarchy(config)
