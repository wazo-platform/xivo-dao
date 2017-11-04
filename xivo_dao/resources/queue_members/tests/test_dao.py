# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
#
# SPDX-License-Identifier: GPL-3.0+
from hamcrest import assert_that, all_of, has_property, equal_to
from hamcrest.core.base_matcher import BaseMatcher

from xivo_dao.resources.queue_members import dao as queue_members_dao
from xivo_dao.resources.queue_members.model import QueueMemberAgent
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.agentfeatures import AgentFeatures as AgentFeaturesSchema
from xivo_dao.alchemy.queuefeatures import QueueFeatures as QueueFeaturesSchema
from xivo_dao.alchemy.queuemember import QueueMember as QueueMemberSchema


class IsAnAgentQueueMember(BaseMatcher):
    def __init__(self, agent, queue_name):
        self.agent = agent
        self.queue_name = queue_name
        self.error = ""

    def _sub_match(self, property, expected, item):
        if not has_property(property, expected).matches(item):
            self.error = "%s is <%s> should be <%s>" % (property, getattr(item, property), expected)
            return False
        return True

    def _matches(self, item):
        if not self._sub_match('queue_name', self.queue_name, item):
            return False
        if not self._sub_match('interface', ('Agent/%s' % self.agent.number), item):
            return False
        if not self._sub_match('commented', 0, item):
            return False
        if not self._sub_match('usertype', 'agent', item):
            return False
        if not self._sub_match('userid', self.agent.id, item):
            return False
        if not self._sub_match('channel', 'Agent', item):
            return False
        if not self._sub_match('category', 'queue', item):
            return False
        if not self._sub_match('position', 0, item):
            return False
        return True

    def describe_mismatch(self, item, mismatch_description):
        mismatch_description.append_text(self.error)

    def describe_to(self, description):
        description.append_text("queue member should have proper queue_name, interface, category, userid")


def is_an_agent_queue_member(agent, queue_name):
    return IsAnAgentQueueMember(agent, queue_name)


class TestQueueAgentAssociation(DAOTestCase):
    def test_get_by_queue_and_agent_id(self):
        agent_id = 23
        queue_id = 2
        penalty = 5
        queue_name = 'myqueue'
        self.add_queuefeatures(id=queue_id, name=queue_name)
        self.add_agent(id=agent_id, number='1200')
        self.add_queue_member(queue_name=queue_name,
                              interface='Agent/1200',
                              penalty=penalty,
                              usertype='agent',
                              userid=agent_id,
                              channel='Agent',
                              category='queue')

        result = queue_members_dao.get_by_queue_id_and_agent_id(queue_id, agent_id)

        assert_that(result, all_of(has_property('penalty', penalty),
                                   has_property('agent_id', agent_id),
                                   has_property('queue_id', queue_id)))

    def test_get_by_queue_and_agent_id_not_exists(self):
        self.assertRaises(NotFoundError, queue_members_dao.get_by_queue_id_and_agent_id, 1, 8)

    def test_edit_agent_queue_association(self):
        agent_id = 23
        queue_id = 2
        penalty = 4
        queue_name = 'myqueue'
        self.add_queuefeatures(id=queue_id, name=queue_name)
        self.add_agent(id=agent_id, number='1200')
        self.add_queue_member(queue_name=queue_name, interface='Agent/1200', penalty=penalty, usertype='agent',
                              userid=agent_id, channel='Agent', category='queue')

        queue_member = QueueMemberAgent(agent_id=agent_id, queue_id=queue_id, penalty=6)
        queue_members_dao.edit_agent_queue_association(queue_member)

        assert_that(queue_members_dao.get_by_queue_id_and_agent_id(queue_id, agent_id), has_property('penalty', 6))

    def test_associate(self):
        queue_name = 'yellowstone'
        queue_member = QueueMemberAgent(agent_id=52, queue_id=34, penalty=9)

        self.add_queuefeatures(id=queue_member.queue_id, name=queue_name)
        self.add_agent(id=queue_member.agent_id, number='1400')
        agent = (self.session.query(AgentFeaturesSchema)
                 .filter(AgentFeaturesSchema.id == queue_member.agent_id).first())

        res_qm = queue_members_dao.associate(queue_member)

        assert_that(res_qm, equal_to(queue_member))

        assert_that(self.qm_in_base(queue_member), is_an_agent_queue_member(agent, queue_name))

    def test_associate_at_last_position(self):
        queue_name = 'blackpearl'
        queue_memberPos0 = QueueMemberAgent(agent_id=52, queue_id=34, penalty=9)
        queue_memberPosMax = QueueMemberAgent(agent_id=62, queue_id=34, penalty=5)

        self.add_queuefeatures(id=queue_memberPos0.queue_id, name=queue_name)
        self.add_agent(id=queue_memberPos0.agent_id, number='1410')
        self.add_agent(id=queue_memberPosMax.agent_id, number='1411')
        queue_members_dao.associate(queue_memberPos0)

        res_qmPosMax = queue_members_dao.associate(queue_memberPosMax)

        assert_that(self.qm_in_base(queue_memberPosMax), has_property('position', 1))

    def test_remove_agent_from_queue(self):
        agent_id = 88
        queue_id = 124
        queue_name = 'topone'
        penalty = 2
        self.add_queuefeatures(id=queue_id, name=queue_name)
        self.add_agent(id=agent_id, number='1200')
        self._add_agent_to_queue(queue_name, 1200, agent_id, penalty)

        queue_members_dao.remove_agent_from_queue(agent_id, queue_id)

        self.assertRaises(NotFoundError, queue_members_dao.get_by_queue_id_and_agent_id, queue_id, agent_id)

    def qm_in_base(self, queue_member):
        return (self.session.query(QueueMemberSchema)
                .filter(QueueFeaturesSchema.name == QueueMemberSchema.queue_name)
                .filter(QueueMemberSchema.usertype == 'agent')
                .filter(QueueMemberSchema.userid == queue_member.agent_id)
                .filter(QueueFeaturesSchema.id == queue_member.queue_id)).first()

    def _add_agent_to_queue(self, queue_name, agent_number, agent_id, penalty):
        self.add_queue_member(queue_name=queue_name,
                              interface='Agent/%s' % agent_number,
                              penalty=penalty,
                              usertype='agent',
                              userid=agent_id,
                              channel='Agent',
                              category='queue')
