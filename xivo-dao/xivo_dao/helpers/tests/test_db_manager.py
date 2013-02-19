# -*- coding: UTF-8 -*-

import unittest
from mock import patch, Mock, ANY
from xivo_dao.helpers import config
from xivo_dao.helpers import db_manager
from sqlalchemy.exc import InvalidRequestError


class TestDBManager(unittest.TestCase):

    def tearDown(self):
        db_manager.dbsession = None
        db_manager.xivo_dbsession = None

    @patch('xivo_dao.helpers.db_manager.create_engine')
    @patch('xivo_dao.helpers.db_manager.sessionmaker')
    def test_connect(self, sessionmaker_mock, create_engine_mock):
        engine_mock = Mock()
        sessionmaker_value = Mock()
        session_mock = Mock()

        create_engine_mock.return_value = engine_mock
        sessionmaker_mock.return_value = sessionmaker_value
        sessionmaker_value.return_value = session_mock

        db_name = db_manager.XIVO_DB_NAME
        result = db_manager.connect(db_name)

        create_engine_mock.assert_called_with(config.XIVO_DB_URI, echo=ANY)
        sessionmaker_mock.assert_called_with()
        self.assertEquals(result, session_mock)

        db_name = db_manager.ASTERISK_DB_NAME
        result = db_manager.connect(db_name)

        create_engine_mock.assert_called_with(config.DB_URI, echo=ANY)
        sessionmaker_mock.assert_called_with()
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

        result1 = db_manager.session(db_manager.ASTERISK_DB_NAME)
        self.assertEquals(result1, dbsession)

        result2 = db_manager.session(db_manager.ASTERISK_DB_NAME)
        self.assertEquals(result2, dbsession)

    @patch('xivo_dao.helpers.db_manager.connect')
    def test_session_returns_different_sessions_for_different_db(self, connect_mock):
        def connect_side_effect(db_name):
            result = Mock()
            result.db_name = db_name
            return result

        connect_mock.side_effect = connect_side_effect

        result1 = db_manager.session(db_manager.ASTERISK_DB_NAME)
        self.assertEquals(result1.db_name, db_manager.ASTERISK_DB_NAME)

        result2 = db_manager.session(db_manager.XIVO_DB_NAME)
        self.assertEquals(result2.db_name, db_manager.XIVO_DB_NAME)

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

    @patch('xivo_dao.helpers.db_manager.session')
    def test_xivo_daosession_starts_and_stops_a_session(self, session_creator_mock):
        function_mock = Mock()
        function_mock.__name__ = "tested_function"

        function_result = Mock()
        function_mock.return_value = function_result

        session_mock = Mock()
        session_creator_mock.return_value = session_mock

        decorated_function = db_manager.xivo_daosession(function_mock)

        result = decorated_function('arg1', 'arg2', arg3='arg3')

        session_mock.commit.assert_called_once_with()
        function_mock.assert_called_once_with(session_mock, 'arg1', 'arg2', arg3='arg3')

        self.assertEquals(result, function_result)

    @patch('xivo_dao.helpers.db_manager.connect')
    def test_xivo_daosession_reconnects_after_connection_error(self, connect_mock):
        function_mock = Mock()
        function_mock.__name__ = "tested_function"

        function_result = Mock()
        function_mock.side_effect = [InvalidRequestError(), function_result]

        broken_session = Mock()
        new_session = Mock()
        connect_mock.side_effect = None
        connect_mock.side_effect = [broken_session, new_session]

        decorated_function = db_manager.xivo_daosession(function_mock)

        result = decorated_function('arg1')

        new_session.commit.assert_called_once_with()
        function_mock.assert_called_with(new_session, 'arg1')

        self.assertEquals(result, function_result)
