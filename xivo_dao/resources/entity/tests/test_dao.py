# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import (assert_that,
                      contains,
                      equal_to,
                      has_items,
                      has_properties,
                      has_property,
                      is_not,
                      none)


from xivo_dao.alchemy.entity import Entity
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.entity import dao as entity_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestFind(DAOTestCase):

    def test_find_no_entity(self):
        result = entity_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        entity_row = self.add_entity(name='entity',
                                     display_name='Entity_Namé',
                                     description='description')

        entity = entity_dao.find(entity_row.id)

        assert_that(entity.id, equal_to(entity_row.id))
        assert_that(entity.name, equal_to(entity_row.name))
        assert_that(entity.display_name, equal_to(entity_row.display_name))
        assert_that(entity.description, equal_to(entity_row.description))


class TestGet(DAOTestCase):

    def test_get_no_entity(self):
        self.assertRaises(NotFoundError, entity_dao.get, 42)

    def test_get(self):
        entity_row = self.add_entity()

        entity = entity_dao.get(entity_row.id)

        assert_that(entity.id, equal_to(entity.id))


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, entity_dao.find_by, invalid=42)

    def test_find_by_display_name(self):
        entity_row = self.add_entity(name='Entité')

        entity = entity_dao.find_by(name='Entité')

        assert_that(entity.id, equal_to(entity_row.id))
        assert_that(entity.name, equal_to('Entité'))

    def test_given_entity_does_not_exist_then_returns_null(self):
        entity = entity_dao.find_by(name='42')

        assert_that(entity, none())


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, entity_dao.get_by, invalid=42)

    def test_get_by_name(self):
        entity_row = self.add_entity(name='Entité')

        entity = entity_dao.get_by(name='Entité')

        assert_that(entity.id, equal_to(entity_row.id))
        assert_that(entity.name, equal_to('Entité'))

    def test_given_entity_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, entity_dao.get_by, name='42')


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_entities(self):
        result = entity_dao.find_all_by(name='toto')

        assert_that(result, contains())

    def test_find_all_by_renamed_column(self):
        entity1 = self.add_entity(name='entity1', display_name='renamed')
        entity2 = self.add_entity(name='entity2', display_name='renamed')

        entities = entity_dao.find_all_by(display_name='renamed')

        assert_that(entities, has_items(has_property('id', entity1.id),
                                        has_property('id', entity2.id)))

    def test_find_all_by_native_column(self):
        entity1 = self.add_entity(name='bob', description='description')
        entity2 = self.add_entity(name='alice', description='description')

        entities = entity_dao.find_all_by(description='description')

        assert_that(entities, has_items(has_property('id', entity1.id),
                                        has_property('id', entity2.id)))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = entity_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_entities_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_entity_then_returns_one_result(self):
        entity = self.add_entity(name='bob')
        expected = SearchResult(1, [entity])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleEntities(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.entity1 = self.add_entity(name='Ashton', description='resto', display_name='Poutine')
        self.entity2 = self.add_entity(name='Beaugarton', description='bar')
        self.entity3 = self.add_entity(name='Casa', description='resto')
        self.entity4 = self.add_entity(name='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.entity2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.entity1])
        self.assert_search_returns_result(expected_resto, search='ton', description='resto')

        expected_bar = SearchResult(1, [self.entity2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.entity1, self.entity3, self.entity4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='name')

    def test_when_searching_with_a_custom_extra_argument(self):
        expected = SearchResult(1, [self.entity1])
        self.assert_search_returns_result(expected, display_name='Poutine')

        expected_all = SearchResult(3, [self.entity2, self.entity3, self.entity4])
        self.assert_search_returns_result(expected_all, display_name=None)

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4,
                                [self.entity1,
                                 self.entity2,
                                 self.entity3,
                                 self.entity4])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.entity4,
                                    self.entity3,
                                    self.entity2,
                                    self.entity1])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.entity1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.entity2, self.entity3, self.entity4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.entity2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='name',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        entity = Entity(name='Proformatique', description='')
        created_entity = entity_dao.create(entity)

        row = self.session.query(Entity).first()

        assert_that(created_entity, has_properties(id=row.id,
                                                   name="Proformatique",
                                                   description=''))

        assert_that(row, has_properties(id=is_not(none()),
                                        name='Proformatique',
                                        description=''))

    def test_create_with_all_fields(self):
        entity = Entity(name="Proformatique",
                        display_name='totoformatiqué',
                        description='informatique')

        created_entity = entity_dao.create(entity)

        row = self.session.query(Entity).first()

        assert_that(created_entity, has_properties(id=row.id,
                                                   name="Proformatique",
                                                   display_name='totoformatiqué',
                                                   description='informatique'))

        assert_that(row, has_properties(id=is_not(none()),
                                        name='Proformatique',
                                        displayname='totoformatiqué',
                                        description='informatique'))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        entity = entity_dao.create(Entity(name="Proformatique",
                                          display_name='totoformatiqué',
                                          description='informatique'))

        entity = entity_dao.get(entity.id)
        entity.name = 'Halala'
        entity.display_name = 'tata'
        entity.description = 'description'

        entity_dao.edit(entity)

        row = self.session.query(Entity).first()

        assert_that(row, has_properties(name='Halala',
                                        displayname='tata',
                                        description='description'))

    def test_edit_set_fields_to_null(self):
        entity = entity_dao.create(Entity(name="Proformatique",
                                          display_name='totoformatiqué',
                                          description='informatique'))

        entity = entity_dao.get(entity.id)
        entity.display_name = None

        entity_dao.edit(entity)

        row = self.session.query(Entity).first()

        assert_that(row, has_properties(display_name=none()))


class TestDelete(DAOTestCase):

    def test_delete(self):
        entity = entity_dao.create(Entity(name='Delete', description=''))
        entity = entity_dao.get(entity.id)

        entity_dao.delete(entity)

        row = self.session.query(Entity).first()
        assert_that(row, none())
