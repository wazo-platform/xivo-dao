# -*- coding: utf-8 -*-
# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from mock import patch

from xivo_dao import queue_member_dao
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.tests.test_dao import DAOTestCase


class TestQueueMemberDAO(DAOTestCase):

    def test_add_agent_to_queue(self):
        agent_id = 123
        agent_number = '123'
        queue_name = 'queue1'

        queue_member_dao.add_agent_to_queue(agent_id, agent_number, queue_name)

        queue_member = self.session.query(QueueMember).first()
        self.assertEqual(queue_member.queue_name, queue_name)
        self.assertEqual(queue_member.interface, 'Agent/123')
        self.assertEqual(queue_member.usertype, 'agent')
        self.assertEqual(queue_member.userid, agent_id)
        self.assertEqual(queue_member.channel, 'Agent')
        self.assertEqual(queue_member.category, 'queue')
        self.assertEqual(queue_member.position, 0)

    def test_remove_agent_from_queue(self):
        agent_id = 123
        queue_name = 'queue1'
        self._insert_queue_member(queue_name, 'Agent/123', usertype='agent', userid=agent_id)

        queue_member_dao.remove_agent_from_queue(agent_id, queue_name)

        nb_queue_members = self.session.query(QueueMember).count()
        self.assertEqual(0, nb_queue_members)

    def test_get_next_position_for_queue(self):
        queue_name = 'queue1'
        member_name = 'Agent/123'
        self._insert_queue_member(queue_name, member_name)

        position = queue_member_dao._get_next_position_for_queue(self.session, queue_name)

        self.assertEqual(position, 1)

    def test_get_queue_members_for_queues(self):
        self._insert_queue_member('queue1', 'Agent/2')
        self._insert_queue_member('queue2', 'Agent/3')
        self._insert_queue_member('group1', 'SIP/abcdef', is_queue=False)

        queue_feature = QueueFeatures(
            tenant_uuid=self.default_tenant.uuid,
            name='queue1',
            displayname='queue1'
        )

        self.add_me(queue_feature)

        queue_members = queue_member_dao.get_queue_members_for_queues()

        self.assertEqual(len(queue_members), 1)

        queue_member = queue_members[0]
        self.assertEqual(queue_member.queue_name, 'queue1')
        self.assertEqual(queue_member.member_name, 'Agent/2')

    @patch('xivo_dao.user_line_dao.get_line_identity_by_user_id')
    def test_add_user_to_queue(self, mock_get_line_identity):
        user_id = 1
        queue = 'queue1'
        interface = 'SIP/123'
        mock_get_line_identity.return_value = interface

        queue_member_dao.add_user_to_queue(user_id, queue)

        queue_member = self.session.query(QueueMember).first()
        self.assertEqual(queue_member.queue_name, queue)
        self.assertEqual(queue_member.interface, interface)
        self.assertEqual(queue_member.usertype, 'user')
        self.assertEqual(queue_member.userid, user_id)
        self.assertEqual(queue_member.channel, 'SIP')
        self.assertEqual(queue_member.category, 'queue')
        self.assertEqual(queue_member.position, 0)

    def test_delete_by_userid(self):
        self._insert_queue_member("test", "sip/123", 'user', 1, True)
        self._insert_queue_member("test", "sip/456", 'agent', 1, True)

        queue_member_dao.delete_by_userid(1)

        result = self.session.query(QueueMember).all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].usertype, 'agent')

    def _insert_queue_member(self, queue_name, member_name, usertype='user', userid=1, is_queue=True):
        queue_member = QueueMember()
        queue_member.queue_name = queue_name
        queue_member.interface = member_name
        queue_member.penalty = 0
        queue_member.usertype = usertype
        queue_member.userid = userid
        queue_member.channel = 'foobar'
        queue_member.category = 'queue' if is_queue else 'group'
        queue_member.position = 0

        self.add_me(queue_member)
