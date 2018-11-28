# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    contains_inanyorder,
    empty,
    equal_to,
    none,
)
from sqlalchemy.inspection import inspect

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper

from ..func_key_dest_agent import FuncKeyDestAgent
from ..queuemember import QueueMember


class TestAgentQueueSkills(DAOTestCase):

    def test_getter(self):
        agent = self.add_agent()
        agent_skill1 = self.add_agent_queue_skill(agentid=agent.id)
        agent_skill2 = self.add_agent_queue_skill(agentid=agent.id)

        self.session.expire_all()
        assert_that(agent.agent_queue_skills, contains_inanyorder(agent_skill1, agent_skill2))

    def test_setter(self):
        agent = self.add_agent()
        agent_skill = self.add_agent_queue_skill()
        agent.agent_queue_skills = [agent_skill]
        self.session.flush()

        self.session.expire_all()
        assert_that(agent.agent_queue_skills, contains_inanyorder(agent_skill))
        assert_that(agent_skill.agentid, equal_to(agent.id))

    def test_deleter(self):
        skill = self.add_queue_skill()
        agent = self.add_agent()
        agent_skill = self.add_agent_queue_skill(skillid=skill.id, agentid=agent.id)

        agent.agent_queue_skills = []
        self.session.flush()

        self.session.expire_all()
        assert_that(agent.agent_queue_skills, empty())

        assert_that(inspect(agent_skill).deleted)
        assert_that(not inspect(skill).deleted)
        assert_that(not inspect(agent).deleted)


class TestUsers(DAOTestCase):

    def test_getter(self):
        agent = self.add_agent()
        user_1 = self.add_user(agent_id=agent.id)
        user_2 = self.add_user(agent_id=agent.id)

        self.session.expire_all()
        assert_that(agent.users, contains_inanyorder(user_1, user_2))


class TestDelete(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super(TestDelete, self).setUp()
        self.setup_funckeys()

    def test_funckeys_are_deleted(self):
        agent = self.add_agent()
        extension = self.add_extension()
        self.add_agent_destination(agent.id, extension.id)

        self.session.delete(agent)
        self.session.flush()

        row = self.session.query(FuncKeyDestAgent).first()
        assert_that(row, none())

    def test_queue_queue_members_are_deleted(self):
        agent = self.add_agent()
        self.add_queue_member(category='queue', usertype='agent', userid=agent.id)

        self.session.delete(agent)
        self.session.flush()

        row = self.session.query(QueueMember).first()
        assert_that(row, none())
