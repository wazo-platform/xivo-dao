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
from hamcrest import all_of, assert_that, contains, contains_inanyorder, equal_to, has_length, has_property
from mock import Mock, patch
from sqlalchemy.exc import SQLAlchemyError

from xivo_dao.alchemy.call_log import CallLog as CallLogSchema
from xivo_dao.alchemy.cel import CEL as CELSchema
from xivo_dao.data_handler.call_log import dao as call_log_dao
from xivo_dao.data_handler.call_log.model import CallLog
from xivo_dao.data_handler.exception import ElementCreationError, ElementDeletionError
from xivo_dao.tests.test_dao import DAOTestCase


class TestCallLogDAO(DAOTestCase):

    tables = [
        CallLogSchema,
        CELSchema
    ]

    def setUp(self):
        self.empty_tables()
        self.db_converter_patcher = patch('xivo_dao.data_handler.call_log.model.db_converter')
        self.db_converter = self.db_converter_patcher.start()
        self.call_log_rows = []
        self.db_converter.to_source.side_effect = lambda: self.call_log_rows.pop(0)

    def tearDown(self):
        self.db_converter_patcher.stop()

    def test_find_all_not_found(self):
        expected_result = []

        result = call_log_dao.find_all()

        assert_that(result, equal_to(expected_result))

    def test_find_all_found(self):
        call_logs = (self._mock_call_log(), self._mock_call_log())
        call_log_dao.create_from_list(call_logs)

        result = call_log_dao.find_all()

        assert_that(result, has_length(2))

    def test_find_all_in_period_not_found(self):
        expected_result = []
        start, end = datetime(2013, 1, 1), datetime(2013, 2, 1)

        result = call_log_dao.find_all_in_period(start, end)

        assert_that(result, equal_to(expected_result))

    def test_find_all_in_period_found(self):
        call_logs = _, call_log_1, call_log_2, _ = (self._mock_call_log(date=datetime(2012, 1, 1, 13)),
                                                    self._mock_call_log(date=datetime(2013, 1, 1, 13)),
                                                    self._mock_call_log(date=datetime(2013, 1, 2, 13)),
                                                    self._mock_call_log(date=datetime(2014, 1, 1, 13)))
        start = datetime(2013, 1, 1, 12)
        end = datetime(2013, 1, 3, 12)
        call_log_dao.create_from_list(call_logs)

        result = call_log_dao.find_all_in_period(start, end)

        assert_that(result, has_length(2))
        assert_that(result, contains_inanyorder(has_property('date', call_log_1.date),
                                                has_property('date', call_log_2.date)))

    def test_create_from_list(self):
        cel_id_1, cel_id_2 = self.add_cel(), self.add_cel()
        cel_id_3, cel_id_4 = self.add_cel(), self.add_cel()
        call_logs = call_log_1, call_log_2 = (self._mock_call_log((cel_id_1, cel_id_2)),
                                              self._mock_call_log((cel_id_3, cel_id_4)))

        call_log_dao.create_from_list(call_logs)

        call_log_rows = self.session.query(CallLogSchema).all()
        assert_that(call_log_rows, has_length(2))

        call_log_id_1, call_log_id_2 = [call_log.id for call_log in call_log_rows]

        cel_rows = self.session.query(CELSchema).all()
        assert_that(cel_rows, contains_inanyorder(
            all_of(has_property('id', cel_id_1), has_property('call_log_id', call_log_id_1)),
            all_of(has_property('id', cel_id_2), has_property('call_log_id', call_log_id_1)),
            all_of(has_property('id', cel_id_3), has_property('call_log_id', call_log_id_2)),
            all_of(has_property('id', cel_id_4), has_property('call_log_id', call_log_id_2))))

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_create_from_list_db_error(self, session_init):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        session_init.return_value = session

        call_logs = (self._mock_call_log(), self._mock_call_log())

        self.assertRaises(ElementCreationError, call_log_dao.create_from_list, call_logs)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_delete_all(self):
        call_logs = (self._mock_call_log(), self._mock_call_log())
        call_log_dao.create_from_list(call_logs)

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

    def test_delete_from_list(self):
        id_1, id_2, id_3 = [42, 43, 44]
        call_logs = (self._mock_call_log(id=id_1), self._mock_call_log(id=id_2), self._mock_call_log(id=id_3))
        call_log_dao.create_from_list(call_logs)

        call_log_dao.delete_from_list([id_1, id_3])

        call_log_rows = self.session.query(CallLogSchema).all()
        assert_that(call_log_rows, contains(has_property('id', id_2)))

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_delete_from_list_db_error(self, session_init):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        session_init.return_value = session

        self.assertRaises(ElementDeletionError, call_log_dao.delete_from_list, [1, 2])
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def _mock_call_log(self, cel_ids=None, date=None, id=None):
        if cel_ids is None:
            cel_ids = ()
        if date is None:
            date = datetime.now()
        call_log = CallLog(id=id, date=date, duration=timedelta(0))
        call_log.add_related_cels(cel_ids)
        self.call_log_rows.append(CallLogSchema(id=id, date=date, duration=timedelta(3)))
        return call_log
