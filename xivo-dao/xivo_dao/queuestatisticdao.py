# -*- coding: UTF-8 -*-

import time
from xivo_dao.alchemy.dbconnection import get_connection


def _get_session():
    return get_connection('asterisk').get_session()


class QueueStatisticDAO(object):

    def get_statistics(self, queue_name, window, xqos):
        in_window = self._compute_window_time(window)
        queue_statistic = (_get_session()
                           .query('received_call_count',
                                  'answered_call_count',
                                  'answered_call_in_qos_count',
                                  'abandonned_call_count',
                                  'received_and_done',
                                  'max_hold_time',
                                  'mean_hold_time')
                           .from_statement('select * from get_queue_statistics('
                                           'cast (:queue_name as text),'
                                           'cast (:in_window as int),'
                                           'cast (:xqos as int))')
                           .params(queue_name=queue_name,
                                   in_window=in_window,
                                   xqos=xqos)
                           .first())

        return queue_statistic

    def _compute_window_time(self, window):
        return time.time() - window
