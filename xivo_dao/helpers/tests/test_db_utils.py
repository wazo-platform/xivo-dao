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
from mock import Mock

from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.helpers import db_utils


class CustomException(Exception):

    def __init__(self, element, error):
        self.element = element
        self.error = error


class TestCommitOrAbort(unittest.TestCase):

    def test_when_adding_a_row_then_row_is_committed(self):
        row = Mock()
        session = Mock()
        error = Mock()
        element = Mock()

        with db_utils.commit_or_abort(session, error, element):
            session.add(row)

        session.begin.assert_called_once_with(subtransactions=True)
        session.commit.assert_called_once_with()

    def test_given_row_added_when_error_then_rollback_and_error_raised(self):
        row = Mock()
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        element = Mock()

        with self.assertRaises(CustomException):
            with db_utils.commit_or_abort(session, CustomException, element):
                session.add(row)

        session.begin.assert_called_once_with(subtransactions=True)
        session.rollback.assert_called_once_with()

    def test_on_error_rollback_and_raise_if_no_error_supplied(self):
        row = Mock()
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()

        with self.assertRaises(SQLAlchemyError):
            with db_utils.commit_or_abort(session):
                session.add(row)

        session.begin.assert_called_once_with(subtransactions=True)
        session.rollback.assert_called_once_with()
