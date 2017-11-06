# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao import queue_dao
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.tests.test_dao import DAOTestCase


class TestQueueDAO(DAOTestCase):

    def test_id_from_name(self):
        queue = self._insert_queue('test_queue', 'Queue Test')

        result = queue_dao.id_from_name(queue.name)

        self.assertEqual(result, queue.id)

    def test_queue_name(self):
        queue = self._insert_queue('my_queue', 'My Queue')

        result = queue_dao.queue_name(queue.id)

        self.assertEqual(result, 'my_queue')

    def test_get_name_number(self):
        self.assertRaises(LookupError, queue_dao.get_display_name_number, 1)

        queue = self._insert_queue('my_queue', 'My Queue', '3000')

        name, number = queue_dao.get_display_name_number(queue.id)

        self.assertEqual(name, 'My Queue')
        self.assertEqual(number, '3000')

    def test_is_user_member_of_queue_when_present(self):
        user_id = 1
        queue = self._insert_queue('foobar', 'Foobar')
        self._insert_queue_member(queue.name, 'user', user_id)

        result = queue_dao.is_user_member_of_queue(user_id, queue.id)

        self.assertTrue(result)

    def test_is_user_member_of_queue_when_not_present(self):
        user_id = 1
        queue = self._insert_queue('foobar', 'Foobar')

        result = queue_dao.is_user_member_of_queue(user_id, queue.id)

        self.assertFalse(result)

    def test_is_user_member_of_queue_when_present_as_agent(self):
        user_id = 1
        agent_id = 42
        self._insert_user(user_id, agent_id)
        queue = self._insert_queue('foobar', 'Foobar')
        self._insert_queue_member(queue.name, 'agent', agent_id)

        result = queue_dao.is_user_member_of_queue(user_id, queue.id)

        self.assertTrue(result)

    def test_all_queues(self):
        expected = []
        expected.append(self._insert_queue('name1', 'display1', '3001'))
        expected.append(self._insert_queue('name2', 'display2', '3002'))
        self.assertTrue(queue_dao.all_queues() == expected)

    def _insert_user(self, user_id, agent_id):
        return self.add_user(id=user_id, firstname='John', agentid=agent_id)

    def _insert_queue(self, name, display_name, number='3000'):
        queue = QueueFeatures()
        queue.name = name
        queue.displayname = display_name
        queue.number = number

        self.add_me(queue)

        return queue

    def _insert_queue_member(self, queue_name, user_type, user_id):
        queue_member = QueueMember()
        queue_member.queue_name = queue_name
        queue_member.interface = 'SIP/abcdef'
        queue_member.penalty = 0
        queue_member.usertype = user_type
        queue_member.userid = user_id
        queue_member.channel = 'foobar'
        queue_member.category = 'queue'

        self.add_me(queue_member)
