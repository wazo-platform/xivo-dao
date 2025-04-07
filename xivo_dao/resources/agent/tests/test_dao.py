# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
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
    instance_of,
    none,
    not_,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent
from xivo_dao.alchemy.agentqueueskill import AgentQueueSkill
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as agent_dao


class TestFind(DAOTestCase):
    def test_find_no_agent(self):
        result = agent_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        agent_row = self.add_agent()

        agent = agent_dao.find(agent_row.id)

        assert_that(agent, equal_to(agent_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()

        agent = self.add_agent(tenant_uuid=tenant.uuid)

        result = agent_dao.find(agent.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(agent))

        result = agent_dao.find(agent.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):
    def test_get_no_agent(self):
        self.assertRaises(NotFoundError, agent_dao.get, 42)

    def test_get(self):
        agent_row = self.add_agent()

        agent = agent_dao.get(agent_row.id)

        assert_that(agent, equal_to(agent_row))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        agent_row = self.add_agent(tenant_uuid=tenant.uuid)
        agent = agent_dao.get(agent_row.id, tenant_uuids=[tenant.uuid])
        assert_that(agent, equal_to(agent_row))

        agent_row = self.add_agent()
        self.assertRaises(
            NotFoundError, agent_dao.get, agent_row.id, tenant_uuids=[tenant.uuid]
        )


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

    def test_find_by_number(self):
        agent_row = self.add_agent(number='2')

        agent = agent_dao.find_by(number='2')

        assert_that(agent, equal_to(agent_row))
        assert_that(agent.number, equal_to('2'))

    def test_find_by_preprocess_subroutine(self):
        agent_row = self.add_agent(preprocess_subroutine='mysubroutine')

        agent = agent_dao.find_by(preprocess_subroutine='mysubroutine')

        assert_that(agent, equal_to(agent_row))
        assert_that(agent.preprocess_subroutine, equal_to('mysubroutine'))

    def test_given_agent_does_not_exist_then_returns_null(self):
        agent = agent_dao.find_by(id=42)

        assert_that(agent, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        agent_row = self.add_agent()
        agent = agent_dao.find_by(
            firstname=agent_row.firstname, tenant_uuids=[tenant.uuid]
        )
        assert_that(agent, none())

        agent_row = self.add_agent(tenant_uuid=tenant.uuid)
        agent = agent_dao.find_by(
            firstname=agent_row.firstname, tenant_uuids=[tenant.uuid]
        )
        assert_that(agent, equal_to(agent_row))


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

    def test_get_by_number(self):
        agent_row = self.add_agent(number='2')

        agent = agent_dao.get_by(number='2')

        assert_that(agent, equal_to(agent_row))
        assert_that(agent.number, equal_to('2'))

    def test_get_by_preprocess_subroutine(self):
        agent_row = self.add_agent(preprocess_subroutine='MySubroutine')

        agent = agent_dao.get_by(preprocess_subroutine='MySubroutine')

        assert_that(agent, equal_to(agent_row))
        assert_that(agent.preprocess_subroutine, equal_to('MySubroutine'))

    def test_given_agent_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, agent_dao.get_by, id='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        agent_row = self.add_agent()
        self.assertRaises(
            NotFoundError,
            agent_dao.get_by,
            id=agent_row.id,
            tenant_uuids=[tenant.uuid],
        )

        agent_row = self.add_agent(tenant_uuid=tenant.uuid)
        agent = agent_dao.get_by(id=agent_row.id, tenant_uuids=[tenant.uuid])
        assert_that(agent, equal_to(agent_row))


class TestFindAllBy(DAOTestCase):
    def test_find_all_by_no_agent(self):
        result = agent_dao.find_all_by(firstname='toto')

        assert_that(result, contains_exactly())

    def test_find_all_by_custom_column(self):
        pass

    def test_find_all_by_native_column(self):
        agent1 = self.add_agent(preprocess_subroutine='subroutine')
        agent2 = self.add_agent(preprocess_subroutine='subroutine')

        agents = agent_dao.find_all_by(preprocess_subroutine='subroutine')

        assert_that(
            agents,
            has_items(has_property('id', agent1.id), has_property('id', agent2.id)),
        )

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        agent1 = self.add_agent(
            preprocess_subroutine='subroutine', tenant_uuid=tenant.uuid
        )
        agent2 = self.add_agent(preprocess_subroutine='subroutine')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        agents = agent_dao.find_all_by(
            preprocess_subroutine='subroutine', tenant_uuids=tenants
        )
        assert_that(agents, has_items(agent1, agent2))

        tenants = [tenant.uuid]
        agents = agent_dao.find_all_by(
            preprocess_subroutine='subroutine', tenant_uuids=tenants
        )
        assert_that(agents, all_of(has_items(agent1), not_(has_items(agent2))))


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

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        agent1 = self.add_agent()
        agent2 = self.add_agent(tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [agent1, agent2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [agent2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleAgent(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.agent1 = self.add_agent(firstname='Ashton', preprocess_subroutine='resto')
        self.agent2 = self.add_agent(
            firstname='Beaugarton', preprocess_subroutine='bar'
        )
        self.agent3 = self.add_agent(firstname='Casa', preprocess_subroutine='resto')
        self.agent4 = self.add_agent(firstname='Dunkin', preprocess_subroutine='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.agent2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.agent1])
        self.assert_search_returns_result(
            expected_resto, search='ton', preprocess_subroutine='resto'
        )

        expected_bar = SearchResult(1, [self.agent2])
        self.assert_search_returns_result(
            expected_bar, search='ton', preprocess_subroutine='bar'
        )

        expected_all_resto = SearchResult(3, [self.agent1, self.agent3, self.agent4])
        self.assert_search_returns_result(
            expected_all_resto, preprocess_subroutine='resto', order='firstname'
        )

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.agent1, self.agent2, self.agent3, self.agent4])

        self.assert_search_returns_result(expected, order='firstname')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(4, [self.agent4, self.agent3, self.agent2, self.agent1])

        self.assert_search_returns_result(expected, order='firstname', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.agent1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.agent2, self.agent3, self.agent4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.agent2])

        self.assert_search_returns_result(
            expected, search='a', order='firstname', direction='desc', offset=1, limit=1
        )


class TestCreate(DAOTestCase):
    def test_create_minimal_fields(self):
        agent = Agent(number='1234', tenant_uuid=self.default_tenant.uuid)
        created_agent = agent_dao.create(agent)

        row = self.session.query(Agent).first()

        assert_that(created_agent, equal_to(row))
        assert_that(
            created_agent,
            has_properties(
                id=instance_of(int),
                tenant_uuid=self.default_tenant.uuid,
                number='1234',
                firstname=None,
                lastname=None,
                passwd=None,
                language=None,
                description=None,
                preprocess_subroutine=None,
            ),
        )

    def test_create_with_all_fields(self):
        agent = Agent(
            tenant_uuid=self.default_tenant.uuid,
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
        assert_that(
            created_agent,
            has_properties(
                id=instance_of(int),
                tenant_uuid=self.default_tenant.uuid,
                number='1234',
                firstname='first',
                lastname='last',
                passwd='pwd',
                language='en',
                description='description',
                preprocess_subroutine='Subroutine',
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        agent = agent_dao.create(
            Agent(
                tenant_uuid=self.default_tenant.uuid,
                number='1234',
                firstname=None,
                lastname=None,
                passwd=None,
                language=None,
                description=None,
                preprocess_subroutine=None,
            )
        )

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
        assert_that(
            agent,
            has_properties(
                id=instance_of(int),
                number='1234',
                firstname='firstname',
                lastname='lastname',
                passwd='passwd',
                language='en',
                description='desc',
                preprocess_subroutine='routine',
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        agent = self.add_agent()

        agent_dao.delete(agent)

        row = self.session.query(Agent).first()
        assert_that(row, none())


class TestAssociateAgentSkill(DAOTestCase):
    def test_associate(self):
        skill = self.add_queue_skill()
        agent = self.add_agent()

        agent_dao.associate_agent_skill(agent, AgentQueueSkill(skill=skill))

        self.session.expire_all()
        assert_that(
            agent.agent_queue_skills,
            contains_exactly(
                has_properties(
                    agentid=agent.id,
                    skillid=skill.id,
                )
            ),
        )

    def test_association_already_associated(self):
        skill = self.add_queue_skill()
        agent = self.add_agent()
        agent_skill = AgentQueueSkill(skill=skill)

        agent_dao.associate_agent_skill(agent, agent_skill)

        self.session.expire_all()
        agent_dao.associate_agent_skill(agent, agent_skill)

        self.session.expire_all()
        assert_that(agent.agent_queue_skills, contains_exactly(agent_skill))


class TestDissociateAgentSkill(DAOTestCase):
    def test_dissociation(self):
        skill = self.add_queue_skill()
        agent = self.add_agent()
        agent_skill = AgentQueueSkill(skill=skill)
        agent_dao.associate_agent_skill(agent, agent_skill)

        self.session.expire_all()
        agent_dao.dissociate_agent_skill(agent, agent_skill)

        self.session.expire_all()
        assert_that(agent.agent_queue_skills, empty())

        assert_that(inspect(agent_skill).deleted)
        assert_that(not inspect(skill).deleted)
        assert_that(not inspect(agent).deleted)

    def test_dissociation_already_dissociated(self):
        skill = self.add_queue_skill()
        agent = self.add_agent()
        agent_skill = AgentQueueSkill(skill=skill)
        agent_dao.associate_agent_skill(agent, agent_skill)

        self.session.expire_all()
        agent_dao.dissociate_agent_skill(agent, agent_skill)

        self.session.expire_all()
        agent_dao.dissociate_agent_skill(agent, agent_skill)

        self.session.expire_all()
        assert_that(agent.agent_queue_skills, empty())
