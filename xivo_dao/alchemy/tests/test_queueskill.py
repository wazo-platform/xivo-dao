# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    empty,
    equal_to,
)

from sqlalchemy.inspection import inspect

from xivo_dao.tests.test_dao import DAOTestCase


class TestAgentQueueSkills(DAOTestCase):
    def test_getter(self):
        skill = self.add_queue_skill()
        agent_skill1 = self.add_agent_queue_skill(skillid=skill.id)
        agent_skill2 = self.add_agent_queue_skill(skillid=skill.id)

        self.session.expire_all()
        assert_that(
            skill.agent_queue_skills, contains_inanyorder(agent_skill1, agent_skill2)
        )

    def test_setter(self):
        skill = self.add_queue_skill()
        agent_skill = self.add_agent_queue_skill()
        skill.agent_queue_skills = [agent_skill]
        self.session.flush()

        self.session.expire_all()
        assert_that(skill.agent_queue_skills, contains_inanyorder(agent_skill))
        assert_that(agent_skill.skillid, equal_to(skill.id))

    def test_deleter(self):
        skill = self.add_queue_skill()
        agent = self.add_agent()
        agent_skill = self.add_agent_queue_skill(skillid=skill.id, agentid=agent.id)

        skill.agent_queue_skills = []
        self.session.flush()

        self.session.expire_all()
        assert_that(skill.agent_queue_skills, empty())

        assert_that(inspect(agent_skill).deleted)
        assert_that(not inspect(skill).deleted)
        assert_that(not inspect(agent).deleted)


class TestDeleter(DAOTestCase):
    def test_queue_skill(self):
        skill = self.add_queue_skill()

        self.session.delete(skill)
        self.session.flush()

        assert_that(inspect(skill).deleted)
