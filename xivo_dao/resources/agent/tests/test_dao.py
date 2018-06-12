# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    has_items,
    has_properties,
    has_property,
    instance_of,
    none,
)

from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent

from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as agent_dao


class TestAgentExist(DAOTestCase):

    def test_given_no_agent_then_returns_false(self):
        result = agent_dao.exists(1)

        assert_that(result, equal_to(False))

    def test_given_agent_exists_then_return_true(self):
        agent_row = self.add_agent()

        result = agent_dao.exists(agent_row.id)

        assert_that(result, equal_to(True))


class TestFind(DAOTestCase):

    def test_find_no_agent(self):
        result = agent_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        agent_row = self.add_agent()

        agent = agent_dao.find(agent_row.id)

        assert_that(agent, equal_to(agent_row))


class TestGet(DAOTestCase):

    def test_get_no_agent(self):
        self.assertRaises(NotFoundError, agent_dao.get, 42)

    def test_get(self):
        agent_row = self.add_agent()

        agent = agent_dao.get(agent_row.id)

        assert_that(agent, equal_to(agent_row))


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, agent_dao.find_by, invalid=42)

    def test_find_by_firstname(self):
        agent_row = self.add_agent(firstname='myfirstname')

        agent = agent_dao.find_by(firstname='myfirstname')

        assert_that(agent, equal_to(agent_row))
        assert_that(agent.firstname, equal_to('myfirstname'))

    def test_find_by_lastname(self):
        agent_row = self.add_agent(lastname='mylastname')

        agent = agent_dao.find_by(lastname='mylastname')

        assert_that(agent, equal_to(agent_row))
        assert_that(agent.lastname, equal_to('mylastname'))

    def test_find_by_preprocess_subroutine(self):
        agent_row = self.add_agent(preprocess_subroutine='mysubroutine')

        agent = agent_dao.find_by(preprocess_subroutine='mysubroutine')

        assert_that(agent, equal_to(agent_row))
        assert_that(agent.preprocess_subroutine, equal_to('mysubroutine'))

    def test_given_agent_does_not_exist_then_returns_null(self):
        agent = agent_dao.find_by(id=42)

        assert_that(agent, none())


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, agent_dao.get_by, invalid=42)

    def test_get_by_firstname(self):
        agent_row = self.add_agent(firstname='myfirstname')

        agent = agent_dao.get_by(firstname='myfirstname')

        assert_that(agent, equal_to(agent_row))
        assert_that(agent.firstname, equal_to('myfirstname'))

    def test_get_by_lastname(self):
        agent_row = self.add_agent(lastname='mylastname')

        agent = agent_dao.get_by(lastname='mylastname')

        assert_that(agent, equal_to(agent_row))
        assert_that(agent.lastname, equal_to('mylastname'))

    def test_get_by_preprocess_subroutine(self):
        agent_row = self.add_agent(preprocess_subroutine='MySubroutine')

        agent = agent_dao.get_by(preprocess_subroutine='MySubroutine')

        assert_that(agent, equal_to(agent_row))
        assert_that(agent.preprocess_subroutine, equal_to('MySubroutine'))

    def test_given_agent_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, agent_dao.get_by, id='42')


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_agent(self):
        result = agent_dao.find_all_by(firstname='toto')

        assert_that(result, contains())

    def test_find_all_by_custom_column(self):
        pass

    def test_find_all_by_native_column(self):
        agent1 = self.add_agent(preprocess_subroutine='subroutine')
        agent2 = self.add_agent(preprocess_subroutine='subroutine')

        agents = agent_dao.find_all_by(preprocess_subroutine='subroutine')

        assert_that(agents, has_items(has_property('id', agent1.id),
                                      has_property('id', agent2.id)))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = agent_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_agent_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_agent_then_returns_one_result(self):
        agent = self.add_agent()
        expected = SearchResult(1, [agent])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleAgent(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.agent1 = self.add_agent(firstname='Ashton', preprocess_subroutine='resto')
        self.agent2 = self.add_agent(firstname='Beaugarton', preprocess_subroutine='bar')
        self.agent3 = self.add_agent(firstname='Casa', preprocess_subroutine='resto')
        self.agent4 = self.add_agent(firstname='Dunkin', preprocess_subroutine='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.agent2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.agent1])
        self.assert_search_returns_result(expected_resto, search='ton', preprocess_subroutine='resto')

        expected_bar = SearchResult(1, [self.agent2])
        self.assert_search_returns_result(expected_bar, search='ton', preprocess_subroutine='bar')

        expected_all_resto = SearchResult(3, [self.agent1, self.agent3, self.agent4])
        self.assert_search_returns_result(expected_all_resto, preprocess_subroutine='resto', order='firstname')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4,
                                [self.agent1,
                                 self.agent2,
                                 self.agent3,
                                 self.agent4])

        self.assert_search_returns_result(expected, order='firstname')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.agent4,
                                    self.agent3,
                                    self.agent2,
                                    self.agent1])

        self.assert_search_returns_result(expected, order='firstname', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.agent1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.agent2, self.agent3, self.agent4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.agent2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='firstname',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        agent = Agent(number='1234')
        created_agent = agent_dao.create(agent)

        row = self.session.query(Agent).first()

        assert_that(created_agent, equal_to(row))
        assert_that(created_agent, has_properties(
            id=instance_of(int),
            number='1234',
            firstname=None,
            lastname=None,
            passwd=None,
            language=None,
            description=None,
            preprocess_subroutine=None,
        ))

    def test_create_with_all_fields(self):
        agent = Agent(
            number='1234',
            firstname='first',
            lastname='last',
            passwd='pwd',
            language='en',
            description='description',
            preprocess_subroutine='Subroutine',
        )

        created_agent = agent_dao.create(agent)

        row = self.session.query(Agent).first()

        assert_that(created_agent, equal_to(row))
        assert_that(created_agent, has_properties(
            id=instance_of(int),
            number='1234',
            firstname='first',
            lastname='last',
            passwd='pwd',
            language='en',
            description='description',
            preprocess_subroutine='Subroutine',
        ))

    def test_create_fill_default_values(self):
        agent = Agent(number='1234')

        created_agent = agent_dao.create(agent)

        row = self.session.query(Agent).first()

        assert_that(created_agent, equal_to(row))
        assert_that(created_agent, has_properties(
            numgroup=1,
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        agent = agent_dao.create(Agent(
            number='1234',
            firstname=None,
            lastname=None,
            passwd=None,
            language=None,
            description=None,
            preprocess_subroutine=None,
        ))

        agent = agent_dao.get(agent.id)
        agent.number = '1234'
        agent.firstname = 'firstname'
        agent.lastname = 'lastname'
        agent.passwd = 'passwd'
        agent.language = 'en'
        agent.description = 'desc'
        agent.preprocess_subroutine = 'routine'
        agent_dao.edit(agent)

        row = self.session.query(Agent).first()

        assert_that(agent, equal_to(row))
        assert_that(agent, has_properties(
            id=instance_of(int),
            number='1234',
            firstname='firstname',
            lastname='lastname',
            passwd='passwd',
            language='en',
            description='desc',
            preprocess_subroutine='routine',
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        agent = self.add_agent()

        agent_dao.delete(agent)

        row = self.session.query(Agent).first()
        assert_that(row, none())
