# -*- coding: utf-8 -*-

from xivo_dao.alchemy.stat_agent_periodic import StatAgentPeriodic
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao import stat_agent_periodic_dao
from datetime import datetime as dt
from datetime import timedelta
from sqlalchemy import func


ONE_HOUR = timedelta(hours=1)


class TestStatAgentPeriodicDAO(DAOTestCase):

    tables = [StatAgent, StatAgentPeriodic]

    def setUp(self):
        self.empty_tables()

    def _insert_agent_to_stat_agent(self):
        agent = StatAgent()
        agent.name = 'test_agent'

        self.session.add(agent)
        self.session.commit()

        return agent.name, agent.id

    def test_insert_periodic_stat(self):
        _, agent_id_1 = self._insert_agent_to_stat_agent()
        _, agent_id_2 = self._insert_agent_to_stat_agent()
        stats = {
            dt(2012, 01, 01, 01, 00, 00): {
                agent_id_1: {
                    'login_time': timedelta(minutes=50),
                    'pause_time': timedelta(minutes=13)
                },
                agent_id_2: {
                    'login_time': ONE_HOUR,
                    'pause_time': timedelta(minutes=13)},
            },
            dt(2012, 01, 01, 02, 00, 00): {
                agent_id_1: {
                    'login_time': timedelta(minutes=20),
                    'pause_time': timedelta(minutes=33)
                },
                agent_id_2: {
                    'login_time': ONE_HOUR,
                    'pause_time': timedelta(minutes=13)
                },
            },
            dt(2012, 01, 01, 03, 00, 00): {
                agent_id_2: {
                    'login_time': ONE_HOUR,
                    'pause_time': ONE_HOUR
                },
            },
            dt(2012, 01, 01, 04, 00, 00): {
                agent_id_2: {
                    'login_time': ONE_HOUR,
                    'pause_time': ONE_HOUR
                },
            }
        }

        for period_start, agents_stats in stats.iteritems():
            stat_agent_periodic_dao.insert_stats(agents_stats, period_start)

        period_start = dt(2012, 01, 01, 01, 00, 00)

        try:
            result = (self.session.query(StatAgentPeriodic)
                      .filter(StatAgentPeriodic.time == period_start)
                      .filter(StatAgentPeriodic.agent_id == agent_id_1)[0])

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

        stat_agent_periodic_dao.insert_stats(stats, dt(2012, 1, 1))

        stat_agent_periodic_dao.clean_table()

        total = self.session.query(func.count(StatAgentPeriodic.time))[0][0]

        self.assertEqual(total, 0)

    def test_remove_after(self):
        _, agent_id = self._insert_agent_to_stat_agent()
        stats = {
            dt(2012, 1, 1): {
                agent_id: {
                    'login_time': timedelta(minutes=15),
                    'pause_time': timedelta(minutes=13)
                },
            },
            dt(2012, 1, 2): {
                agent_id: {
                    'login_time': timedelta(minutes=20),
                    'pause_time': timedelta(minutes=13)
                },
            },
            dt(2012, 1, 3): {
                agent_id: {
                    'login_time': timedelta(minutes=25),
                    'pause_time': timedelta(minutes=13)
                },
            },
        }

        for period_start, agents_stats in stats.iteritems():
            stat_agent_periodic_dao.insert_stats(agents_stats, period_start)

        stat_agent_periodic_dao.remove_after(dt(2012, 1, 2))

        res = self.session.query(StatAgentPeriodic.time)

        self.assertEqual(res.count(), 1)
        self.assertEqual(res[0].time, dt(2012, 1, 1))
