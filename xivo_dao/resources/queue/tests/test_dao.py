# -*- coding: UTF-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    has_items,
    has_properties,
    has_property,
    is_not,
    none,
)

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queue import Queue

from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as queue_dao


class TestQueueExist(DAOTestCase):

    def test_given_no_queue_then_returns_false(self):
        result = queue_dao.exists(1)

        assert_that(result, equal_to(False))

    def test_given_queue_exists_then_return_true(self):
        queue_row = self.add_queuefeatures()

        result = queue_dao.exists(queue_row.id)

        assert_that(result, equal_to(True))


class TestFind(DAOTestCase):

    def test_find_no_queue(self):
        result = queue_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        queue_row = self.add_queuefeatures()

        queue = queue_dao.find(queue_row.id)

        assert_that(queue, equal_to(queue_row))


class TestGet(DAOTestCase):

    def test_get_no_queue(self):
        self.assertRaises(NotFoundError, queue_dao.get, 42)

    def test_get(self):
        queue_row = self.add_queuefeatures()

        queue = queue_dao.get(queue_row.id)

        assert_that(queue, equal_to(queue_row))


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, queue_dao.find_by, invalid=42)

    def test_find_by_name(self):
        queue_row = self.add_queuefeatures(name='myname')

        queue = queue_dao.find_by(name='myname')

        assert_that(queue, equal_to(queue_row))
        assert_that(queue.name, equal_to('myname'))

    def test_find_by_preprocess_subroutine(self):
        queue_row = self.add_queuefeatures(preprocess_subroutine='mysubroutine')

        queue = queue_dao.find_by(preprocess_subroutine='mysubroutine')

        assert_that(queue, equal_to(queue_row))
        assert_that(queue.preprocess_subroutine, equal_to('mysubroutine'))

    def test_given_queue_does_not_exist_then_returns_null(self):
        queue = queue_dao.find_by(id=42)

        assert_that(queue, none())


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, queue_dao.get_by, invalid=42)

    def test_get_by_name(self):
        queue_row = self.add_queuefeatures(name='myname')

        queue = queue_dao.get_by(name='myname')

        assert_that(queue, equal_to(queue_row))
        assert_that(queue.name, equal_to('myname'))

    def test_get_by_preprocess_subroutine(self):
        queue_row = self.add_queuefeatures(preprocess_subroutine='MySubroutine')

        queue = queue_dao.get_by(preprocess_subroutine='MySubroutine')

        assert_that(queue, equal_to(queue_row))
        assert_that(queue.preprocess_subroutine, equal_to('MySubroutine'))

    def test_given_queue_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, queue_dao.get_by, id='42')


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_queue(self):
        result = queue_dao.find_all_by(name='toto')

        assert_that(result, contains())

    def test_find_all_by_custom_column(self):
        pass

    def test_find_all_by_native_column(self):
        queue1 = self.add_queuefeatures(preprocess_subroutine='subroutine')
        queue2 = self.add_queuefeatures(preprocess_subroutine='subroutine')

        queues = queue_dao.find_all_by(preprocess_subroutine='subroutine')

        assert_that(queues, has_items(has_property('id', queue1.id),
                                      has_property('id', queue2.id)))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = queue_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_queue_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_queue_then_returns_one_result(self):
        queue = self.add_queuefeatures()
        expected = SearchResult(1, [queue])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleQueue(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.queue1 = self.add_queuefeatures(name='Ashton', preprocess_subroutine='resto')
        self.queue2 = self.add_queuefeatures(name='Beaugarton', preprocess_subroutine='bar')
        self.queue3 = self.add_queuefeatures(name='Casa', preprocess_subroutine='resto')
        self.queue4 = self.add_queuefeatures(name='Dunkin', preprocess_subroutine='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.queue2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.queue1])
        self.assert_search_returns_result(expected_resto, search='ton', preprocess_subroutine='resto')

        expected_bar = SearchResult(1, [self.queue2])
        self.assert_search_returns_result(expected_bar, search='ton', preprocess_subroutine='bar')

        expected_all_resto = SearchResult(3, [self.queue1, self.queue3, self.queue4])
        self.assert_search_returns_result(expected_all_resto, preprocess_subroutine='resto', order='name')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4,
                                [self.queue1,
                                 self.queue2,
                                 self.queue3,
                                 self.queue4])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.queue4,
                                    self.queue3,
                                    self.queue2,
                                    self.queue1])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.queue1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.queue2, self.queue3, self.queue4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.queue2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='name',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        queue = QueueFeatures(name='myqueue', displayname='')
        created_queue = queue_dao.create(queue)

        row = self.session.query(QueueFeatures).first()

        assert_that(created_queue, equal_to(row))
        assert_that(created_queue, has_properties(
            id=is_not(none()),
            name='myqueue',
            caller_id_mode=None,
            caller_id_name=None,
            # TODO add other fields
            enabled=True,
        ))

    def test_create_with_all_fields(self):
        queue = QueueFeatures(
            name='MyQueue',
            displayname='',  # TODO rename displayname with sed
            caller_id_mode='prepend',
            caller_id_name='toto',
            # TODO add other fields
            enabled=False,
        )

        created_queue = queue_dao.create(queue)

        row = self.session.query(QueueFeatures).first()

        assert_that(created_queue, equal_to(row))
        assert_that(created_queue, has_properties(
            id=is_not(none()),
            name='MyQueue',
            caller_id_mode='prepend',
            caller_id_name='toto',
            # TODO add other fields
            enabled=False,
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        queue = queue_dao.create(QueueFeatures(
            name='MyQueue',
            displayname='',
            caller_id_mode='prepend',
            caller_id_name='toto',
            # TODO add other fields
            enabled=True,
        ))

        queue = queue_dao.get(queue.id)
        queue.name = 'other_name'
        queue.displayname = 'other_displayname'
        queue.caller_id_mode = 'overwrite'
        queue.caller_id_name = 'bob'
        queue.enabled = False
        # TODO add other fields
        queue_dao.edit(queue)

        row = self.session.query(QueueFeatures).first()

        assert_that(queue, equal_to(row))
        assert_that(queue, has_properties(
            id=is_not(none()),
            name='other_name',
            displayname='other_displayname',
            caller_id_mode='overtwrite',
            caller_id_name='bob',
            # TODO add other fields
            enabled=False,
        ))

    def test_edit_set_fields_to_null(self):
        queue = queue_dao.create(QueueFeatures(
            name='MyQueue',
            displayname='',
            caller_id_mode='prepend',
            caller_id_name='toto',
            # TODO add other fields
            preprocess_subroutine='t',
        ))

        queue = queue_dao.get(queue.id)
        # TODO add other fields
        queue.caller_id_mode = None
        queue.caller_id_name = None
        queue.preprocess_subroutine = None
        queue_dao.edit(queue)

        row = self.session.query(QueueFeatures).first()
        assert_that(queue, equal_to(row))
        assert_that(row, has_properties(
            preprocess_subroutine=none(),
            caller_id_mode=none(),
            caller_id_name=none(),
            # TODO add other fields
        ))

    def test_edit_queue_name(self):
        queue_dao.create(QueueFeatures(name='MyQueue', displayname=''))
        self.session.expunge_all()

        meta_queue = self.session.query(Queue).first()
        assert_that(meta_queue.name, equal_to('MyQueue'))

        queue = self.session.query(QueueFeatures).first()
        queue.name = 'OtherName'
        queue_dao.edit(queue)

        meta_queue = self.session.query(Queue).first()
        assert_that(meta_queue.name, equal_to('OtherName'))


class TestDelete(DAOTestCase):

    def test_delete(self):
        queue = self.add_queuefeatures()

        queue_dao.delete(queue)

        row = self.session.query(QueueFeatures).first()
        assert_that(row, none())

    def test_when_deleting_then_extension_are_dissociated(self):
        queue = self.add_queuefeatures()
        extension = self.add_extension(type='queue', typeval=str(queue.id))

        queue_dao.delete(queue)

        row = self.session.query(Extension).first()
        assert_that(row.id, equal_to(extension.id))
        assert_that(row, has_properties(type='user', typeval='0'))

    def test_when_deleting_then_dialactions_are_unlinked(self):
        queue = self.add_queuefeatures()
        self.add_dialaction(action='queue', actionarg1=str(queue.id), linked=1)

        queue_dao.delete(queue)

        dialaction = self.session.query(Dialaction).filter(Dialaction.actionarg1 == str(queue.id)).first()
        assert_that(dialaction, has_properties(linked=0))
