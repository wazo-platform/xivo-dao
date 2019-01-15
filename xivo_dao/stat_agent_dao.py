# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.stat_agent import StatAgent


def insert_missing_agents(session):
    session.execute('''\
INSERT INTO stat_agent (name)
  SELECT 'Agent/' || number FROM agentfeatures EXCEPT SELECT name FROM stat_agent
''')


@daosession
def id_from_name(session, agent_name):
    return session.query(StatAgent.id).filter(StatAgent.name == agent_name).first().id


def clean_table(session):
    session.query(StatAgent).delete()
