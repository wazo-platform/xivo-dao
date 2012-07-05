# -*- coding: UTF-8 -*-

import unittest
from xivo_dao import queue_log_dao
from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.base import Base
import datetime


class TestQueueLogDAO(unittest.TestCase):

    tables = [QueueLog]

    @classmethod
    def setUpClass(cls):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        cls.session = connection.get_session()

        engine = connection.get_engine()
        Base.metadata.drop_all(engine, [table.__table__ for table in cls.tables])
        Base.metadata.create_all(engine, [table.__table__ for table in cls.tables])
        engine.dispose()

    @classmethod
    def tearDownClass(cls):
        dbconnection.unregister_db_connection_pool()

    def _empty_tables(self):
        for table in self.tables:
            entries = self.session.query(table)
            if entries.count() > 0:
                map(self.session.delete, entries)

    def setUp(self):
        self._empty_tables()

    def _insert_entry_queue_full(self, timestamp, callid, queuename):
        queue_log = QueueLog()
        queue_log.time = timestamp
        queue_log.callid = callid
        queue_log.queuename = queuename
        queue_log.event = 'FULL'
        self.session.add(queue_log)
        self.session.commit()

    @staticmethod
    def _build_date(year, month, day, hour=0, minute=0, second=0, micro=0):
        return datetime.datetime(year, month, day, hour, minute, second, micro).strftime("%Y-%m-%d %H:%M:%S.%f")

    def test_get_queue_full_call(self):
        queuename = 'q1'
        expected_result = []
        for minute in [0, 10, 20, 30, 40, 50]:
            datetimewithmicro = self._build_date(2012, 01, 01, 00, minute, 00)
            callid = str(12345678.123 + minute)
            self._insert_entry_queue_full(datetimewithmicro, callid, queuename)
            expected_result.append({'queue_name': queuename,
                                    'event': 'full',
                                    'time': datetimewithmicro,
                                    'callid': callid})
        after = self._build_date(2012, 01, 02, 00, 00, 00)
        self._insert_entry_queue_full(after, '1234.123', queuename)

        before = self._build_date(2011, 12, 31, 00, 00, 00)
        self._insert_entry_queue_full(before, '5555555.123', queuename)

        datetimestart = self._build_date(2012, 01, 01, 00, 00, 00)
        datetimeend = self._build_date(2012, 01, 01, 00, 59, 59)

        result = queue_log_dao.get_queue_full_call(datetimestart, datetimeend)

        self.assertEqual(sorted(result), sorted(expected_result))
