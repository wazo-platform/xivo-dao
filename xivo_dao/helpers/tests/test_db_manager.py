# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

import unittest
from mock import patch, Mock, sentinel, call
from xivo_dao.helpers import db_manager
from sqlalchemy.exc import InterfaceError


class TestDBManager(unittest.TestCase):

    @patch('xivo_dao.helpers.db_manager._execute_with_session')
    def test_daosession_decorator(self, execute_mock):
        execute_mock.return_value = sentinel

        function_mock = Mock()
        function_mock.__name__ = "tested_function"
        args = ('arg1', 'arg2')
        kwargs = {'arg3': 'arg3'}

        decorated_function = db_manager.daosession(function_mock)

        result = decorated_function(*args, **kwargs)

        execute_mock.assert_called_once_with(db_manager.AsteriskSession, function_mock, args, kwargs)
        self.assertEqual(result, sentinel)

    @patch('xivo_dao.helpers.db_manager._execute_with_session')
    def testxivo_daosession_decorator(self, execute_mock):
        execute_mock.return_value = sentinel

        function_mock = Mock()
        function_mock.__name__ = "tested_function"
        args = ('arg1', 'arg2')
        kwargs = {'arg3': 'arg3'}

        decorated_function = db_manager.xivo_daosession(function_mock)

        result = decorated_function(*args, **kwargs)

        execute_mock.assert_called_once_with(db_manager.XivoSession, function_mock, args, kwargs)
        self.assertEqual(result, sentinel)

    @patch('xivo_dao.helpers.db_manager._apply_and_flush')
    def test_execute_with_session_with_reconnection(self, apply_and_flush_mock):
        function_mock = Mock()
        args = ()
        kwargs = {}

        broken_session = Mock()
        new_session = Mock()
        session_class_mock = Mock()
        session_class_mock.side_effect = [broken_session, new_session]

        apply_and_flush_mock.side_effect = [InterfaceError(None, None, None, None), sentinel]

        result = db_manager._execute_with_session(session_class_mock, function_mock, args, kwargs)

        expected_calls = [
            call(function_mock, broken_session, args, kwargs),
            call(function_mock, new_session, args, kwargs),
        ]
        self.assertEqual(apply_and_flush_mock.call_args_list, expected_calls)
        self.assertEqual(result, sentinel)

    def test_apply_and_flush(self):
        function = Mock()
        function.return_value = sentinel
        session = Mock()
        args = (1,)
        kwargs = {'foo': 2}

        result = db_manager._apply_and_flush(function, session, args, kwargs)

        function.assert_called_once_with(session, *args, **kwargs)
        session.flush.assert_called_once_with()
        self.assertEqual(result, sentinel)
