# Copyright 2012-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.tests.test_dao import DAOTestCase

from .. import queue_member_dao


class TestQueueMemberDAO(DAOTestCase):

    def test_add_agent_to_queue(self):
        agent_id = 123
        agent_number = '123'
        queue_name = 'queue1'

        queue_member_dao.add_agent_to_queue(agent_id, agent_number, queue_name)

        queue_member = self.session.query(QueueMember).first()
        assert queue_member.queue_name == queue_name
        assert queue_member.interface == 'Agent/123'
        assert queue_member.usertype == 'agent'
        assert queue_member.userid == agent_id
        assert queue_member.channel == 'Agent'
        assert queue_member.category == 'queue'
        assert queue_member.position == 0

    def test_remove_agent_from_queue(self):
        agent_id = 123
        queue_name = 'queue1'
        self._insert_queue_member(queue_name, 'Agent/123', usertype='agent', userid=agent_id)

        queue_member_dao.remove_agent_from_queue(agent_id, queue_name)

        nb_queue_members = self.session.query(QueueMember).count()
        assert 0 == nb_queue_members

    def test_get_next_position_for_queue(self):
        queue_name = 'queue1'
        member_name = 'Agent/123'
        self._insert_queue_member(queue_name, member_name)

        position = queue_member_dao._get_next_position_for_queue(self.session, queue_name)

        assert position == 1

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
