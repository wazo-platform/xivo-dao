# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class AgentPersistor(CriteriaBuilderMixin):

    _search_table = Agent

    def __init__(self, session, agent_search):
        self.session = session
        self.agent_search = agent_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Agent)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        agent = self.find_by(criteria)
        if not agent:
            raise errors.not_found('Agent', **criteria)
        return agent

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(Agent)
        rows, total = self.agent_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def create(self, agent):
        self._fill_default_values(agent)
        self.session.add(agent)
        self.session.flush()
        return agent

    def edit(self, agent):
        self.session.add(agent)
        self.session.flush()

    def delete(self, agent):
        self.session.delete(agent)
        self.session.flush()

    def _fill_default_values(self, agent):
        # matches to default AgentGroup in populate.sql
        agent.numgroup = 1

    def associate_agent_skill(self, agent, agent_skill):
        if agent_skill not in agent.agent_queue_skills:
            agent.agent_queue_skills.append(agent_skill)
        self.session.flush()

    def dissociate_agent_skill(self, agent, agent_skill):
        try:
            agent.agent_queue_skills.remove(agent_skill)
            self.session.flush()
        except ValueError:
            pass
