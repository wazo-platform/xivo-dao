# -*- coding: utf-8 -*-
# Copyright 2013-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

from hamcrest import assert_that, contains_inanyorder

from xivo_dao import stat_queue_dao
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.tests.test_dao import DAOTestCase


class TestStatQueueDAO(DAOTestCase):

    def test_id_from_name(self):
        queue = self._insert_queue('test_queue')

        result = stat_queue_dao.id_from_name(queue.name)

        self.assertEqual(result, queue.id)

    def test_insert_if_missing(self):
        # queue1: in confd + in cel + in stat
        # queue2: in confd + not in cel + in stat
        # queue3: in confd + not in cel + not in stat',
        # queue4: in confd + in cel + not in stat',
        # queue5: not in confd + in cel + not in stat',
        # queue6: not in confd + in cel + in stat',
        # queue7: not in confd + not in cel + in stat',
        confd_queues = [
            {
                'id': 1,
                'name': 'queue1',
                'tenant_uuid': 'tenant1',
            },
            {
                'id': 2,
                'name': 'queue2',
                'tenant_uuid': 'tenant2',
            },
            {
                'id': 3,
                'name': 'queue3',
                'tenant_uuid': 'tenant3',
            },
            {
                'id': 4,
                'name': 'queue4',
                'tenant_uuid': 'tenant4',
            },
        ]
        self._insert_queue('queue1', 'tenant1', 1)
        self._insert_queue('queue2', 'tenant2', 2)
        self._insert_queue('queue6', 'tenant6', 6)
        self._insert_queue('queue7', 'tenant7', 7)

        new_queues = ['queue1', 'queue4', 'queue5']
        master_tenant = str(uuid.uuid4())

        with flush_session(self.session):
            stat_queue_dao.insert_if_missing(self.session, new_queues, confd_queues, master_tenant)

        result = self._fetch_stat_queues()
        assert_that(result, contains_inanyorder(
            ('queue1', 'tenant1', 1, False),
            ('queue2', 'tenant2', 2, False),
            ('queue3', 'tenant3', 3, False),
            ('queue4', 'tenant4', 4, False),
            ('queue5', master_tenant, None, True),
            ('queue6', 'tenant6', 6, True),
            ('queue7', 'tenant7', 7, True),
        ))

    def test_when_queue_marked_as_deleted_then_new_one_is_created(self):
        confd_queues = [{'id': 1, 'name': 'queue', 'tenant_uuid': 'tenant'}]
        self._insert_queue('queue', 'tenant', queue_id=999, deleted=True)
        new_queues = ['queue']
        master_tenant = str(uuid.uuid4())

        with flush_session(self.session):
            stat_queue_dao.insert_if_missing(self.session, new_queues, confd_queues, master_tenant)

        result = self._fetch_stat_queues()
        assert_that(result, contains_inanyorder(
            ('queue', 'tenant', 1, False),
            ('queue_', 'tenant', 999, True),
        ))

    def test_mark_recreated_queues_with_same_name_as_deleted(self):
        confd_queues = {'queue': {'id': 1, 'name': 'queue', 'tenant_uuid': 'tenant'}}
        self._insert_queue('queue', 'tenant', queue_id=999, deleted=False)

        with flush_session(self.session):
            stat_queue_dao._mark_recreated_queues_with_same_name_as_deleted(self.session, confd_queues)

        result = self._fetch_stat_queues()
        assert_that(result, contains_inanyorder(
            ('queue', 'tenant', 999, True),
        ))

    def test_mark_non_confd_queues_as_deleted(self):
        confd_queues = [{'id': 1, 'name': 'queue1', 'tenant_uuid': 'tenant'}]
        self._insert_queue('queue2', 'tenant', queue_id=2, deleted=False)
        self._insert_queue('queue3', 'tenant', queue_id=None, deleted=False)

        with flush_session(self.session):
            stat_queue_dao._mark_non_confd_queues_as_deleted(self.session, confd_queues)

        result = self._fetch_stat_queues()
        assert_that(result, contains_inanyorder(
            ('queue2', 'tenant', 2, True),
            ('queue3', 'tenant', None, True),
        ))

    def test_create_missing_queues(self):
        confd_queues = {
            'queue1': {'id': 1, 'name': 'queue1', 'tenant_uuid': 'tenant'},
        }
        new_queues = ['queue2', 'queue3']
        master_tenant = str(uuid.uuid4())
        self._insert_queue('queue3', 'tenant', deleted=True)

        with flush_session(self.session):
            stat_queue_dao._create_missing_queues(
                self.session, new_queues, confd_queues, master_tenant
            )

        result = self._fetch_stat_queues()
        assert_that(result, contains_inanyorder(
            ('queue1', 'tenant', 1, False),
            ('queue2', master_tenant, None, True),
            ('queue3', 'tenant', None, True),
        ))

    def test_rename_deleted_queues_with_duplicate_name(self):
        confd_queues = {'queue': {'id': 1, 'name': 'queue', 'tenant_uuid': 'tenant'}}
        self._insert_queue('queue', 'tenant', queue_id=1, deleted=True)
        self._insert_queue('queue', 'tenant', queue_id=1, deleted=True)

        with flush_session(self.session):
            stat_queue_dao._rename_deleted_queues_with_duplicate_name(
                self.session, confd_queues
            )

        result = self._fetch_stat_queues()
        assert_that(result, contains_inanyorder(
            ('queue_', 'tenant', 1, True),
            ('queue__', 'tenant', 1, True),
        ))

    def test_clean_table(self):
        self._insert_queue('queue1')

        stat_queue_dao.clean_table(self.session)

        self.assertTrue(self.session.query(StatQueue).first() is None)

    def _fetch_stat_queues(self):
        return [
            (name, tenant_uuid, queue_id, deleted)
            for name, tenant_uuid, queue_id, deleted
            in self.session.query(
                StatQueue.name, StatQueue.tenant_uuid, StatQueue.queue_id, StatQueue.deleted
            ).all()
        ]

    def _insert_queue(self, name, tenant_uuid=None, queue_id=None, deleted=False):
        queue = StatQueue()
        queue.name = name
        queue.tenant_uuid = tenant_uuid or self.default_tenant.uuid
        queue.queue_id = queue_id
        queue.deleted = deleted

        self.add_me(queue)

        return queue
