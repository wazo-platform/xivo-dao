# -*- coding: utf-8 -*-
import datetime
from datetime import datetime as t

from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao import stat_dao

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class TestStatDAO(DAOTestCase):

    tables = [StatAgent, StatQueue, QueueLog, StatCallOnQueue]

    def setUp(self):
        self.empty_tables()
        self.start = t(2012, 07, 01)
        self.end = t(2012, 07, 31, 23, 59, 59, 999999)
        self.qname1, self.qid1 = self._insert_queue('q1')
        self.qname2, self.qid2 = self._insert_queue('q2')
        self.aname1, self.aid1 = self._insert_agent('a1')
        self.aname2, self.aid2 = self._insert_agent('a2')

    def test_fill_answered_calls_empty(self):
        try:
            stat_dao.fill_answered_calls(self.start, self.end)
        except Exception, e:
            print e
            self.assertTrue(False, 'Should not happen')

    def test_fill_answered_transfer(self):
        transfered_calls = [
            (t(2012, 7, 1, 10, 00, 00), 'transfered_1', self.qname1, self.aname1, 5, 25),
            (t(2012, 7, 1, 10, 00, 01), 'transfered_2', self.qname2, self.aname1, 7, 32),
            (t(2012, 7, 1, 10, 59, 59), 'transfered_3', self.qname1, self.aname1, 10, 59),
            (t(2012, 7, 1, 11, 00, 00), 'transfered_4', self.qname1, self.aname2, 3, 13),
            ]
        self._insert_transfered_calls(transfered_calls)

        stat_dao.fill_answered_calls(self.start, self.end)

        result = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid.like('transfered_%'))
        self.assertEqual(result.count(), len(transfered_calls))
        for r in result.all():
            expected = [c for c in transfered_calls if c[1] == r.callid][0]
            self.assertEqual(r.time, expected[0])
            self.assertEqual(r.callid, expected[1])
            qid = self.qid1 if expected[2] == self.qname1 else self.qid2
            self.assertEqual(r.queue_id, qid)
            aid = self.aid1 if expected[3] == self.aname1 else self.aid2
            self.assertEqual(r.agent_id, aid)
            self.assertEqual(r.waittime, expected[4])
            self.assertEqual(r.talktime, expected[5])

    def test_fill_answered_complete(self):
        completed_calls = [
            (t(2012, 7, 1, 10, 00, 00), 'completed_1', self.qname1, self.aname1, 5, 25, True),
            (t(2012, 7, 1, 10, 00, 01), 'completed_2', self.qname2, self.aname1, 7, 32, False),
            (t(2012, 7, 1, 10, 59, 59), 'completed_3', self.qname1, self.aname1, 10, 59, True),
            (t(2012, 7, 1, 11, 00, 00), 'completed_4', self.qname1, self.aname2, 3, 13, False),
            ]
        self._insert_completed_calls(completed_calls)

        stat_dao.fill_answered_calls(self.start, self.end)

        result = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid.like('completed_%'))
        self.assertEqual(result.count(), len(completed_calls))
        for r in result.all():
            expected = [c for c in completed_calls if c[1] == r.callid][0]
            self.assertEqual(r.time, expected[0])
            self.assertEqual(r.callid, expected[1])
            qid = self.qid1 if expected[2] == self.qname1 else self.qid2
            self.assertEqual(r.queue_id, qid)
            aid = self.aid1 if expected[3] == self.aname1 else self.aid2
            self.assertEqual(r.agent_id, aid)
            self.assertEqual(r.waittime, expected[4])
            self.assertEqual(r.talktime, expected[5])

    def test_fill_saturated_calls_empty(self):
        try:
            stat_dao.fill_saturated_calls(self.start, self.end)
        except:
            self.assertTrue(False, 'Should not happen')

    def test_fill_saturated_calls_fulls(self):
        full_calls = [
            (t(2012, 7, 1, 10, 00, 00), 'full_1', self.qname1),
            (t(2012, 7, 1, 10, 59, 59), 'full_2', self.qname2),
            (t(2012, 7, 1, 10, 00, 01), 'full_3', self.qname1),
            (t(2012, 7, 1, 10, 00, 02), 'full_4', self.qname2),
            (t(2012, 7, 1, 10, 00, 03), 'full_5', self.qname1),
            ]

        self._insert_full_calls(full_calls)

        stat_dao.fill_saturated_calls(self.start, self.end)

        result = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid.like('full_%'))
        self.assertEqual(result.count(), len(full_calls))
        for r in result.all():
            cid = r.callid
            if r.queue_id == self.qid1:
                qname = self.qname1
            elif r.queue_id == self.qid2:
                qname = self.qname2
            else:
                raise AssertionError('%s should be in [%s, %s]' % (r.queue_id, self.qid1, self.qid2))
            expected = [c for c in full_calls if c[1] == cid][0]
            self.assertEqual(cid, expected[1])
            self.assertEqual(r.time, expected[0])
            self.assertEqual(qname, expected[2])
            self.assertEqual(r.status, 'full')

    def test_fill_saturated_calls_ca_ratio(self):
        ca_ratio_calls = [
            (t(2012, 7, 1, 10, 00, 00), 'ratio_1', self.qname1),
            (t(2012, 7, 1, 10, 59, 59), 'ratio_2', self.qname2),
            (t(2012, 7, 1, 10, 00, 01), 'ratio_3', self.qname1),
            (t(2012, 7, 1, 10, 00, 02), 'ratio_4', self.qname2),
            (t(2012, 7, 1, 10, 00, 03), 'ratio_5', self.qname1),
            ]

        self._insert_ca_ratio_calls(ca_ratio_calls)

        stat_dao.fill_saturated_calls(self.start, self.end)

        result = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid.like('ratio_%'))
        self.assertEqual(result.count(), len(ca_ratio_calls))
        for r in result.all():
            cid = r.callid
            if r.queue_id == self.qid1:
                qname = self.qname1
            elif r.queue_id == self.qid2:
                qname = self.qname2
            else:
                raise AssertionError('%s should be in [%s, %s]' % (r.queue_id, self.qid1, self.qid2))
            expected = [c for c in ca_ratio_calls if c[1] == cid][0]
            self.assertEqual(cid, expected[1])
            self.assertEqual(r.time, expected[0])
            self.assertEqual(qname, expected[2])
            self.assertEqual(r.status, 'divert_ca_ratio')

    def _insert_transfered_calls(self, transfered_calls):
        map(lambda transfered_call: self._insert_transfered_call(*transfered_call), transfered_calls)

    def _insert_completed_calls(self, completed_calls):
        map(lambda completed_call: self._insert_completed_call(*completed_call), completed_calls)

    def _insert_full_calls(self, full_calls):
        map(lambda full_call: self._insert_full_call(*full_call), full_calls)

    def _insert_ca_ratio_calls(self, ca_ratio_calls):
        map(lambda ca_ratio_call: self._insert_ca_ratio_call(*ca_ratio_call), ca_ratio_calls)

    def _insert_transfered_call(self, time, callid, qname, aname, waittime, talktime):
        enterqueue = QueueLog(
            time=time.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='ENTERQUEUE',
            data2='1001',
            data3='1'
            )

        connect = QueueLog(
            time=(time + datetime.timedelta(seconds=waittime)).strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent=aname,
            event='CONNECT',
            data1=str(waittime),
            data2='1344965966.141',
            data3='1'
            )

        transfer = QueueLog(
            time=(time + datetime.timedelta(seconds=waittime + talktime)).strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent=aname,
            event='TRANSFER',
            data1='s',
            data2='user',
            data3=str(waittime),
            data4=str(talktime)
            )

        self.session.add(enterqueue)
        self.session.add(connect)
        self.session.add(transfer)
        self.session.commit()

    def _insert_completed_call(self, time, callid, qname, aname, waittime, talktime, agent_complete):
        enterqueue = QueueLog(
            time=time.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='ENTERQUEUE',
            data2='1001',
            data3='1'
            )

        connect = QueueLog(
            time=(time + datetime.timedelta(seconds=waittime)).strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent=aname,
            event='CONNECT',
            data1=str(waittime),
            data2='1344965966.141',
            data3='1'
            )

        complete = QueueLog(
            time=(time + datetime.timedelta(seconds=waittime + talktime)).strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent=aname,
            event='COMPLETEAGENT' if agent_complete else 'COMPLETECALLER',
            data1=str(waittime),
            data2=str(talktime)
            )

        self.session.add(enterqueue)
        self.session.add(connect)
        self.session.add(complete)
        self.session.commit()

    def _insert_full_call(self, t, callid, qname):
        full = QueueLog(
            time=t.strftime(TIMESTAMP_FORMAT),
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

    def _insert_agent(self, aname):
        a = StatAgent(name=aname)
        self.session.add(a)
        self.session.commit()
        return a.name, a.id

    def _insert_queue(self, qname):
        q = StatQueue(name=qname)
        self.session.add(q)
        self.session.commit()
        return q.name, q.id

    @classmethod
    def _create_functions(cls):
        ### WARNING: These functions should always be the same as the one in baseconfig
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

        fill_answered_calls_fn = '''\
DROP FUNCTION IF EXISTS "fill_answered_calls" (text, text);
CREATE FUNCTION "fill_answered_calls"(period_start text, period_end text)
  RETURNS void AS
$$
  INSERT INTO stat_call_on_queue (callid, "time", talktime, waittime, queue_id, agent_id, status)
  SELECT
    callid,
    CAST ((SELECT "time" FROM queue_log WHERE callid=outer_queue_log.callid and event='ENTERQUEUE') AS TIMESTAMP) AS "time",
    CASE WHEN event IN ('COMPLETEAGENT', 'COMPLETECALLER') THEN CAST (data2 AS INTEGER)
         WHEN event = 'TRANSFER' THEN CAST (data4 AS INTEGER) END as talktime,
    CASE WHEN event IN ('COMPLETEAGENT', 'COMPLETECALLER') THEN CAST (data1 AS INTEGER)
         WHEN event = 'TRANSFER' THEN CAST (data3 AS INTEGER) END as waittime,
    (SELECT id FROM stat_queue WHERE "name"=queuename) AS queue_id,
    (SELECT id FROM stat_agent WHERE "name"=agent) AS agent_id,
    'answered' AS status
  FROM
    queue_log as outer_queue_log
  WHERE
    callid IN
      (SELECT callid
       FROM queue_log
       WHERE event = 'ENTERQUEUE' AND "time" BETWEEN $1 AND $2)
    AND event IN ('COMPLETEAGENT', 'COMPLETECALLER', 'TRANSFER');
$$
LANGUAGE SQL;
'''
        cls.session.execute(fill_answered_calls_fn)
