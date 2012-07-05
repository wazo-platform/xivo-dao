# -*- coding: utf-8 -*-

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

_DB_CONNECTION_POOL = None


class DBConnection(object):
    def __init__(self, uri):
        self._engine = None
        self._session = None
        if '?' in uri:
            self._uri = uri.split('?')[0]
        else:
            self._uri = uri

    def connect(self):
        self._engine = create_engine(self._uri)
        Session = sessionmaker(bind=self._engine)
        self._session = Session()

    def close(self):
        if self._session is not None:
            self._session.close()
            self._session = None

    def get_engine(self):
        return self._engine

    def get_session(self):
        return self._session


class DBConnectionPool(object):
    def __init__(self, connection_factory):
        self._connection_factory = connection_factory
        self._key_to_connection = {}
        self._uri_to_connection = {}

    def close(self):
        for connection in self._uri_to_connection.itervalues():
            connection.close()
        self._key_to_connection = {}
        self._uri_to_connection = {}

    def _do_add_connection(self, uri, key):
        if key is None:
            key = uri
        if uri not in self._uri_to_connection:
            connection = self._connection_factory(uri)
            connection.connect()
            self._uri_to_connection[uri] = connection
        if key not in self._key_to_connection:
            self._key_to_connection[key] = self._uri_to_connection[uri]

    def add_connection(self, uri):
        self._do_add_connection(uri, None)

    def add_connection_as(self, uri, key):
        self._do_add_connection(uri, key)

    def get_connection(self, uri):
        return self._key_to_connection[uri]


def register_db_connection_pool(db_connection_pool):
    global _DB_CONNECTION_POOL
    _DB_CONNECTION_POOL = db_connection_pool


def unregister_db_connection_pool():
    global _DB_CONNECTION_POOL
    if _DB_CONNECTION_POOL is not None:
        _DB_CONNECTION_POOL.close()
        _DB_CONNECTION_POOL = None


def get_db_connection_pool():
    return _DB_CONNECTION_POOL


def _get_connection_pool_or_raise():
    db_connection_pool = _DB_CONNECTION_POOL
    if db_connection_pool is None:
        raise Exception("No registered DB connection pool")
    else:
        return db_connection_pool


def add_connection(uri):
    db_connection_pool = _get_connection_pool_or_raise()
    db_connection_pool.add_connection(uri)


def add_connection_as(uri, key):
    db_connection_pool = _get_connection_pool_or_raise()
    db_connection_pool.add_connection_as(uri, key)


def get_connection(uri):
    db_connection_pool = _get_connection_pool_or_raise()
    return db_connection_pool.get_connection(uri)
