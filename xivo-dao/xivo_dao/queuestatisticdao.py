# -*- coding: UTF-8 -*-

import time
from xivo_dao.alchemy.queueinfo import QueueInfo
from xivo_dao.alchemy import dbconnection
from sqlalchemy import or_
from sqlalchemy.sql.expression import func

NO_VALUE = ""


def _get_session():
    return dbconnection.get_connection('asterisk').get_session()


class QueueStatisticDAO(object):
    def get_received_call_count(self, queue_name, window):
        return (self._query(QueueInfo, window, queue_name)
                .count())

    def get_answered_call_count(self, queue_name, window):
        return (self._query(QueueInfo, window, queue_name)
                .filter(QueueInfo.call_picker != '').count())

    def get_abandonned_call_count(self, queue_name, window):
        return (self._query(QueueInfo, window, queue_name)
                .filter(or_(QueueInfo.call_picker == '', QueueInfo.call_picker == None))
                .filter(QueueInfo.hold_time != None).count())

    def get_answered_call_in_qos_count(self, queue_name, window, xqos):
        return (self._query(QueueInfo, window, queue_name)
                .filter(QueueInfo.call_picker != '')
                .filter(QueueInfo.hold_time <= xqos).count())

    def get_received_and_done(self, queue_name, window):
        return (self._query(QueueInfo, window, queue_name)
                .filter(QueueInfo.hold_time != None).count())

    def get_max_hold_time(self, queue_name, window):
        max_hold_time = (self._query(func.max(QueueInfo.hold_time), window, queue_name)
                .one()[0])
        if(max_hold_time is None):
            return NO_VALUE
        else:
            return max_hold_time

    def get_mean_hold_time(self, queue_name, window):
        mean_hold_time = (self._query(func.avg(QueueInfo.hold_time), window, queue_name)
                          .one()[0])
        if(mean_hold_time is None):
            return NO_VALUE
        else:
            return int(round(mean_hold_time))

    def _compute_window_time(self, window):
        return time.time() - window

    def _query(self, query_function, window, queue_name):
        in_window = self._compute_window_time(window)
        return (_get_session().query(query_function)
                .filter(QueueInfo.call_time_t > in_window)
                .filter(QueueInfo.queue_name == queue_name))
