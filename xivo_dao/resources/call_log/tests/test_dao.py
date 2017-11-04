# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from datetime import datetime as dt
from datetime import timedelta as td
from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import contains
from hamcrest import contains_inanyorder
from hamcrest import empty
from hamcrest import equal_to
from hamcrest import has_length
from hamcrest import has_property
from hamcrest import is_

from xivo_dao.alchemy.call_log import CallLog
from xivo_dao.alchemy.cel import CEL
from xivo_dao.resources.call_log import dao as call_log_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestCallLogDAO(DAOTestCase):

    def setUp(self):
        super(TestCallLogDAO, self).setUp()
        self.call_log_rows = []

    def test_find_all_history_for_phones_limited(self):
        identities = ["sip/131313", "sip/1234"]
        limit = 7

        self.add_call_log(date=dt(2015, 1, 1, 13, 10, 10), destination_line_identity=identities[0])
        c1 = self.add_call_log(date=dt(2015, 1, 1, 13, 11, 10), destination_line_identity=identities[1])
        c2 = self.add_call_log(date=dt(2015, 1, 1, 13, 12, 10), destination_line_identity=identities[0])
        c3 = self.add_call_log(date=dt(2015, 1, 1, 13, 12, 30),
                               date_answer=dt(2015, 1, 1, 13, 12, 30),
                               destination_line_identity=identities[1])
        c4 = self.add_call_log(date=dt(2015, 1, 1, 13, 10, 30),
                               date_answer=dt(2015, 1, 1, 13, 10, 30),
                               destination_line_identity=identities[1])
        c5 = self.add_call_log(date=dt(2015, 1, 1, 13, 11, 30),
                               date_answer=dt(2015, 1, 1, 13, 11, 30),
                               destination_line_identity=identities[0])
        self.add_call_log(date=dt(2015, 1, 1, 13, 10, 20), source_line_identity=identities[0])
        c7 = self.add_call_log(date=dt(2015, 1, 1, 13, 11, 20), source_line_identity=identities[1])
        c8 = self.add_call_log(date=dt(2015, 1, 1, 13, 12, 20), source_line_identity=identities[1])

        result = call_log_dao.find_all_history_for_phones(identities, limit)

        assert_that(result, contains(
            all_of(has_property('date', c3.date),
                   has_property('destination_line_identity', c3.destination_line_identity),
                   has_property('date_answer', c3.date_answer)),
            all_of(has_property('date', c8.date),
                   has_property('destination_line_identity', c8.destination_line_identity),
                   has_property('date_answer', c8.date_answer)),
            all_of(has_property('date', c2.date),
                   has_property('destination_line_identity', c2.destination_line_identity),
                   has_property('date_answer', c2.date_answer)),
            all_of(has_property('date', c5.date),
                   has_property('destination_line_identity', c5.destination_line_identity),
                   has_property('date_answer', c5.date_answer)),
            all_of(has_property('date', c7.date),
                   has_property('destination_line_identity', c7.destination_line_identity),
                   has_property('date_answer', c7.date_answer)),
            all_of(has_property('date', c1.date),
                   has_property('destination_line_identity', c1.destination_line_identity),
                   has_property('date_answer', c1.date_answer)),
            all_of(has_property('date', c4.date),
                   has_property('destination_line_identity', c4.destination_line_identity),
                   has_property('date_answer', c4.date_answer))))

    def test_find_all_history_for_phones_no_calls(self):
        result = call_log_dao.find_all_history_for_phones(['sip/foobar'], 42)

        assert_that(result, is_(empty()))

    def test_find_all_not_found(self):
        expected_result = []

        result = call_log_dao.find_all()

        assert_that(result, equal_to(expected_result))

    def test_find_all_found(self):
        self.add_call_log()
        self.add_call_log()

        result = call_log_dao.find_all()

        assert_that(result, has_length(2))

    def test_find_all_in_period_no_result(self):
        start, end = dt(2013, 1, 1), dt(2013, 2, 1)

        result = call_log_dao.find_all_in_period(start, end)

        assert_that(result, empty())

    def test_find_all_in_period_start_after_end(self):
        self.add_call_log(date=dt(2017, 4, 13, 12))
        start, end = dt(2017, 4, 14), dt(2017, 4, 13)

        result = call_log_dao.find_all_in_period(start, end)

        assert_that(result, empty())

    def test_find_all_in_period_start_only(self):
        self.add_call_log(date=dt(2013, 1, 1))
        call_log_2 = self.add_call_log(date=dt(2013, 1, 2))

        result = call_log_dao.find_all_in_period(start=dt(2013, 1, 2))

        assert_that(result, contains(has_property('date', call_log_2.date)))

    def test_find_all_in_period_end_only(self):
        call_log_1 = self.add_call_log(date=dt(2013, 1, 1))
        self.add_call_log(date=dt(2013, 1, 2))

        result = call_log_dao.find_all_in_period(end=dt(2013, 1, 2))

        assert_that(result, contains(has_property('date', call_log_1.date)))

    def test_find_all_in_period_found(self):
        self.add_call_log(date=dt(2012, 1, 1, 13))
        call_log_1 = self.add_call_log(date=dt(2013, 1, 1, 13))
        call_log_2 = self.add_call_log(date=dt(2013, 1, 2, 13))
        self.add_call_log(date=dt(2014, 1, 1, 13))

        start = dt(2013, 1, 1, 12)
        end = dt(2013, 1, 3, 12)
        result = call_log_dao.find_all_in_period(start, end)

        assert_that(result, has_length(2))
        assert_that(result, contains_inanyorder(has_property('date', call_log_1.date),
                                                has_property('date', call_log_2.date)))

    def test_find_all_in_order(self):
        call_log_1 = self.add_call_log(date=dt(2012, 1, 1))
        call_log_2 = self.add_call_log(date=dt(2013, 1, 1))
        call_log_3 = self.add_call_log(date=dt(2014, 1, 1))

        result_asc = call_log_dao.find_all_in_period(order='date', direction='asc')
        result_desc = call_log_dao.find_all_in_period(order='date', direction='desc')

        assert_that(result_asc, contains(has_property('date', call_log_1.date),
                                         has_property('date', call_log_2.date),
                                         has_property('date', call_log_3.date)))
        assert_that(result_desc, contains(has_property('date', call_log_3.date),
                                          has_property('date', call_log_2.date),
                                          has_property('date', call_log_1.date)))

    def test_find_all_pagination(self):
        self.add_call_log(date=dt(2012, 1, 1))
        self.add_call_log(date=dt(2013, 1, 1))
        self.add_call_log(date=dt(2014, 1, 1))

        result_unpaginated = call_log_dao.find_all_in_period()
        result_paginated = call_log_dao.find_all_in_period(limit=1, offset=1)

        assert_that(result_paginated, contains(has_property('date', result_unpaginated[1].date)))

    def test_create_call_log(self):
        expected_id = 13
        call_log = self.add_call_log(id=expected_id)

        call_log_dao.create_call_log(self.session, call_log)

        call_log_rows = self.session.query(CallLog).all()
        assert_that(call_log_rows, contains(has_property('id', expected_id)))

    def test_create_from_list(self):
        cel_id_1, cel_id_2 = self.add_cel(), self.add_cel()
        cel_id_3, cel_id_4 = self.add_cel(), self.add_cel()
        call_log_1 = CallLog(date=dt.now())
        call_log_1.cel_ids = [cel_id_1, cel_id_2]
        call_log_2 = CallLog(date=dt.now())
        call_log_2.cel_ids = [cel_id_3, cel_id_4]

        call_log_dao.create_from_list([call_log_1, call_log_2])

        call_log_rows = self.session.query(CallLog).all()
        assert_that(call_log_rows, has_length(2))

        call_log_id_1, call_log_id_2 = [call_log.id for call_log in call_log_rows]

        cel_rows = self.session.query(CEL).all()
        assert_that(cel_rows, contains_inanyorder(
            all_of(has_property('id', cel_id_1), has_property('call_log_id', call_log_id_1)),
            all_of(has_property('id', cel_id_2), has_property('call_log_id', call_log_id_1)),
            all_of(has_property('id', cel_id_3), has_property('call_log_id', call_log_id_2)),
            all_of(has_property('id', cel_id_4), has_property('call_log_id', call_log_id_2))))

    def test_delete_from_list(self):
        id_1, id_2, id_3 = [42, 43, 44]
        self.add_call_log(id=id_1)
        self.add_call_log(id=id_2)
        self.add_call_log(id=id_3)

        call_log_dao.delete_from_list([id_1, id_3])

        call_log_rows = self.session.query(CallLog).all()
        assert_that(call_log_rows, contains(has_property('id', id_2)))

    def test_delete_all(self):
        self.add_call_log()
        self.add_call_log()
        self.add_call_log()

        call_log_dao.delete()

        result = self.session.query(CallLog).all()
        assert_that(result, empty())

    def test_delete_older(self):
        now = dt.now()
        older = now - td(hours=1)
        exclude_time = now - td(hours=2)
        self.add_call_log(date=now)
        call_log_2 = self.add_call_log(date=exclude_time)
        self.add_call_log(date=now)

        call_log_dao.delete(older=older)

        result = self.session.query(CallLog).all()
        assert_that(result, contains(call_log_2))
