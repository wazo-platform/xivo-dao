# -*- coding: utf-8 -*-
import datetime

from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao import stat_dao


class TestStatDAO(DAOTestCase):

    tables = [StatAgent, StatQueue, QueueLog, StatCallOnQueue]

    def setUp(self):
        self.empty_tables()
        self.start = datetime.datetime(2012, 07, 01)
        self.end = datetime.datetime(2012, 07, 31, 23, 59, 59, 999999)

    def test_fill_saturated_calls_empty(self):
        try:
            stat_dao.fill_saturated_calls(self.start, self.end)
        except:
            self.assertTrue(False, 'Should not happen')

    def test_fill_saturated_calls_fulls(self):
        qname1, qid1 = self._insert_queue('q1')
        qname2, qid2 = self._insert_queue('q2')
        t = datetime.datetime
        full_calls = [
            (t(2012, 7, 1, 10, 00, 00), 'full_1', qname1),
            (t(2012, 7, 1, 10, 59, 59), 'full_2', qname2),
            (t(2012, 7, 1, 10, 00, 01), 'full_3', qname1),
            (t(2012, 7, 1, 10, 00, 02), 'full_4', qname2),
            (t(2012, 7, 1, 10, 00, 03), 'full_5', qname1),
            ]

        self._insert_full_calls(full_calls)

        stat_dao.fill_saturated_calls(self.start, self.end)

        result = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid.like('full_%'))
        self.assertEqual(result.count(), len(full_calls))
        for r in result.all():
            cid = r.callid
            if r.queue_id == qid1:
                qname = qname1
            elif r.queue_id == qid2:
                qname = qname2
            else:
                raise AssertionError('%s should be in [%s, %s]' % (r.queue_id, qid1, qid2))
            expected = [c for c in full_calls if c[1] == cid][0]
            self.assertEqual(cid, expected[1])
            self.assertEqual(r.time, expected[0])
            self.assertEqual(qname, expected[2])
            self.assertEqual(r.status, 'full')

    def test_fill_saturated_calls_ca_ratio(self):
        qname1, qid1 = self._insert_queue('q1')
        qname2, qid2 = self._insert_queue('q2')
        t = datetime.datetime
        ca_ratio_calls = [
            (t(2012, 7, 1, 10, 00, 00), 'ratio_1', qname1),
            (t(2012, 7, 1, 10, 59, 59), 'ratio_2', qname2),
            (t(2012, 7, 1, 10, 00, 01), 'ratio_3', qname1),
            (t(2012, 7, 1, 10, 00, 02), 'ratio_4', qname2),
            (t(2012, 7, 1, 10, 00, 03), 'ratio_5', qname1),
            ]

        self._insert_ca_ratio_calls(ca_ratio_calls)

        stat_dao.fill_saturated_calls(self.start, self.end)

        result = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid.like('ratio_%'))
        self.assertEqual(result.count(), len(ca_ratio_calls))
        for r in result.all():
            cid = r.callid
            if r.queue_id == qid1:
                qname = qname1
            elif r.queue_id == qid2:
                qname = qname2
            else:
                raise AssertionError('%s should be in [%s, %s]' % (r.queue_id, qid1, qid2))
            expected = [c for c in ca_ratio_calls if c[1] == cid][0]
            self.assertEqual(cid, expected[1])
            self.assertEqual(r.time, expected[0])
            self.assertEqual(qname, expected[2])
            self.assertEqual(r.status, 'divert_ca_ratio')

    def _insert_full_calls(self, full_calls):
        map(lambda full_call: self._insert_full_call(*full_call), full_calls)

    def _insert_ca_ratio_calls(self, ca_ratio_calls):
        map(lambda ca_ratio_call: self._insert_ca_ratio_call(*ca_ratio_call), ca_ratio_calls)

    def _insert_full_call(self, t, callid, qname):
        full = QueueLog(
            time=t,
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='FULL'
            )

        self.session.add(full)
        self.session.commit()

    def _insert_ca_ratio_call(self, t, callid, qname):
        call = QueueLog(
            time=t,
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='DIVERT_CA_RATIO'
            )

        self.session.add(call)
        self.session.commit()

    def _insert_queue(self, qname):
        q = StatQueue(name=qname)
        self.session.add(q)
        self.session.commit()
        return q.name, q.id

    @classmethod
    def _create_functions(cls):
        ### WARNING: This function should always be the same as the one in baseconfig
        fill_saturated_calls_fn = '''\
DROP FUNCTION IF EXISTS "fill_saturated_calls" (text, text);
CREATE FUNCTION "fill_saturated_calls"(period_start text, period_end text)
  RETURNS void AS
$$
  -- Insert full, divert_ca_ratio, divert_waittime into stat_call_on_queue
  INSERT INTO "stat_call_on_queue" (callid, "time", queue_id, status)
    SELECT
      callid,
      CAST ("time" AS TIMESTAMP) as "time",
      (SELECT id FROM stat_queue WHERE name=queuename) as queue_id,
      CASE WHEN event = 'FULL' THEN 'full'::call_exit_type
           WHEN event = 'DIVERT_CA_RATIO' THEN 'divert_ca_ratio'
           WHEN event = 'DIVERT_HOLDTIME' THEN 'divert_waittime'
      END as status
    FROM queue_log
    WHERE event = 'FULL' OR event LIKE 'DIVERT_%' AND
          "time" BETWEEN $1 AND $2;
$$
LANGUAGE SQL;
'''
        cls.session.execute(fill_saturated_calls_fn)
