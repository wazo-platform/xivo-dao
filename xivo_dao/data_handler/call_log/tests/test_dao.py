# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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
from hamcrest import assert_that, equal_to, has_length, contains_inanyorder, has_property, contains, all_of
from mock import patch
from sqlalchemy.exc import SQLAlchemyError

from xivo_dao.alchemy.call_log import CallLog as CallLogSchema
from xivo_dao.alchemy.cel import CEL as CELSchema
from xivo_dao.data_handler.call_log import dao as call_log_dao
from xivo_dao.data_handler.call_log.model import CallLog
from xivo_dao.data_handler.exception import DataError
from xivo_dao.tests.helpers.session import mocked_dao_session
from xivo_dao.tests.test_dao import DAOTestCase


class TestCallLogDAO(DAOTestCase):

    def setUp(self):
        super(TestCallLogDAO, self).setUp()
        self.db_converter_patcher = patch('xivo_dao.data_handler.call_log.model.db_converter')
        self.db_converter = self.db_converter_patcher.start()
        self.call_log_rows = []
        self.db_converter.to_source.side_effect = lambda: self.call_log_rows.pop(0)

    def tearDown(self):
        self.db_converter_patcher.stop()
        super(TestCallLogDAO, self).tearDown()

    def test_find_all_history_for_phone_limited(self):
        identity = "sip/131313"
        limit = 2
        call_logs = call_log_0, call_log_1, _ = (
            self._mock_call_log(date=datetime(2015, 1, 1, 13, 10, 30), destination_line_identity=identity, answered=True),
            self._mock_call_log(date=datetime(2014, 1, 1, 13, 11, 30), destination_line_identity=identity, answered=True),
            self._mock_call_log(date=datetime(2013, 1, 1, 13, 12, 30), destination_line_identity=identity, answered=True),
        )

        call_log_dao.create_from_list(call_logs)

        result = call_log_dao.find_all_history_for_phone(identity, limit)

        assert_that(result, has_length(2))

        assert_that(result[0].date, equal_to(call_log_0.date))
        assert_that(result[0].destination_line_identity, equal_to(call_log_0.destination_line_identity))
        assert_that(result[0].answered, equal_to(call_log_0.answered))

        assert_that(result[1].date, equal_to(call_log_1.date))
        assert_that(result[1].destination_line_identity, equal_to(call_log_1.destination_line_identity))
        assert_that(result[1].answered, equal_to(call_log_1.answered))


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

    def test_find_all_answered_for_phone_no_calls(self):
        identity = "sip/131313"
        limit = 10

        result = call_log_dao.find_all_answered_for_phone(identity, limit)

        assert_that(result, has_length(0))

    def test_find_all_missed_calls_for_phone_no_calls(self):
        identity = "sip/131313"
        limit = 10

        result = call_log_dao.find_all_missed_for_phone(identity, limit)

        assert_that(result, has_length(0))

    def test_find_all_missed_for_phone_limited(self):
        identity = "sip/131313"
        limit = 2
        call_logs = _, call_log_1, call_log_2, call_log_3, _ = (self._mock_call_log(source_line_identity=identity),
                                                                self._mock_call_log(date=datetime(2015, 1, 1, 13), destination_line_identity=identity, answered=False),
                                                                self._mock_call_log(date=datetime(2012, 1, 1, 13), destination_line_identity=identity, answered=False),
                                                                self._mock_call_log(date=datetime(2014, 1, 1, 13), destination_line_identity=identity, answered=False),
                                                                self._mock_call_log(source_line_identity=identity))

        call_log_dao.create_from_list(call_logs)

        result = call_log_dao.find_all_missed_for_phone(identity, limit)

        assert_that(result, has_length(2))
        assert_that(result[0].date, equal_to(call_log_1.date))
        assert_that(result[0].destination_line_identity, equal_to(call_log_1.destination_line_identity))
        assert_that(result[0].answered, equal_to(call_log_1.answered))
        assert_that(result[1].date, equal_to(call_log_3.date))
        assert_that(result[1].destination_line_identity, equal_to(call_log_3.destination_line_identity))
        assert_that(result[1].answered, equal_to(call_log_3.answered))

    def test_find_all_outgoing_calls_for_phone_no_calls(self):
        identity = "sip/131313"
        limit = 10

        result = call_log_dao.find_all_outgoing_for_phone(identity, limit)

        assert_that(result, has_length(0))

    def test_find_all_outgoing_for_phone_limited(self):
        identity = "sip/131313"
        limit = 2
        call_logs = _, call_log_1, call_log_2, call_log_3, _ = (self._mock_call_log(),
                                                                self._mock_call_log(date=datetime(2015, 1, 1, 13), source_line_identity=identity),
                                                                self._mock_call_log(date=datetime(2011, 1, 1, 13), source_line_identity=identity),
                                                                self._mock_call_log(date=datetime(2015, 2, 1, 13), source_line_identity=identity),
                                                                self._mock_call_log())

        call_log_dao.create_from_list(call_logs)

        result = call_log_dao.find_all_outgoing_for_phone(identity, limit)

        assert_that(result, has_length(2))
        assert_that(result[0].date, equal_to(call_log_3.date))
        assert_that(result[1].date, equal_to(call_log_1.date))
        assert_that(result[0].source_line_identity, equal_to(call_log_3.source_line_identity))
        assert_that(result[1].source_line_identity, equal_to(call_log_1.source_line_identity))

    @mocked_dao_session
    def test_create_call_log(self, session):
        expected_id = 13
        call_log = self._mock_call_log(id=expected_id)
        call_log_id = call_log_dao.create_call_log(session, call_log)

        session.add.assert_called_once()
        session.flush.assert_called_once()
        assert_that(call_log_id, equal_to(expected_id))

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

    @mocked_dao_session
    @patch('xivo_dao.data_handler.call_log.dao.create_call_log')
    def test_create_from_list_db_error(self, session, create_call_log):
        session.commit.side_effect = SQLAlchemyError()
        create_call_log.return_value = 13

        call_logs = (self._mock_call_log(), self._mock_call_log())

        self.assertRaises(DataError, call_log_dao.create_from_list, call_logs)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_delete_all(self):
        call_logs = (self._mock_call_log(), self._mock_call_log())
        call_log_dao.create_from_list(call_logs)

        call_log_dao.delete_all()

        call_log_rows = self.session.query(CallLogSchema).all()
        assert_that(call_log_rows, has_length(0))

    @mocked_dao_session
    def test_delete_all_db_error(self, session):
        session.commit.side_effect = SQLAlchemyError()

        self.assertRaises(DataError, call_log_dao.delete_all)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_delete_from_list(self):
        id_1, id_2, id_3 = [42, 43, 44]
        call_logs = (self._mock_call_log(id=id_1), self._mock_call_log(id=id_2), self._mock_call_log(id=id_3))
        call_log_dao.create_from_list(call_logs)

        call_log_dao.delete_from_list([id_1, id_3])

        call_log_rows = self.session.query(CallLogSchema).all()
        assert_that(call_log_rows, contains(has_property('id', id_2)))

    @mocked_dao_session
    def test_delete_from_list_db_error(self, session):
        session.commit.side_effect = SQLAlchemyError()

        self.assertRaises(DataError, call_log_dao.delete_from_list, [1, 2])
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def _mock_call_log(self, cel_ids=None, date=None, id=None, source_line_identity=None, destination_line_identity=None, answered=False):
        if cel_ids is None:
            cel_ids = ()
        if date is None:
            date = datetime.now()
        call_log = CallLog(id=id,
                           date=date,
                           duration=timedelta(0),
                           source_line_identity=source_line_identity,
                           destination_line_identity=destination_line_identity,
                           answered=answered)
        call_log.add_related_cels(cel_ids)
        self.call_log_rows.append(CallLogSchema(id=id,
                                                date=date,
                                                source_line_identity=source_line_identity,
                                                destination_line_identity=destination_line_identity,
                                                answered=answered,
                                                duration=timedelta(3)))
        return call_log
