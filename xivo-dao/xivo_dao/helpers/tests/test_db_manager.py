# -*- coding: UTF-8 -*-

import unittest
from mock import patch, Mock, ANY
from xivo_dao.helpers import db_manager
from sqlalchemy.exc import InvalidRequestError

class TestDBManager(unittest.TestCase):

    def tearDown(self):
        db_manager.dbsession = None

    @patch('xivo_dao.helpers.db_manager.create_engine')
    @patch('xivo_dao.helpers.db_manager.sessionmaker')
    def test_connect(self, sessionmaker_mock, create_engine_mock):
        db_manager._DB_URI = "testuri"

        engine_mock = Mock()
        sessionmaker_value = Mock()
        session_mock = Mock()

        create_engine_mock.return_value = engine_mock
        sessionmaker_mock.return_value = sessionmaker_value
        sessionmaker_value.return_value = session_mock

        result = db_manager.connect()

        create_engine_mock.assert_called_once_with("testuri", echo=ANY)
        sessionmaker_mock.assert_called_once_with(bind=engine_mock)
        self.assertEquals(result, session_mock)

    @patch('xivo_dao.helpers.db_manager.session')
    def test_daosession_starts_and_stops_a_session(self, session_creator_mock):
        function_mock = Mock()
        function_mock.__name__ = "tested_function"

        function_result = Mock()
        function_mock.return_value = function_result

        session_mock = Mock()
        session_creator_mock.return_value = session_mock

        decorated_function = db_manager.daosession(function_mock)

        result = decorated_function('arg1', 'arg2', arg3='arg3')

        session_mock.commit.assert_called_once_with()
        function_mock.assert_called_once_with(session_mock, 'arg1', 'arg2', arg3='arg3')

        self.assertEquals(result, function_result)

    @patch('xivo_dao.helpers.db_manager.connect')
    def test_session_returns_same_session_when_called_twice(self, connect_mock):
        dbsession = Mock()
        connect_mock.return_value = dbsession

        result1 = db_manager.session()
        self.assertEquals(result1, dbsession)

        result2 = db_manager.session()
        self.assertEquals(result2, dbsession)


    @patch('xivo_dao.helpers.db_manager.connect')
    def test_daosession_reconnects_after_connection_error(self, connect_mock):
        function_mock = Mock()
        function_mock.__name__ = "tested_function"

        function_result = Mock()
        function_mock.side_effect = [InvalidRequestError(), function_result]

        broken_session = Mock()
        new_session = Mock()
        connect_mock.side_effect = [broken_session, new_session]

        decorated_function = db_manager.daosession(function_mock)

        result = decorated_function('arg1')

        new_session.commit.assert_called_once_with()
        function_mock.assert_called_with(new_session, 'arg1')

        self.assertEquals(result, function_result)

