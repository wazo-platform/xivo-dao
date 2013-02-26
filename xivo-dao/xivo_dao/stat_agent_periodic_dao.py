# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_dao.alchemy.stat_agent_periodic import StatAgentPeriodic


def insert_stats(session, period_stats, period_start):
    session.begin()
    for agent_id, times in period_stats.iteritems():
        entry = StatAgentPeriodic(
            time=period_start,
            login_time=times['login_time'] if 'login_time' in times else '00:00:00',
            pause_time=times['pause_time'] if 'pause_time' in times else '00:00:00',
            wrapup_time=times['wrapup_time'] if 'wrapup_time' in times else '00:00:00',
            agent_id=agent_id,
        )

        session.add(entry)
    session.commit()


def clean_table(session):
    session.query(StatAgentPeriodic).delete()


def remove_after(session, date):
    session.query(StatAgentPeriodic).filter(StatAgentPeriodic.time >= date).delete()
