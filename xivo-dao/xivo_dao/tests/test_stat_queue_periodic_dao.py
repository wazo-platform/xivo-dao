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

import datetime

from xivo_dao.alchemy.stat_queue_periodic import StatQueuePeriodic
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao import stat_queue_periodic_dao
from sqlalchemy import func


class TestStatQueuePeriodicDAO(DAOTestCase):

    tables = [StatQueue, StatQueuePeriodic]

    def setUp(self):
        self.empty_tables()

    def _insert_queue_to_stat_queue(self):
        queue = StatQueue()
        queue.name = 'test_queue'

        self.session.begin()
        self.session.add(queue)
        self.session.commit()

        return queue.name, queue.id

    def _get_stats_for_queue(self):
        queue_name, queue_id = self._insert_queue_to_stat_queue()
        stats = {
            queue_id: {
                'abandoned': 7,
                'answered': 27,
                'closed': 5,
                'full': 4,
                'joinempty': 2,
                'leaveempty': 11,
                'timeout': 5,
                'divert_ca_ratio': 22,
                'divert_waittime': 15,
                'total': 98
            }
        }
        return stats

    def test_insert_periodic_stat(self):
        stats = self._get_stats_for_queue()
        period_start = datetime.datetime(2012, 01, 01, 00, 00, 00)

        self.session.begin()
        stat_queue_periodic_dao.insert_stats(self.session, stats, period_start)
        self.session.commit()

        try:
            result = (self.session.query(StatQueuePeriodic)
                      .filter(StatQueuePeriodic.time == period_start)[0])

            self.assertEqual(result.abandoned, 7)
            self.assertEqual(result.answered, 27)
            self.assertEqual(result.closed, 5)
            self.assertEqual(result.full, 4)
            self.assertEqual(result.joinempty, 2)
            self.assertEqual(result.leaveempty, 11)
            self.assertEqual(result.timeout, 5)
            self.assertEqual(result.divert_ca_ratio, 22)
            self.assertEqual(result.divert_waittime, 15)
            self.assertEqual(result.total, 98)
        except LookupError:
            self.fail('Should have found a row')

    def test_get_most_recent_time(self):
        self.assertRaises(LookupError, stat_queue_periodic_dao.get_most_recent_time, self.session)

        stats = self._get_stats_for_queue()
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)

        self.session.begin()
        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_queue_periodic_dao.insert_stats(self.session, stats, time)
        self.session.commit()

        result = stat_queue_periodic_dao.get_most_recent_time(self.session)
        expected = start + datetime.timedelta(minutes=120)

        self.assertEqual(result, expected)

    def test_clean_table(self):
        queue_name, queue_id = self._insert_queue_to_stat_queue()
        stats = {
            queue_id: {
                'full': 4,
                'total': 10
            }
        }
        period_start = datetime.datetime(2012, 01, 01, 00, 00, 00)

        stat_queue_periodic_dao.insert_stats(self.session, stats, period_start)

        stat_queue_periodic_dao.clean_table(self.session)

        total = self.session.query(func.count(StatQueuePeriodic.time))[0][0]

        self.assertEqual(total, 0)

    def test_remove_after(self):
        queue_name, queue_id = self._insert_queue_to_stat_queue()
        stats = {
            queue_id: {
                'full': 4,
                'total': 10
            }
        }

        self.session.begin()
        stat_queue_periodic_dao.insert_stats(self.session, stats, datetime.datetime(2012, 1, 1))
        stat_queue_periodic_dao.insert_stats(self.session, stats, datetime.datetime(2012, 1, 2))
        stat_queue_periodic_dao.insert_stats(self.session, stats, datetime.datetime(2012, 1, 3))
        self.session.commit()

        stat_queue_periodic_dao.remove_after(self.session, datetime.datetime(2012, 1, 2))

        res = self.session.query(StatQueuePeriodic.time)

        self.assertEqual(res.count(), 1)
        self.assertEqual(res[0].time, datetime.datetime(2012, 1, 1))
