# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    empty,
    equal_to,
    has_items,
    has_properties,
    has_property,
    none,
    not_,
    not_none,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.queueskillrule import QueueSkillRule
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as skill_rule_dao


class TestFind(DAOTestCase):
    def test_find_no_skill_rule(self):
        result = skill_rule_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        skill_rule_row = self.add_queue_skill_rule()

        skill_rule = skill_rule_dao.find(skill_rule_row.id)

        assert_that(skill_rule, equal_to(skill_rule_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()

        skill_rule = self.add_queue_skill_rule(tenant_uuid=tenant.uuid)

        result = skill_rule_dao.find(skill_rule.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(skill_rule))

        result = skill_rule_dao.find(
            skill_rule.id, tenant_uuids=[self.default_tenant.uuid]
        )
        assert_that(result, none())


class TestGet(DAOTestCase):
    def test_get_no_skill_rule(self):
        self.assertRaises(NotFoundError, skill_rule_dao.get, 42)

    def test_get(self):
        skill_rule_row = self.add_queue_skill_rule()

        skill_rule = skill_rule_dao.get(skill_rule_row.id)

        assert_that(skill_rule.id, equal_to(skill_rule.id))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        skill_rule_row = self.add_queue_skill_rule(tenant_uuid=tenant.uuid)
        skill_rule = skill_rule_dao.get(skill_rule_row.id, tenant_uuids=[tenant.uuid])
        assert_that(skill_rule, equal_to(skill_rule_row))

        skill_rule_row = self.add_queue_skill_rule()
        self.assertRaises(
            NotFoundError,
            skill_rule_dao.get,
            skill_rule_row.id,
            tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, skill_rule_dao.find_by, invalid=42)

    def test_find_by_name(self):
        skill_rule_row = self.add_queue_skill_rule(name='123')

        skill_rule = skill_rule_dao.find_by(name='123')

        assert_that(skill_rule, equal_to(skill_rule_row))
        assert_that(skill_rule.name, equal_to('123'))

    def test_given_skill_rule_does_not_exist_then_returns_null(self):
        skill_rule = skill_rule_dao.find_by(name='42')

        assert_that(skill_rule, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        skill_rule_row = self.add_queue_skill_rule()
        skill_rule = skill_rule_dao.find_by(
            name=skill_rule_row.name, tenant_uuids=[tenant.uuid]
        )
        assert_that(skill_rule, none())

        skill_rule_row = self.add_queue_skill_rule(tenant_uuid=tenant.uuid)
        skill_rule = skill_rule_dao.find_by(
            name=skill_rule_row.name, tenant_uuids=[tenant.uuid]
        )
        assert_that(skill_rule, equal_to(skill_rule_row))


class TestGetBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, skill_rule_dao.get_by, invalid=42)

    def test_get_by_name(self):
        skill_rule_row = self.add_queue_skill_rule(name='123')

        skill_rule = skill_rule_dao.get_by(name='123')

        assert_that(skill_rule, equal_to(skill_rule_row))
        assert_that(skill_rule.name, equal_to('123'))

    def test_given_skill_rule_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, skill_rule_dao.get_by, name='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        skill_rule_row = self.add_queue_skill_rule()
        self.assertRaises(
            NotFoundError,
            skill_rule_dao.get_by,
            id=skill_rule_row.id,
            tenant_uuids=[tenant.uuid],
        )

        skill_rule_row = self.add_queue_skill_rule(tenant_uuid=tenant.uuid)
        skill_rule = skill_rule_dao.get_by(
            id=skill_rule_row.id, tenant_uuids=[tenant.uuid]
        )
        assert_that(skill_rule, equal_to(skill_rule_row))


class TestFindAllBy(DAOTestCase):
    def test_find_all_by_no_skill_rules(self):
        result = skill_rule_dao.find_all_by(name='123')

        assert_that(result, contains_exactly())

    def test_find_all_by(self):
        skill_rule = self.add_queue_skill_rule(name='description')

        skill_rules = skill_rule_dao.find_all_by(name='description')

        assert_that(
            skill_rules,
            has_items(
                has_property('id', skill_rule.id),
            ),
        )

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        skill_rule1 = self.add_queue_skill_rule(tenant_uuid=tenant.uuid)
        skill_rule2 = self.add_queue_skill_rule()

        tenants = [tenant.uuid, self.default_tenant.uuid]
        skill_rules = skill_rule_dao.find_all_by(tenant_uuids=tenants)
        assert_that(skill_rules, has_items(skill_rule1, skill_rule2))

        tenants = [tenant.uuid]
        skill_rules = skill_rule_dao.find_all_by(tenant_uuids=tenants)
        assert_that(
            skill_rules, all_of(has_items(skill_rule1), not_(has_items(skill_rule2)))
        )


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = skill_rule_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_skill_rules_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_skill_rule_then_returns_one_result(self):
        skill_rule = self.add_queue_skill_rule()
        expected = SearchResult(1, [skill_rule])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleSkillRules(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.skill_rule1 = self.add_queue_skill_rule(name='Ashton')
        self.skill_rule2 = self.add_queue_skill_rule(name='Beaugarton')
        self.skill_rule3 = self.add_queue_skill_rule(name='Casa')
        self.skill_rule4 = self.add_queue_skill_rule(name='Dunkin')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.skill_rule2])

        self.assert_search_returns_result(expected, search='arton')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4,
            [
                self.skill_rule1,
                self.skill_rule2,
                self.skill_rule3,
                self.skill_rule4,
            ],
        )

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4,
            [
                self.skill_rule4,
                self.skill_rule3,
                self.skill_rule2,
                self.skill_rule1,
            ],
        )

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.skill_rule1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_name_of_items(self):
        expected = SearchResult(
            4, [self.skill_rule2, self.skill_rule3, self.skill_rule4]
        )

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.skill_rule2])

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

        skill_rule_1 = self.add_queue_skill_rule(name='a', tenant_uuid=tenant_1.uuid)
        skill_rule_2 = self.add_queue_skill_rule(name='b', tenant_uuid=tenant_2.uuid)
        skill_rule_3 = self.add_queue_skill_rule(name='c', tenant_uuid=tenant_3.uuid)

        expected = SearchResult(2, [skill_rule_1, skill_rule_2])
        self.assert_search_returns_result(
            expected, tenant_uuids=[tenant_1.uuid, tenant_2.uuid]
        )

        expected = SearchResult(0, [])
        self.assert_search_returns_result(expected, tenant_uuids=[])

        expected = SearchResult(3, [skill_rule_1, skill_rule_2, skill_rule_3])
        self.assert_search_returns_result(expected)


class TestCreate(DAOTestCase):
    def test_create_minimal_fields(self):
        skill_rule = QueueSkillRule(
            tenant_uuid=self.default_tenant.uuid, name='SkillRule'
        )
        skill_rule = skill_rule_dao.create(skill_rule)

        self.session.expire_all()
        assert_that(inspect(skill_rule).persistent)
        assert_that(
            skill_rule,
            has_properties(
                id=not_none(),
                name='SkillRule',
                rules=[],
            ),
        )

    def test_create_with_all_fields(self):
        skill_rule = QueueSkillRule(
            tenant_uuid=self.default_tenant.uuid,
            name='MyName',
            rules=['rule1', 'rule2'],
        )
        skill_rule = skill_rule_dao.create(skill_rule)

        self.session.expire_all()
        assert_that(inspect(skill_rule).persistent)
        assert_that(
            skill_rule,
            has_properties(
                name='MyName',
                rules=['rule1', 'rule2'],
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        skill_rule = self.add_queue_skill_rule(
            name='MyName',
            rules=['rule1', 'rule2'],
        )

        self.session.expire_all()
        skill_rule.name = 'OtherName'
        skill_rule.rules = ['rule3']

        skill_rule_dao.edit(skill_rule)

        self.session.expire_all()
        assert_that(
            skill_rule,
            has_properties(
                name='OtherName',
                rules=['rule3'],
            ),
        )

    def test_edit_set_fields_to_null(self):
        skill_rule = self.add_queue_skill_rule(
            name='MyName',
            rules=['rule1', 'rule2'],
        )

        self.session.expire_all()
        skill_rule.name = 'OtherName'
        skill_rule.rules = []

        skill_rule_dao.edit(skill_rule)

        self.session.expire_all()
        assert_that(
            skill_rule,
            has_properties(
                name='OtherName',
                rules=empty(),
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        skill_rule = self.add_queue_skill_rule()

        skill_rule_dao.delete(skill_rule)

        assert_that(inspect(skill_rule).deleted)
