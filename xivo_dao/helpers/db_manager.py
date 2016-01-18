# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging
from functools import wraps
from sqlalchemy import event, exc
from sqlalchemy import create_engine
from sqlalchemy.pool import Pool
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from xivo.config_helper import ConfigParser, ErrorHandler

DEFAULT_DB_URI = 'postgresql://asterisk:proformatique@localhost/asterisk'


logger = logging.getLogger(__name__)
Session = scoped_session(sessionmaker())
Base = declarative_base()


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


def init_db(db_uri, legacy_mode=False):
    engine = create_engine(db_uri)
    Session.configure(bind=engine)
    Base.metadata.bind = engine


def init_db_from_config(config=None, legacy_mode=False):
    config = config or default_config()
    url = config.get('db_uri', DEFAULT_DB_URI)
    init_db(url, legacy_mode)


def default_config():
    config = {
        'config_file': '/etc/xivo-dao/config.yml',
        'extra_config_files': '/etc/xivo-dao/conf.d',
    }
    config_parser = ConfigParser(ErrorHandler())
    return config_parser.read_config_file_hierarchy(config)
