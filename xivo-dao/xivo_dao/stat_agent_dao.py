# -*- coding: UTF-8 -*-
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.stat_agent import StatAgent
from sqlalchemy import distinct


_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def insert_if_missing(agents):
    agents = set(agents)
    old_agents = set(r.agent for r in _session().query(distinct(StatAgent.name).label('agent')))

    missing_agents = list(agents - old_agents)

    for agent_name in missing_agents:
        agent = StatAgent()
        agent.name = agent_name
        _session().add(agent)
    _session().commit()


def id_from_name(agent_name):
    return _session().query(StatAgent.id).filter(StatAgent.name == agent_name).first().id
