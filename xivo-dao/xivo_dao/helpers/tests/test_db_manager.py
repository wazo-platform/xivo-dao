# -*- coding: UTF-8 -*-

import unittest
from mock import patch, ANY
from xivo import config
from xivo.db_manager import DBManager


class TestDBManager(unittest.TestCase):

    @patch('xivo_dao.alchemy.dbconnection.register_db_connection_pool')
    @patch('xivo_dao.alchemy.dbconnection.add_connection_as')
    def test_connect(self, add_connection_as, register_db_connection_pool):
        db_manager = DBManager()

        db_manager.connect()

        register_db_connection_pool.assert_called_once_with(ANY)
        add_connection_as.assert_called_once_with(config.DB_URI, 'asterisk')

    @patch('xivo_dao.alchemy.dbconnection.unregister_db_connection_pool')
    def test_disconnect(self, unregister_db_connection_pool):
        db_manager = DBManager()

        db_manager.disconnect()

        unregister_db_connection_pool.assert_called_once_with()

    def test_reconnect(self):
        db_manager = DBManager()

        with patch.object(db_manager, 'disconnect') as disconnect:
            with patch.object(db_manager, 'connect') as connect:
                db_manager.reconnect()

                disconnect.assert_called_once_with()
                connect.assert_called_once_with()
