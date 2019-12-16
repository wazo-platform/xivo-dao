# -*- coding: utf-8 -*-
# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
import sys

from functools import wraps
from sqlalchemy import event, exc
from sqlalchemy import create_engine
from sqlalchemy.pool import Pool
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, TypeDecorator

from xivo.config_helper import ConfigParser, ErrorHandler

DEFAULT_DB_URI = 'postgresql://asterisk:proformatique@localhost/asterisk'

logger = logging.getLogger(__name__)
Session = scoped_session(sessionmaker())
Base = declarative_base()


# http://docs.sqlalchemy.org/en/rel_0_9/_modules/examples/join_conditions/cast.html
class IntAsString(TypeDecorator):
    """Coerce integer->string type.

    This is needed only if the relationship() from
    string to int is writable, as SQLAlchemy will copy
    the int parent values into the string attribute
    on the child during a flush.

    """
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = str(value)
        return value


class UUIDAsString(TypeDecorator):
    impl = String

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


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        raise exc.DisconnectionError()
    cursor.close()


def daosession(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        session = Session()
        return func(session, *args, **kwargs)
    return wrapped


def init_db(db_uri):
    engine = create_engine(db_uri)
    Session.configure(bind=engine)
    Base.metadata.bind = engine


def init_db_from_config(config=None):
    config = config or default_config()
    app_name = os.path.basename(sys.argv[0])
    url = config.get('db_uri', "%s?application_name=%s" % (DEFAULT_DB_URI, app_name))
    init_db(url)


def default_config():
    config = {
        'config_file': '/etc/xivo-dao/config.yml',
        'extra_config_files': '/etc/xivo-dao/conf.d',
    }
    config_parser = ConfigParser(ErrorHandler())
    return config_parser.read_config_file_hierarchy(config)
