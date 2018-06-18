# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession

from .persistor import AgentPersistor
from .search import agent_search


@daosession
def search(session, **parameters):
    return AgentPersistor(session, agent_search).search(parameters)


@daosession
def get(session, agent_id):
    return AgentPersistor(session, agent_search).get_by({'id': agent_id})


@daosession
def get_by(session, **criteria):
    return AgentPersistor(session, agent_search).get_by(criteria)


@daosession
def find(session, agent_id):
    return AgentPersistor(session, agent_search).find_by({'id': agent_id})


@daosession
def find_by(session, **criteria):
    return AgentPersistor(session, agent_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return AgentPersistor(session, agent_search).find_all_by(criteria)


@daosession
def create(session, agent):
    return AgentPersistor(session, agent_search).create(agent)


@daosession
def edit(session, agent):
    AgentPersistor(session, agent_search).edit(agent)


@daosession
def delete(session, agent):
    AgentPersistor(session, agent_search).delete(agent)
