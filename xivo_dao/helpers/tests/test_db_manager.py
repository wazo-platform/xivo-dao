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

from hamcrest import assert_that
from hamcrest import equal_to
from mock import patch, Mock, sentinel, call
from xivo_dao.helpers import db_manager
from xivo_dao.helpers.db_manager import mocked_dao_session
from xivo_dao.helpers.db_manager import daosession
from sqlalchemy.exc import InterfaceError


class TestDBManager(unittest.TestCase):

    @mocked_dao_session
    def test_daosession_decorator(self, session_mock):
        args = (sentinel.arg1, sentinel.arg2)
        kwargs = {'arg3': sentinel.arg3}

        @daosession
        def f(session, arg1, arg2, arg3):
            assert_that(session, equal_to(session_mock))
            assert_that(arg1, equal_to(sentinel.arg1))
            assert_that(arg2, equal_to(sentinel.arg2))
            assert_that(arg3, equal_to(sentinel.arg3))
            return sentinel.result

        result = f(*args, **kwargs)

        assert_that(result, equal_to(sentinel.result))

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
