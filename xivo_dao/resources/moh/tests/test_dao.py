# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      contains,
                      equal_to,
                      has_items,
                      has_properties,
                      has_property,
                      is_not,
                      none)

from xivo_dao.alchemy.moh import MOH
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.moh import dao as moh_dao
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

UUID = 'abc-123-4567'


class TestFind(DAOTestCase):

    def test_find_no_moh(self):
        result = moh_dao.find(UUID)

        assert_that(result, none())

    def test_find(self):
        moh_row = self.add_moh()

        moh = moh_dao.find(moh_row.uuid)

        assert_that(moh, equal_to(moh_row))


class TestGet(DAOTestCase):

    def test_get_no_moh(self):
        self.assertRaises(NotFoundError, moh_dao.get, UUID)

    def test_get(self):
        moh_row = self.add_moh()

        moh = moh_dao.get(moh_row.uuid)

        assert_that(moh, equal_to(moh_row))


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, moh_dao.find_by, invalid=42)

    def test_find_by_name(self):
        moh_row = self.add_moh(name='myname')

        moh = moh_dao.find_by(name='myname')

        assert_that(moh, equal_to(moh_row))
        assert_that(moh.name, equal_to('myname'))

    def test_find_by_label(self):
        moh_row = self.add_moh(label='mylabel')

        moh = moh_dao.find_by(label='mylabel')

        assert_that(moh, equal_to(moh_row))
        assert_that(moh.label, equal_to('mylabel'))

    def test_given_moh_does_not_exist_then_returns_null(self):
        moh = moh_dao.find_by(uuid=UUID)

        assert_that(moh, none())


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, moh_dao.get_by, invalid=42)

    def test_get_by_name(self):
        moh_row = self.add_moh(name='myname')

        moh = moh_dao.get_by(name='myname')

        assert_that(moh, equal_to(moh_row))
        assert_that(moh.name, equal_to('myname'))

    def test_get_by_label(self):
        moh_row = self.add_moh(label='mylabel')

        moh = moh_dao.get_by(label='mylabel')

        assert_that(moh, equal_to(moh_row))
        assert_that(moh.label, equal_to('mylabel'))

    def test_given_moh_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, moh_dao.get_by, uuid=UUID)


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_moh(self):
        result = moh_dao.find_all_by(label='toto')

        assert_that(result, contains())

    def test_find_all_by_native_column(self):
        moh1 = self.add_moh(label='mymoh')
        moh2 = self.add_moh(label='mymoh')

        mohs = moh_dao.find_all_by(label='mymoh')

        assert_that(mohs, has_items(has_property('uuid', moh1.uuid),
                                    has_property('uuid', moh2.uuid)))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = moh_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_moh_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_moh_then_returns_one_result(self):
        moh = self.add_moh()
        expected = SearchResult(1, [moh])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleMOH(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.moh1 = self.add_moh(label='Ashton', name='resto1')
        self.moh2 = self.add_moh(label='Beaugarton', name='bar2')
        self.moh3 = self.add_moh(label='Casa', name='resto3')
        self.moh4 = self.add_moh(label='Dunkin', name='resto4')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.moh2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.moh1])
        self.assert_search_returns_result(expected_resto, search='ton', name='resto1')

        expected_bar = SearchResult(1, [self.moh2])
        self.assert_search_returns_result(expected_bar, search='ton', name='bar2')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4,
                                [self.moh1,
                                 self.moh2,
                                 self.moh3,
                                 self.moh4])

        self.assert_search_returns_result(expected, order='label')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.moh4,
                                    self.moh3,
                                    self.moh2,
                                    self.moh1])

        self.assert_search_returns_result(expected, order='label', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.moh1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.moh2, self.moh3, self.moh4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.moh3])

        self.assert_search_returns_result(expected,
                                          search='resto',
                                          order='label',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        moh = MOH(name='mymoh',
                  mode='files')
        created_moh = moh_dao.create(moh)

        row = self.session.query(MOH).first()

        assert_that(created_moh, equal_to(row))
        assert_that(created_moh, has_properties(uuid=is_not(none()),
                                                name='mymoh',
                                                label=none(),
                                                mode='files',
                                                application=none(),
                                                sort=none()))

    def test_create_with_all_fields(self):
        moh = MOH(name='mymoh',
                  label='moh, you\'re mine',
                  mode='files',
                  application='/bin/false unused',
                  sort='random')

        created_moh = moh_dao.create(moh)

        row = self.session.query(MOH).first()

        assert_that(created_moh, equal_to(row))
        assert_that(created_moh, has_properties(uuid=is_not(none()),
                                                name='mymoh',
                                                label='moh, you\'re mine',
                                                mode='files',
                                                application='/bin/false unused',
                                                sort='random'))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        moh = moh_dao.create(MOH(name='mymoh',
                                 label='moh, you\'re mine',
                                 mode='files',
                                 application='/bin/false unused',
                                 sort='random'))

        moh = moh_dao.get(moh.uuid)
        moh.name = 'zmymoh'
        moh.label = 'lol'
        moh.mode = 'custom'
        moh.application = '/bin/true'
        moh.sort = 'alpha'

        moh_dao.edit(moh)

        row = self.session.query(MOH).first()

        assert_that(moh, equal_to(row))
        assert_that(moh, has_properties(uuid=is_not(none()),
                                        name='zmymoh',
                                        label='lol',
                                        mode='custom',
                                        application='/bin/true',
                                        sort='alpha'))

    def test_edit_set_fields_to_null(self):
        moh = moh_dao.create(MOH(name='mymoh',
                                 label='moh, you\'re mine',
                                 mode='files',
                                 application='/bin/false unused',
                                 sort='random'))

        moh = moh_dao.get(moh.uuid)
        moh.label = None
        moh.application = None
        moh.sort = None

        moh_dao.edit(moh)

        row = self.session.query(MOH).first()

        assert_that(moh, equal_to(row))
        assert_that(moh, has_properties(uuid=is_not(none()),
                                        name='mymoh',
                                        label=none(),
                                        mode='files',
                                        application=none(),
                                        sort=none()))


class TestDelete(DAOTestCase):

    def test_delete(self):
        moh = self.add_moh()

        moh_dao.delete(moh)

        row = self.session.query(MOH).first()
        assert_that(row, none())
