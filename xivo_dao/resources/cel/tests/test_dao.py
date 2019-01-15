# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
from hamcrest import assert_that, contains, has_property, contains_inanyorder

from xivo_dao.alchemy.cel import CEL as CELSchema
from xivo_dao.alchemy.call_log import CallLog as CallLogSchema
from xivo_dao.resources.cel import dao as cel_dao
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.tests.test_dao import DAOTestCase


class TestCELDAO(DAOTestCase):

    def test_find_last_unprocessed_no_cels(self):
        limit = 10

        result = cel_dao.find_last_unprocessed(limit)

        assert_that(result, contains())

    def test_find_last_unprocessed_over_limit(self):
        limit = 2
        self.add_cel(linkedid='1')
        cel_id_2 = self.add_cel(linkedid='2')
        cel_id_3 = self.add_cel(linkedid='3')

        result = cel_dao.find_last_unprocessed(limit)

        assert_that(result, contains(has_property('id', cel_id_2),
                                     has_property('id', cel_id_3)))

    def test_find_last_unprocessed_under_limit(self):
        limit = 10
        cel_id_1, cel_id_2 = self.add_cel(linkedid='1'), self.add_cel(linkedid='2')

        result = cel_dao.find_last_unprocessed(limit)

        assert_that(result, contains(has_property('id', cel_id_1),
                                     has_property('id', cel_id_2)))

    def test_find_last_unprocessed_under_limit_exceeding_limit_to_complete_call(self):
        limit = 1
        cel_id_1, cel_id_2 = self.add_cel(linkedid='1'), self.add_cel(linkedid='1')

        result = cel_dao.find_last_unprocessed(limit)

        assert_that(result, contains(has_property('id', cel_id_1),
                                     has_property('id', cel_id_2)))

    def test_find_last_unprocessed_under_limit_exceeding_limit_to_reprocess_partially_processed_call(self):
        limit = 2
        cel_id_1, cel_id_2 = self._add_processed_cel(linkedid='1'), self.add_cel(linkedid='1')
        cel_id_3, cel_id_4 = self._add_processed_cel(linkedid='2'), self.add_cel(linkedid='2')

        result = cel_dao.find_last_unprocessed(limit)

        assert_that(result, contains(has_property('id', cel_id_1),
                                     has_property('id', cel_id_2),
                                     has_property('id', cel_id_3),
                                     has_property('id', cel_id_4)))

    def test_find_last_unprocessed_with_only_processed(self):
        limit = 10
        self._add_processed_cel()
        self._add_processed_cel()

        result = cel_dao.find_last_unprocessed(limit)

        assert_that(result, contains())

    def test_find_last_unprocessed_with_processed_and_unprocessed(self):
        limit = 10
        self._add_processed_cel(linkedid='1')
        self._add_processed_cel(linkedid='1')
        cel_id_3, cel_id_4 = self.add_cel(linkedid='2'), self.add_cel(linkedid='2')

        result = cel_dao.find_last_unprocessed(limit)

        assert_that(result, contains(has_property('id', cel_id_3),
                                     has_property('id', cel_id_4)))

    def test_find_last_unprocessed_with_partially_processed(self):
        limit = 10
        cel_id_1, cel_id_2 = self.add_cel(linkedid='1'), self._add_processed_cel(linkedid='1')
        cel_id_3, cel_id_4 = self._add_processed_cel(linkedid='2'), self.add_cel(linkedid='2')

        result = cel_dao.find_last_unprocessed(limit)

        assert_that(result, contains(has_property('id', cel_id_1),
                                     has_property('id', cel_id_2),
                                     has_property('id', cel_id_3),
                                     has_property('id', cel_id_4)))

    def test_find_from_linked_id_no_cels(self):
        linked_id = '666'

        result = cel_dao.find_from_linked_id(linked_id)

        assert_that(result, contains())

    def test_find_from_linked_id(self):
        linked_id = '666'
        cel_id_1 = self.add_cel(linkedid='666')
        self.add_cel(linkedid='3')
        cel_id_3 = self.add_cel(linkedid='666')

        result = cel_dao.find_from_linked_id(linked_id)

        assert_that(result, contains_inanyorder(has_property('id', cel_id_1),
                                                has_property('id', cel_id_3)))

    def test_find_from_linked_id_when_cels_are_unordered_then_return_cels_in_chronological_order(self):
        linked_id = '666'
        now = datetime.datetime.now()
        one_hour_ago = now - datetime.timedelta(hours=1)
        one_hour_later = now + datetime.timedelta(hours=1)
        cel_id_1, cel_id_2, cel_id_3 = [self.add_cel(linkedid='666', eventtime=now),
                                        self.add_cel(linkedid='666', eventtime=one_hour_ago),
                                        self.add_cel(linkedid='666', eventtime=one_hour_later)]

        result = cel_dao.find_from_linked_id(linked_id)

        assert_that(result, contains(has_property('id', cel_id_2),
                                     has_property('id', cel_id_1),
                                     has_property('id', cel_id_3)))

    def test_find_last_unprocessed_no_cels_with_older(self):
        older = datetime.datetime.now() - datetime.timedelta(hours=1)

        result = cel_dao.find_last_unprocessed(older=older)

        assert_that(result, contains())

    def test_find_last_unprocessed_over_older(self):
        now = datetime.datetime.now()
        older = now - datetime.timedelta(hours=1)
        exclude_time = now - datetime.timedelta(hours=2)

        self.add_cel(eventtime=exclude_time)
        cel_id_2 = self.add_cel(linkedid='2')
        cel_id_3 = self.add_cel(linkedid='3')

        result = cel_dao.find_last_unprocessed(older=older)

        assert_that(result, contains(has_property('id', cel_id_2),
                                     has_property('id', cel_id_3)))

    def test_find_last_unprocessed_under_older(self):
        now = datetime.datetime.now()
        older = now - datetime.timedelta(hours=1)
        cel_id_1, cel_id_2 = self.add_cel(linkedid='1'), self.add_cel(linkedid='2')

        result = cel_dao.find_last_unprocessed(older=older)

        assert_that(result, contains(has_property('id', cel_id_1),
                                     has_property('id', cel_id_2)))

    def test_find_last_unprocessed_under_older_exceeding_limit_to_complete_call(self):
        now = datetime.datetime.now()
        older = now - datetime.timedelta(hours=1)
        exclude_time = now - datetime.timedelta(hours=2)
        cel_id_1, cel_id_2 = self.add_cel(eventtime=exclude_time, linkedid='1'), self.add_cel(linkedid='1')

        result = cel_dao.find_last_unprocessed(older=older)

        assert_that(result, contains(has_property('id', cel_id_1),
                                     has_property('id', cel_id_2)))

    def _add_processed_cel(self, **kwargs):
        call_log_id = self._add_call()
        cel_id = self.add_cel(**kwargs)
        self._link_call_to_cel(call_log_id, cel_id)

        return cel_id

    def _add_call(self):
        call_log = CallLogSchema(date=datetime.datetime.now())
        self.add_me(call_log)
        return call_log.id

    def _link_call_to_cel(self, call_log_id, cel_id):
        with flush_session(self.session):
            cel_row = self.session.query(CELSchema).get(cel_id)
            cel_row.call_log_id = call_log_id
