# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    equal_to,
    has_items,
    has_properties,
    has_property,
    none,
    not_,
    not_none,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.queueskill import QueueSkill
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as skill_dao


class TestFind(DAOTestCase):
    def test_find_no_skill(self):
        result = skill_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        skill_row = self.add_queue_skill()

        skill = skill_dao.find(skill_row.id)

        assert_that(skill, equal_to(skill_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()

        skill = self.add_queue_skill(tenant_uuid=tenant.uuid)

        result = skill_dao.find(skill.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(skill))

        result = skill_dao.find(skill.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):
    def test_get_no_skill(self):
        self.assertRaises(NotFoundError, skill_dao.get, 42)

    def test_get(self):
        skill_row = self.add_queue_skill()

        skill = skill_dao.get(skill_row.id)

        assert_that(skill.id, equal_to(skill.id))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        skill_row = self.add_queue_skill(tenant_uuid=tenant.uuid)
        skill = skill_dao.get(skill_row.id, tenant_uuids=[tenant.uuid])
        assert_that(skill, equal_to(skill_row))

        skill_row = self.add_queue_skill()
        self.assertRaises(
            NotFoundError, skill_dao.get, skill_row.id, tenant_uuids=[tenant.uuid]
        )


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, skill_dao.find_by, invalid=42)

    def test_find_by_name(self):
        skill_row = self.add_queue_skill(name='123')

        skill = skill_dao.find_by(name='123')

        assert_that(skill, equal_to(skill_row))
        assert_that(skill.name, equal_to('123'))

    def test_given_skill_does_not_exist_then_returns_null(self):
        skill = skill_dao.find_by(name='42')

        assert_that(skill, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        skill_row = self.add_queue_skill()
        skill = skill_dao.find_by(name=skill_row.name, tenant_uuids=[tenant.uuid])
        assert_that(skill, none())

        skill_row = self.add_queue_skill(tenant_uuid=tenant.uuid)
        skill = skill_dao.find_by(name=skill_row.name, tenant_uuids=[tenant.uuid])
        assert_that(skill, equal_to(skill_row))


class TestGetBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, skill_dao.get_by, invalid=42)

    def test_get_by_name(self):
        skill_row = self.add_queue_skill(name='123')

        skill = skill_dao.get_by(name='123')

        assert_that(skill, equal_to(skill_row))
        assert_that(skill.name, equal_to('123'))

    def test_given_skill_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, skill_dao.get_by, name='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        skill_row = self.add_queue_skill()
        self.assertRaises(
            NotFoundError,
            skill_dao.get_by,
            id=skill_row.id,
            tenant_uuids=[tenant.uuid],
        )

        skill_row = self.add_queue_skill(tenant_uuid=tenant.uuid)
        skill = skill_dao.get_by(id=skill_row.id, tenant_uuids=[tenant.uuid])
        assert_that(skill, equal_to(skill_row))


class TestFindAllBy(DAOTestCase):
    def test_find_all_by_no_skills(self):
        result = skill_dao.find_all_by(name='123')

        assert_that(result, contains_exactly())

    def test_find_all_by(self):
        skill1 = self.add_queue_skill(description='description')
        skill2 = self.add_queue_skill(description='description')

        skills = skill_dao.find_all_by(description='description')

        assert_that(
            skills,
            has_items(
                has_property('id', skill1.id),
                has_property('id', skill2.id),
            ),
        )

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        skill1 = self.add_queue_skill(tenant_uuid=tenant.uuid)
        skill2 = self.add_queue_skill()

        tenants = [tenant.uuid, self.default_tenant.uuid]
        skills = skill_dao.find_all_by(tenant_uuids=tenants)
        assert_that(skills, has_items(skill1, skill2))

        tenants = [tenant.uuid]
        skills = skill_dao.find_all_by(tenant_uuids=tenants)
        assert_that(skills, all_of(has_items(skill1), not_(has_items(skill2))))


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = skill_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_skills_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_skill_then_returns_one_result(self):
        skill = self.add_queue_skill()
        expected = SearchResult(1, [skill])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleSkills(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.skill1 = self.add_queue_skill(name='Ashton', description='resto')
        self.skill2 = self.add_queue_skill(name='Beaugarton', description='bar')
        self.skill3 = self.add_queue_skill(name='Casa', description='resto')
        self.skill4 = self.add_queue_skill(name='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.skill2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.skill1])
        self.assert_search_returns_result(
            expected_resto, search='ton', description='resto'
        )

        expected_bar = SearchResult(1, [self.skill2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.skill1, self.skill3, self.skill4])
        self.assert_search_returns_result(
            expected_all_resto, description='resto', order='description'
        )

    def test_when_searching_with_a_custom_extra_argument(self):
        expected_allow = SearchResult(1, [self.skill2])
        self.assert_search_returns_result(expected_allow, description='bar')

        expected_all_deny = SearchResult(3, [self.skill1, self.skill3, self.skill4])
        self.assert_search_returns_result(expected_all_deny, description='resto')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4,
            [
                self.skill1,
                self.skill2,
                self.skill3,
                self.skill4,
            ],
        )

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4,
            [
                self.skill4,
                self.skill3,
                self.skill2,
                self.skill1,
            ],
        )

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.skill1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.skill2, self.skill3, self.skill4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.skill2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='name',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestSearchGivenMultipleTenants(TestSearch):
    def test_multiple_tenants(self):
        tenant_1 = self.add_tenant()
        tenant_2 = self.add_tenant()
        tenant_3 = self.add_tenant()

        skill_1 = self.add_queue_skill(name='a', tenant_uuid=tenant_1.uuid)
        skill_2 = self.add_queue_skill(name='b', tenant_uuid=tenant_2.uuid)
        skill_3 = self.add_queue_skill(name='c', tenant_uuid=tenant_3.uuid)

        expected = SearchResult(2, [skill_1, skill_2])
        self.assert_search_returns_result(
            expected, tenant_uuids=[tenant_1.uuid, tenant_2.uuid]
        )

        expected = SearchResult(0, [])
        self.assert_search_returns_result(expected, tenant_uuids=[])

        expected = SearchResult(3, [skill_1, skill_2, skill_3])
        self.assert_search_returns_result(expected)


class TestCreate(DAOTestCase):
    def test_create_minimal_fields(self):
        skill = QueueSkill(tenant_uuid=self.default_tenant.uuid, name='name')
        skill = skill_dao.create(skill)

        assert_that(inspect(skill).persistent)
        assert_that(
            skill,
            has_properties(
                id=not_none(),
                name='name',
                description=None,
            ),
        )

    def test_create_with_all_fields(self):
        skill = QueueSkill(
            tenant_uuid=self.default_tenant.uuid,
            name='MyName',
            description='MyDescription',
        )
        skill = skill_dao.create(skill)

        assert_that(inspect(skill).persistent)
        assert_that(
            skill,
            has_properties(
                name='MyName',
                description='MyDescription',
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        skill = self.add_queue_skill(
            name='MyName',
            description='MyDescription',
        )

        self.session.expire_all()
        skill.name = 'OtherName'
        skill.description = 'OtherDescription'

        skill_dao.edit(skill)

        self.session.expire_all()
        assert_that(
            skill,
            has_properties(
                name='OtherName',
                description='OtherDescription',
            ),
        )

    def test_edit_set_fields_to_null(self):
        skill = self.add_queue_skill(
            name='MyName',
            description='MyDescription',
        )

        self.session.expire_all()
        skill.description = None

        skill_dao.edit(skill)

        self.session.expire_all()
        assert_that(
            skill,
            has_properties(
                description=none(),
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        skill = self.add_queue_skill()

        skill_dao.delete(skill)

        assert_that(inspect(skill).deleted)
