# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_dao.alchemy import dbconnection


class TestDBConnectionPool(unittest.TestCase):
    def test_add_connection_creates_new_connection(self):
        connection_factory = Mock()

        db_connection_pool = dbconnection.DBConnectionPool(connection_factory)
        db_connection_pool.add_connection('foo')

        connection_factory.assert_called_once_with('foo')

    def test_add_connection_returns_connection(self):
        connection_factory = Mock()
        connection = Mock()
        connection_factory.return_value = connection

        db_connection_pool = dbconnection.DBConnectionPool(connection_factory)
        db_connection_pool.add_connection('foo')

        self.assertTrue(db_connection_pool.get_connection('foo') is connection)

    def test_add_connection_as_creates_new_connection(self):
        connection_factory = Mock()

        db_connection_pool = dbconnection.DBConnectionPool(connection_factory)
        db_connection_pool.add_connection_as('foo', 'bar')

        connection_factory.assert_called_once_with('foo')

    def test_add_connection_as_returns_connection(self):
        connection_factory = Mock()
        connection = Mock()
        connection_factory.return_value = connection

        db_connection_pool = dbconnection.DBConnectionPool(connection_factory)
        db_connection_pool.add_connection_as('foo', 'bar')

        self.assertTrue(db_connection_pool.get_connection('bar') is connection)

    def test_add_connection_doesnt_create_new_connection_if_existing(self):
        connection_factory = Mock()

        db_connection_pool = dbconnection.DBConnectionPool(connection_factory)
        db_connection_pool.add_connection('foo')
        db_connection_pool.add_connection('foo')

        connection_factory.assert_called_once_with('foo')

    def test_add_connection_as_doesnt_create_new_connection_if_existing(self):
        connection_factory = Mock()

        db_connection_pool = dbconnection.DBConnectionPool(connection_factory)
        db_connection_pool.add_connection_as('foo', 'bar')
        db_connection_pool.add_connection_as('foo', 'bar')

        connection_factory.assert_called_once_with('foo')

    def test_close_closes_all_connections(self):
        foo_connection = Mock()
        bar_connection = Mock()

        def connection_factory(uri):
            return {'foo': foo_connection, 'bar': bar_connection}[uri]

        db_connection_pool = dbconnection.DBConnectionPool(connection_factory)
        db_connection_pool.add_connection('foo')
        db_connection_pool.add_connection('bar')
        db_connection_pool.close()

        foo_connection.close.assert_called_once_with()
        bar_connection.close.assert_called_once_with()

    def test_get_connection_raises_key_error_if_absent(self):
        db_connection_pool = dbconnection.DBConnectionPool(Mock())

        self.assertRaises(KeyError, db_connection_pool.get_connection, 'foo')

    def test_add_connection_as_with_different_key_reuse_connection(self):
        db_connection_factory = Mock()
        db_connection_pool = dbconnection.DBConnectionPool(db_connection_factory)

        db_connection_pool.add_connection_as('foo', 'a')
        db_connection_pool.add_connection_as('foo', 'b')

        db_connection_factory.assert_called_once_with('foo')


class TestModule(unittest.TestCase):
    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

    def test_get_connection_pool_return_none_if_not_registered(self):
        self.assertEqual(None, dbconnection.get_db_connection_pool())

    def test_register_connection_pool(self):
        db_connection_pool = Mock()

        dbconnection.register_db_connection_pool(db_connection_pool)

        self.assertTrue(dbconnection.get_db_connection_pool() is db_connection_pool)

    def test_unregister_connection_pool(self):
        db_connection_pool = Mock()

        dbconnection.register_db_connection_pool(db_connection_pool)
        dbconnection.unregister_db_connection_pool()

        self.assertEqual(None, dbconnection.get_db_connection_pool())

    def test_unregister_connection_pool_close_pool(self):
        db_connection_pool = Mock()

        dbconnection.register_db_connection_pool(db_connection_pool)
        dbconnection.unregister_db_connection_pool()

        db_connection_pool.close.assert_called_once_with()

    def test_get_connection(self):
        db_connection_pool = Mock()
        db_connection = object()
        db_connection_pool.get_connection.return_value = db_connection

        dbconnection.register_db_connection_pool(db_connection_pool)
        returned_db_connection = dbconnection.get_connection('foo')

        self.assertTrue(returned_db_connection is db_connection)
        db_connection_pool.get_connection.assert_called_once_with('foo')

    def test_add_connection(self):
        db_connection_pool = Mock()

        dbconnection.register_db_connection_pool(db_connection_pool)
        dbconnection.add_connection('foo')

        db_connection_pool.add_connection.assert_called_once_with('foo')

    def test_add_connection_as(self):
        db_connection_pool = Mock()

        dbconnection.register_db_connection_pool(db_connection_pool)
        dbconnection.add_connection_as('foo', 'bar')

        db_connection_pool.add_connection_as.assert_called_once_with('foo', 'bar')

    def test_function_raise_exception_if_nothing_registered(self):
        self.assertRaises(Exception, dbconnection.add_connection, 'foo')
        self.assertRaises(Exception, dbconnection.add_connection_as, 'foo', 'bar')
        self.assertRaises(Exception, dbconnection.get_connection, 'foo')
