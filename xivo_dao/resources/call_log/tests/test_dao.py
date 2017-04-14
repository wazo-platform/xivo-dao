# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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

from datetime import datetime as dt
from datetime import timedelta
from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import contains
from hamcrest import contains_inanyorder
from hamcrest import equal_to
from hamcrest import empty
from hamcrest import has_length
from hamcrest import has_property
from hamcrest import is_

from mock import patch

from xivo_dao.alchemy.call_log import CallLog as CallLogSchema
from xivo_dao.alchemy.cel import CEL as CELSchema
from xivo_dao.resources.call_log import dao as call_log_dao
from xivo_dao.resources.call_log.model import CallLog
from xivo_dao.tests.test_dao import DAOTestCase


class TestCallLogDAO(DAOTestCase):

    def setUp(self):
        super(TestCallLogDAO, self).setUp()
        self.db_converter_patcher = patch('xivo_dao.resources.call_log.model.db_converter')
        self.db_converter = self.db_converter_patcher.start()
        self.call_log_rows = []
        self.db_converter.to_source.side_effect = lambda: self.call_log_rows.pop(0)

    def tearDown(self):
        self.db_converter_patcher.stop()
        super(TestCallLogDAO, self).tearDown()

    def test_find_all_history_for_phones_limited(self):
        identities = ["sip/131313", "sip/1234"]
        limit = 7

        call_logs = c0, c1, c2, c3, c4, c5, c6, c7, c8 = (
            self._mock_call_log(date=dt(2015, 1, 1, 13, 10, 10),
                                destination_line_identity=identities[0], answered=False),
            self._mock_call_log(date=dt(2015, 1, 1, 13, 11, 10),
                                destination_line_identity=identities[1], answered=False),
            self._mock_call_log(date=dt(2015, 1, 1, 13, 12, 10),
                                destination_line_identity=identities[0], answered=False),
            self._mock_call_log(date=dt(2015, 1, 1, 13, 12, 30),
                                destination_line_identity=identities[1], answered=True),
            self._mock_call_log(date=dt(2015, 1, 1, 13, 10, 30),
                                destination_line_identity=identities[1], answered=True),
            self._mock_call_log(date=dt(2015, 1, 1, 13, 11, 30),
                                destination_line_identity=identities[0], answered=True),
            self._mock_call_log(date=dt(2015, 1, 1, 13, 10, 20), source_line_identity=identities[0]),
            self._mock_call_log(date=dt(2015, 1, 1, 13, 11, 20), source_line_identity=identities[1]),
            self._mock_call_log(date=dt(2015, 1, 1, 13, 12, 20), source_line_identity=identities[1]),
        )

        call_log_dao.create_from_list(call_logs)

        result = call_log_dao.find_all_history_for_phones(identities, limit)

        assert_that(result, contains(
            all_of(has_property('date', c3.date),
                   has_property('destination_line_identity', c3.destination_line_identity),
                   has_property('answered', c3.answered)),
            all_of(has_property('date', c8.date),
                   has_property('destination_line_identity', c8.destination_line_identity),
                   has_property('answered', c8.answered)),
            all_of(has_property('date', c2.date),
                   has_property('destination_line_identity', c2.destination_line_identity),
                   has_property('answered', c2.answered)),
            all_of(has_property('date', c5.date),
                   has_property('destination_line_identity', c5.destination_line_identity),
                   has_property('answered', c5.answered)),
            all_of(has_property('date', c7.date),
                   has_property('destination_line_identity', c7.destination_line_identity),
                   has_property('answered', c7.answered)),
            all_of(has_property('date', c1.date),
                   has_property('destination_line_identity', c1.destination_line_identity),
                   has_property('answered', c1.answered)),
            all_of(has_property('date', c4.date),
                   has_property('destination_line_identity', c4.destination_line_identity),
                   has_property('answered', c4.answered))))

    def test_find_all_history_for_phones_no_calls(self):
        result = call_log_dao.find_all_history_for_phones(['sip/foobar'], 42)

        assert_that(result, is_(empty()))

    def test_find_all_not_found(self):
        expected_result = []

        result = call_log_dao.find_all()

        assert_that(result, equal_to(expected_result))

    def test_find_all_found(self):
        call_logs = (self._mock_call_log(), self._mock_call_log())
        call_log_dao.create_from_list(call_logs)

        result = call_log_dao.find_all()

        assert_that(result, has_length(2))

    def test_find_all_in_period_no_result(self):
        start, end = dt(2013, 1, 1), dt(2013, 2, 1)

        result = call_log_dao.find_all_in_period(start, end)

        assert_that(result, empty())

    def test_find_all_in_period_start_after_end(self):
        self._mock_call_log(date=dt(2017, 4, 13, 12))
        start, end = dt(2017, 4, 14), dt(2017, 4, 13)

        result = call_log_dao.find_all_in_period(start, end)

        assert_that(result, empty())

    def test_find_all_in_period_start_only(self):
        call_logs = call_log_1, call_log_2 = (self._mock_call_log(date=dt(2013, 1, 1)),
                                              self._mock_call_log(date=dt(2013, 1, 2)))
        call_log_dao.create_from_list(call_logs)

        result = call_log_dao.find_all_in_period(start=dt(2013, 1, 2))

        assert_that(result, contains(has_property('date', call_log_2.date)))

    def test_find_all_in_period_end_only(self):
        call_logs = call_log_1, call_log_2 = (self._mock_call_log(date=dt(2013, 1, 1)),
                                              self._mock_call_log(date=dt(2013, 1, 2)))
        call_log_dao.create_from_list(call_logs)

        result = call_log_dao.find_all_in_period(end=dt(2013, 1, 2))

        assert_that(result, contains(has_property('date', call_log_1.date)))

    def test_find_all_in_period_found(self):
        call_logs = _, call_log_1, call_log_2, _ = (self._mock_call_log(date=dt(2012, 1, 1, 13)),
                                                    self._mock_call_log(date=dt(2013, 1, 1, 13)),
                                                    self._mock_call_log(date=dt(2013, 1, 2, 13)),
                                                    self._mock_call_log(date=dt(2014, 1, 1, 13)))
        start = dt(2013, 1, 1, 12)
        end = dt(2013, 1, 3, 12)
        call_log_dao.create_from_list(call_logs)

        result = call_log_dao.find_all_in_period(start, end)

        assert_that(result, has_length(2))
        assert_that(result, contains_inanyorder(has_property('date', call_log_1.date),
                                                has_property('date', call_log_2.date)))

    def test_create_call_log(self):
        expected_id = 13
        call_log = self._mock_call_log(id=expected_id)
        call_log_id = call_log_dao.create_call_log(self.session, call_log)

        assert_that(call_log_id, equal_to(expected_id))

        call_log_rows = self.session.query(CallLogSchema).all()
        assert_that(call_log_rows, contains(has_property('id', call_log_id)))

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

    def test_delete_all(self):
        call_logs = (self._mock_call_log(), self._mock_call_log())
        call_log_dao.create_from_list(call_logs)

        call_log_dao.delete_all()

        call_log_rows = self.session.query(CallLogSchema).all()
        assert_that(call_log_rows, has_length(0))

    def test_delete_from_list(self):
        id_1, id_2, id_3 = [42, 43, 44]
        call_logs = (self._mock_call_log(id=id_1), self._mock_call_log(id=id_2), self._mock_call_log(id=id_3))
        call_log_dao.create_from_list(call_logs)

        call_log_dao.delete_from_list([id_1, id_3])

        call_log_rows = self.session.query(CallLogSchema).all()
        assert_that(call_log_rows, contains(has_property('id', id_2)))

    def _mock_call_log(self, cel_ids=None, date=None, id=None, source_line_identity=None, destination_line_identity=None, answered=False):
        if cel_ids is None:
            cel_ids = ()
        if date is None:
            date = dt.now()
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
