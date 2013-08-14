# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from datetime import datetime, timedelta
from hamcrest import assert_that, has_length
from mock import Mock, patch
from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.alchemy.call_log import CallLog as CallLogSchema
from xivo_dao.data_handler.call_log import dao as call_log_dao
from xivo_dao.data_handler.call_log.model import CallLog
from xivo_dao.data_handler.exception import ElementCreationError, ElementDeletionError
from xivo_dao.tests.test_dao import DAOTestCase


class TestCallLogDAO(DAOTestCase):

    tables = [
        CallLogSchema,
    ]

    def setUp(self):
        self.empty_tables()

    def tearDown(self):
        pass

    def test_create_all(self):
        call_logs = call_log_1, call_log_2 = [CallLog(date=datetime.today(), duration=timedelta(0)),
                                              CallLog(date=datetime.today(), duration=timedelta(1))]

        call_log_dao.create_all(call_logs)

        call_log_rows = self.session.query(CallLogSchema).all()
        assert_that(call_log_rows, has_length(2))

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_create_all_db_error(self, session_init):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        session_init.return_value = session

        call_logs = call_log_1, call_log_2 = [CallLog(date=datetime.today(), duration=timedelta(0)),
                                              CallLog(date=datetime.today(), duration=timedelta(1))]

        self.assertRaises(ElementCreationError, call_log_dao.create_all, call_logs)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_delete_all(self):
        call_logs = [CallLog(date=datetime.today(), duration=timedelta(0)),
                     CallLog(date=datetime.today(), duration=timedelta(1))]
        call_log_dao.create_all(call_logs)

        call_log_dao.delete_all()

        call_log_rows = self.session.query(CallLogSchema).all()
        assert_that(call_log_rows, has_length(0))

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_delete_all_db_error(self, session_init):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        session_init.return_value = session

        self.assertRaises(ElementDeletionError, call_log_dao.delete_all)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()
