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

from hamcrest import assert_that
from hamcrest import equal_to
from mock import sentinel
from unittest import TestCase

from xivo_dao.tests.helpers.session import mocked_dao_session
from xivo_dao.helpers.db_manager import daosession


class TestSession(TestCase):

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
