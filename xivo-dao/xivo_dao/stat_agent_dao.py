# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
