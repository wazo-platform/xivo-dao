# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    empty,
    equal_to,
)

from sqlalchemy.inspection import inspect

from xivo_dao.tests.test_dao import DAOTestCase

from ..queueskill import QueueSkill


class TestAgentQueueSkills(DAOTestCase):

    def test_getter(self):
        skill = self.add_queue_skill()
        agent_skill1 = self.add_agent_queue_skill(skillid=skill.id)
        agent_skill2 = self.add_agent_queue_skill(skillid=skill.id)

        self.session.expire_all()
        assert_that(skill.agent_queue_skills, contains_inanyorder(agent_skill1, agent_skill2))

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


class TestQueueSkillCat(DAOTestCase):

    def test_getter(self):
        skill_category = self.add_queue_skill_category()
        skill = self.add_queue_skill(catid=skill_category.id)

        self.session.expire_all()
        assert_that(skill.queue_skill_cat, equal_to(skill_category))

    def test_setter(self):
        skill_category = self.add_queue_skill_category()
        skill = self.add_queue_skill()

        skill.queue_skill_cat = skill_category
        self.session.flush()

        self.session.expire_all()
        assert_that(skill.catid, equal_to(skill_category.id))
        assert_that(skill.queue_skill_cat, equal_to(skill_category))

    def test_deleter(self):
        skill_category = self.add_queue_skill_category()
        skill = self.add_queue_skill(catid=skill_category.id)

        skill.queue_skill_cat = None
        self.session.flush()

        self.session.expire_all()
        assert_that(skill.catid, equal_to(None))
        assert_that(skill.queue_skill_cat, equal_to(None))


class TestCategory(DAOTestCase):

    def test_getter(self):
        skill_category = self.add_queue_skill_category(name='MyCategory')
        skill = self.add_queue_skill(catid=skill_category.id)

        self.session.expire_all()
        assert_that(skill.category, equal_to('MyCategory'))

    def test_getter_none(self):
        skill = self.add_queue_skill()

        self.session.expire_all()
        assert_that(skill.category, equal_to(None))

    def test_expression(self):
        skill_category = self.add_queue_skill_category(name='category')
        skill = self.add_queue_skill(catid=skill_category.id)

        result = self.session.query(QueueSkill).filter(QueueSkill.category == 'category').first()
        assert_that(result, equal_to(skill))


class TestDeleter(DAOTestCase):

    def test_queue_skill_cat(self):
        skill_category = self.add_queue_skill_category()
        skill = self.add_queue_skill(catid=skill_category.id)

        self.session.delete(skill)
        self.session.flush()

        assert_that(inspect(skill).deleted)
        assert_that(not inspect(skill_category).deleted)
