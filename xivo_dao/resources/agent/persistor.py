# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent
from xivo_dao.helpers import errors
from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin, SearchResult


class AgentPersistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = Agent

    def __init__(self, session, agent_search, tenant_uuids=None):
        self.session = session
        self.agent_search = agent_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(Agent)
        query = self.build_criteria(query, criteria)
        if self.tenant_uuids is not None:
            query = query.filter(Agent.tenant_uuid.in_(self.tenant_uuids))
        return query

    def get_by(self, criteria):
        model = self.find_by(criteria)
        if not model:
            raise errors.not_found('Agent', **criteria)
        return model

    def search(self, parameters):
        query = self.session.query(Agent)
        if self.tenant_uuids is not None:
            query = query.filter(Agent.tenant_uuid.in_(self.tenant_uuids))

        rows, total = self.agent_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def associate_agent_skill(self, agent, agent_skill):
        with Session.no_autoflush:
            if agent_skill not in agent.agent_queue_skills:
                agent.agent_queue_skills.append(agent_skill)
        self.session.flush()

    def dissociate_agent_skill(self, agent, agent_skill):
        try:
            agent.agent_queue_skills.remove(agent_skill)
            self.session.flush()
        except ValueError:
            pass
