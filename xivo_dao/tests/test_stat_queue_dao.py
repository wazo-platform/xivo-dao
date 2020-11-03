# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

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

        new_queues = ['queue1', 'queue4', 'queue5']
        master_tenant = str(uuid.uuid4())

        with flush_session(self.session):
            stat_queue_dao.insert_if_missing(self.session, new_queues, confd_queues, master_tenant)

        result = [
            (name, tenant_uuid, queue_id)
            for name, tenant_uuid, queue_id
            in self.session.query(
                StatQueue.name, StatQueue.tenant_uuid, StatQueue.queue_id
            ).all()
        ]

        self.assertTrue(('queue1', 'tenant1', 1) in result)
        self.assertTrue(('queue2', 'tenant2', 2) in result)
        self.assertTrue(('queue3', 'tenant3', 3) in result)
        self.assertTrue(('queue4', 'tenant4', 4) in result)
        self.assertTrue(('queue5', master_tenant, None) in result)
        self.assertEquals(len(result), 5)

    def test_clean_table(self):
        self._insert_queue('queue1')

        stat_queue_dao.clean_table(self.session)

        self.assertTrue(self.session.query(StatQueue).first() is None)

    def _insert_queue(self, name, tenant_uuid=None, queue_id=None):
        queue = StatQueue()
        queue.name = name
        queue.tenant_uuid = tenant_uuid or self.default_tenant.uuid
        queue.queue_id = queue_id

        self.add_me(queue)

        return queue
