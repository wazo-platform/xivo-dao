# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    has_properties,
    not_,
)

from sqlalchemy.inspection import inspect

from xivo_dao.tests.test_dao import DAOTestCase

from ..queueskill import QueueSkill
from ..queueskillcat import QueueSkillCat


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

    def test_setter_create_new_category(self):
        skill = self.add_queue_skill()

        skill.category = 'Yeeeah'
        self.session.flush()

        self.session.expire_all()
        assert_that(skill.category, equal_to('Yeeeah'))

        categories = self.session.query(QueueSkillCat).all()
        assert_that(categories, contains_inanyorder(skill.queue_skill_cat))

    def test_setter_does_not_create_category(self):
        skill_category1 = self.add_queue_skill_category(name='MyCategory')
        skill_category2 = self.add_queue_skill_category(name='MyCategory2')
        skill = self.add_queue_skill(catid=skill_category1.id)

        skill.category = 'MyCategory2'
        self.session.flush()

        self.session.expire_all()
        assert_that(skill.category, equal_to('MyCategory2'))

        categories = self.session.query(QueueSkillCat).all()
        assert_that(categories, contains_inanyorder(skill_category1, skill_category2))

    def test_setter_none(self):
        skill_category = self.add_queue_skill_category()
        skill = self.add_queue_skill(catid=skill_category.id)

        skill.category = None
        self.session.flush()

        self.session.expire_all()
        assert_that(skill.category, equal_to(None))
        assert_that(skill.queue_skill_cat, equal_to(None))

class TestCreator(DAOTestCase):

    def test_category(self):
        skill = QueueSkill(category='toto')

        self.session.add(skill)
        self.session.flush()

        assert_that(skill, has_properties(category='toto'))


class TestDeleter(DAOTestCase):

    def test_queue_skill_cat(self):
        skill_category = self.add_queue_skill_category()
        skill = self.add_queue_skill(catid=skill_category.id)

        self.session.delete(skill)
        self.session.flush()

        assert_that(inspect(skill).deleted)
        assert_that(not_(inspect(skill_category).deleted))
