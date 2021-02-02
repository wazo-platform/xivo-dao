# -*- coding: utf-8 -*-
# Copyright 2013-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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

from xivo_dao.alchemy.call_log import CallLog
from xivo_dao.alchemy.cel import CEL
from xivo_dao.resources.call_log import dao as call_log_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestCallLogDAO(DAOTestCase):

    def setUp(self):
        super(TestCallLogDAO, self).setUp()
        self.call_log_rows = []

    def test_find_all_not_found(self):
        expected_result = []

        result = call_log_dao.find_all()

        assert_that(result, equal_to(expected_result))

    def test_find_all_found(self):
        self.add_call_log()
        self.add_call_log()

        result = call_log_dao.find_all()

        assert_that(result, has_length(2))

    def test_create_call_log(self):
        expected_id = 13
        call_log = self.add_call_log(id=expected_id)

        call_log_dao.create_call_log(self.session, call_log)

        call_log_rows = self.session.query(CallLog).all()
        assert_that(call_log_rows, contains(has_property('id', expected_id)))

    def test_create_from_list(self):
        cel_id_1, cel_id_2 = self.add_cel(), self.add_cel()
        cel_id_3, cel_id_4 = self.add_cel(), self.add_cel()
        call_log_1 = CallLog(date=dt.now(), tenant_uuid=self.default_tenant.uuid)
        call_log_1.cel_ids = [cel_id_1, cel_id_2]
        call_log_2 = CallLog(date=dt.now(), tenant_uuid=self.default_tenant.uuid)
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
        call_log_1 = self.add_call_log()
        call_log_2 = self.add_call_log()
        call_log_3 = self.add_call_log()

        ids_deleted = call_log_dao.delete()

        assert_that(
            ids_deleted,
            contains_inanyorder(
                call_log_1.id, call_log_2.id, call_log_3.id
            )
        )
        result = self.session.query(CallLog).all()
        assert_that(result, empty())

    def test_delete_older(self):
        now = dt.now()
        older = now - td(hours=1)
        exclude_time = now - td(hours=2)
        call_log_1 = self.add_call_log(date=now)
        call_log_2 = self.add_call_log(date=exclude_time)
        call_log_3 = self.add_call_log(date=now)

        ids_deleted = call_log_dao.delete(older=older)

        assert_that(ids_deleted, contains_inanyorder(call_log_1.id, call_log_3.id))
        result = self.session.query(CallLog).all()
        assert_that(result, contains(call_log_2))

    def test_delete_empty(self):
        result = call_log_dao.delete()
        assert_that(result, empty())
