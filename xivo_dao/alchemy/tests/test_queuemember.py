# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    equal_to,
    has_properties,
    is_,
    none,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..agentfeatures import AgentFeatures
from ..groupfeatures import GroupFeatures
from ..queuemember import QueueMember
from ..userfeatures import UserFeatures


class TestAgent(DAOTestCase):

    def test_getter(self):
        agent = self.add_agent()
        queue_member = self.add_queue_member(usertype='agent', userid=agent.id)

        self.session.expire_all()
        assert_that(queue_member.agent, equal_to(agent))

    def test_setter(self):
        agent = self.add_agent()
        queue_member = self.add_queue_member(usertype='agent')

        queue_member.agent = agent
        self.session.flush()

        self.session.expire_all()
        assert_that(queue_member.agent, equal_to(agent))


class TestQueue(DAOTestCase):

    def test_getter(self):
        queue = self.add_queuefeatures()
        queue_member = self.add_queue_member(queue_name=queue.name)

        self.session.expire_all()
        assert_that(queue_member.queue, equal_to(queue))


class TestPriority(DAOTestCase):

    def test_getter(self):
        member = QueueMember(position=42)
        assert_that(member.priority, equal_to(42))

    def test_setter(self):
        member = QueueMember(priority=42)
        assert_that(member.position, equal_to(42))






class TestExten(DAOTestCase):

    def test_setter(self):
        member = QueueMember()
        member.exten = '123'
        assert_that(member.exten, equal_to('123'))

    def test_exten_with_custom_exten(self):
        member = QueueMember(exten='456', interface='Local/123@default')
        assert_that(member.exten, equal_to('456'))

    def test_exten_without_custom_exten(self):
        member = QueueMember(interface='Local/123@default')
        assert_that(member.exten, equal_to('123'))

    def test_exten_with_no_local(self):
        member = QueueMember(interface='SIP/123')
        assert_that(member.exten, is_(none()))


class TestContext(DAOTestCase):

    def test_setter(self):
        member = QueueMember()
        member.context = 'default'
        assert_that(member.context, equal_to('default'))

    def test_context_with_custom_context(self):
        member = QueueMember(context='toto', interface='Local/123@default')
        assert_that(member.context, equal_to('toto'))

    def test_context_without_custom_context(self):
        member = QueueMember(interface='Local/123@default')
        assert_that(member.context, equal_to('default'))

    def test_context_with_no_local(self):
        member = QueueMember(interface='SIP/123')
        assert_that(member.context, is_(none()))


class TestFix(DAOTestCase):

    def test_user_sip(self):
        user = self.add_user()
        sip = self.add_usersip(name='sipname')
        line = self.add_line(protocol='sip', protocolid=sip.id)
        self.add_user_line(user_id=user.id, line_id=line.id)
        member = self.add_queue_member(usertype='user', userid=user.id, interface='wrong', channel='wrong')

        member.fix()
        self.session.flush()

        self.session.expire_all()
        assert_that(member, has_properties(
            interface='SIP/sipname',
            channel='SIP',
        ))

    def test_user_sccp(self):
        user = self.add_user()
        sccp = self.add_sccpline(name='sccpname')
        line = self.add_line(protocol='sccp', protocolid=sccp.id)
        self.add_user_line(user_id=user.id, line_id=line.id)
        member = self.add_queue_member(usertype='user', userid=user.id, interface='wrong', channel='wrong')

        member.fix()
        self.session.flush()

        self.session.expire_all()
        assert_that(member, has_properties(
            interface='SCCP/sccpname',
            channel='SCCP',
        ))

    def test_user_custom(self):
        user = self.add_user()
        custom = self.add_usercustom(interface='custom/interface')
        line = self.add_line(protocol='custom', protocolid=custom.id)
        self.add_user_line(user_id=user.id, line_id=line.id)
        member = self.add_queue_member(usertype='user', userid=user.id, interface='wrong', channel='wrong')

        member.fix()
        self.session.flush()

        self.session.expire_all()
        assert_that(member, has_properties(
            interface='custom/interface',
            channel='**Unknown**',
        ))

    def test_agent(self):
        agent = self.add_agent(number='1234')
        member = self.add_queue_member(usertype='agent', userid=agent.id, interface='wrong', channel='wrong')

        member.fix()
        self.session.flush()

        self.session.expire_all()
        assert_that(member, has_properties(
            interface='Agent/1234',
            channel='Agent',
        ))


class TestDelete(DAOTestCase):

    def test_group_is_not_deleted(self):
        group = self.add_group()
        queue_member = self.add_queue_member(queue_name=group.name, category='group')

        self.session.delete(queue_member)
        self.session.flush()

        row = self.session.query(GroupFeatures).first()
        assert_that(row, equal_to(group))

    def test_user_is_not_deleted(self):
        user = self.add_user()
        queue_member = self.add_queue_member(usertype='user', userid=user.id)

        self.session.delete(queue_member)
        self.session.flush()

        row = self.session.query(UserFeatures).first()
        assert_that(row, equal_to(user))

    def test_agent_is_not_deleted(self):
        agent = self.add_agent()
        queue_member = self.add_queue_member(usertype='agent', userid=agent.id)

        self.session.delete(queue_member)
        self.session.flush()

        row = self.session.query(AgentFeatures).first()
        assert_that(row, equal_to(agent))
