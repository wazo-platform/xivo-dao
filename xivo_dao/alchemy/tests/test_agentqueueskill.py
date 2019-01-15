# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    equal_to,
)
from sqlalchemy.inspection import inspect

from xivo_dao.tests.test_dao import DAOTestCase


class TestAgent(DAOTestCase):

    def test_getter(self):
        agent = self.add_agent()
        agent_skill = self.add_agent_queue_skill(agentid=agent.id)

        self.session.expire_all()
        assert_that(agent_skill.agent, equal_to(agent))

    def test_setter(self):
        agent = self.add_agent()
        agent_skill = self.add_agent_queue_skill()

        agent_skill.agent = agent
        self.session.flush()

        self.session.expire_all()
        assert_that(agent_skill.agent, equal_to(agent))
        assert_that(agent_skill.agentid, equal_to(agent.id))


class TestSkill(DAOTestCase):

    def test_getter(self):
        skill = self.add_queue_skill()
        agent_skill = self.add_agent_queue_skill(skillid=skill.id)

        self.session.expire_all()
        assert_that(agent_skill.skill, equal_to(skill))

    def test_setter(self):
        skill = self.add_queue_skill()
        agent_skill = self.add_agent_queue_skill()

        agent_skill.skill = skill
        self.session.flush()

        self.session.expire_all()
        assert_that(agent_skill.skill, equal_to(skill))
        assert_that(agent_skill.skillid, equal_to(skill.id))


class TestDeleter(DAOTestCase):

    def test_agent(self):
        agent = self.add_agent()
        agent_skill = self.add_agent_queue_skill(agentid=agent.id)

        self.session.delete(agent_skill)
        self.session.flush()

        assert_that(inspect(agent_skill).deleted)
        assert_that(not inspect(agent).deleted)

    def test_skill(self):
        skill = self.add_queue_skill()
        agent_skill = self.add_agent_queue_skill(skillid=skill.id)

        self.session.delete(agent_skill)
        self.session.flush()

        assert_that(inspect(agent_skill).deleted)
        assert_that(not inspect(skill).deleted)
