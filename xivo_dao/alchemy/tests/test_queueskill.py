# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
)

from sqlalchemy.inspection import inspect

from xivo_dao.tests.test_dao import DAOTestCase

from ..queueskill import QueueSkill


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
