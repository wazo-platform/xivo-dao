# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import six

from datetime import datetime as dt
from datetime import timedelta
from sqlalchemy import func
from pytz import UTC

from xivo_dao import stat_agent_periodic_dao
from xivo_dao.alchemy.stat_agent_periodic import StatAgentPeriodic
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.tests.test_dao import DAOTestCase


ONE_HOUR = timedelta(hours=1)


class TestStatAgentPeriodicDAO(DAOTestCase):

    def _insert_agent_to_stat_agent(self):
        agent = StatAgent()
        agent.name = 'test_agent'
        agent.tenant_uuid = self.default_tenant.uuid

        self.add_me(agent)

        return agent.name, agent.id

    def test_insert_periodic_stat(self):
        _, agent_id_1 = self._insert_agent_to_stat_agent()
        _, agent_id_2 = self._insert_agent_to_stat_agent()
        stats = {
            dt(2012, 1, 1, 1, 0, 0, tzinfo=UTC): {
                agent_id_1: {
                    'login_time': timedelta(minutes=50),
                    'pause_time': timedelta(minutes=13)
                },
                agent_id_2: {
                    'login_time': ONE_HOUR,
                    'pause_time': timedelta(minutes=13)},
            },
            dt(2012, 1, 1, 2, 0, 0, tzinfo=UTC): {
                agent_id_1: {
                    'login_time': timedelta(minutes=20),
                    'pause_time': timedelta(minutes=33)
                },
                agent_id_2: {
                    'login_time': ONE_HOUR,
                    'pause_time': timedelta(minutes=13)
                },
            },
            dt(2012, 1, 1, 3, 0, 0, tzinfo=UTC): {
                agent_id_2: {
                    'login_time': ONE_HOUR,
                    'pause_time': ONE_HOUR
                },
            },
            dt(2012, 1, 1, 4, 0, 0, tzinfo=UTC): {
                agent_id_2: {
                    'login_time': ONE_HOUR,
                    'pause_time': ONE_HOUR
                },
            }
        }

        with flush_session(self.session):
            for period_start, agents_stats in six.iteritems(stats):
                stat_agent_periodic_dao.insert_stats(self.session, agents_stats, period_start)

        period_start = dt(2012, 1, 1, 1, 0, 0, tzinfo=UTC)

        try:
            result = (self.session.query(StatAgentPeriodic)
                      .filter(StatAgentPeriodic.time == period_start)
                      .filter(StatAgentPeriodic.stat_agent_id == agent_id_1)[0])

            self.assertEqual(result.login_time, timedelta(minutes=50))
        except LookupError:
            self.fail('Should have found a row')

    def test_clean_table(self):
        _, agent_id = self._insert_agent_to_stat_agent()
        stats = {
            agent_id: {
                'login_time': timedelta(minutes=15),
                'pause_time': ONE_HOUR
            },
        }

        stat_agent_periodic_dao.insert_stats(self.session, stats, dt(2012, 1, 1, tzinfo=UTC))

        stat_agent_periodic_dao.clean_table(self.session)

        total = self.session.query(func.count(StatAgentPeriodic.time))[0][0]

        self.assertEqual(total, 0)

    def test_remove_after(self):
        _, agent_id = self._insert_agent_to_stat_agent()
        stats = {
            dt(2012, 1, 1, tzinfo=UTC): {
                agent_id: {
                    'login_time': timedelta(minutes=15),
                    'pause_time': timedelta(minutes=13)
                },
            },
            dt(2012, 1, 2, tzinfo=UTC): {
                agent_id: {
                    'login_time': timedelta(minutes=20),
                    'pause_time': timedelta(minutes=13)
                },
            },
            dt(2012, 1, 3, tzinfo=UTC): {
                agent_id: {
                    'login_time': timedelta(minutes=25),
                    'pause_time': timedelta(minutes=13)
                },
            },
        }

        with flush_session(self.session):
            for period_start, agents_stats in six.iteritems(stats):
                stat_agent_periodic_dao.insert_stats(self.session, agents_stats, period_start)

        stat_agent_periodic_dao.remove_after(self.session, dt(2012, 1, 2, tzinfo=UTC))

        res = self.session.query(StatAgentPeriodic.time)

        self.assertEqual(res.count(), 1)
        self.assertEqual(res[0].time, dt(2012, 1, 1, tzinfo=UTC))
