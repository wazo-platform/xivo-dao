# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import AgentPersistor
from .search import agent_search


@daosession
def search(session, tenant_uuids=None, **parameters):
    return AgentPersistor(session, agent_search, tenant_uuids).search(parameters)


@daosession
def get(session, agent_id, tenant_uuids=None):
    return AgentPersistor(session, agent_search, tenant_uuids).get_by({'id': agent_id})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return AgentPersistor(session, agent_search, tenant_uuids).get_by(criteria)


@daosession
def find(session, agent_id, tenant_uuids=None):
    return AgentPersistor(session, agent_search, tenant_uuids).find_by({'id': agent_id})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return AgentPersistor(session, agent_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return AgentPersistor(session, agent_search, tenant_uuids).find_all_by(criteria)


@daosession
def create(session, agent):
    return AgentPersistor(session, agent_search).create(agent)


@daosession
def edit(session, agent):
    AgentPersistor(session, agent_search).edit(agent)


@daosession
def delete(session, agent):
    AgentPersistor(session, agent_search).delete(agent)


@daosession
def associate_agent_skill(session, agent, agent_skill):
    AgentPersistor(session, agent_search).associate_agent_skill(agent, agent_skill)


@daosession
def dissociate_agent_skill(session, agent, agent_skill):
    AgentPersistor(session, agent_search).dissociate_agent_skill(agent, agent_skill)
