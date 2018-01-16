# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import time

from sqlalchemy.sql import text
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_statistics(session, queue_name, window, xqos):
    in_window = _compute_window_time(window)
    queue_statistic = (session
                       .query('received_call_count',
                              'answered_call_count',
                              'answered_call_in_qos_count',
                              'abandonned_call_count',
                              'received_and_done',
                              'max_hold_time',
                              'mean_hold_time')
                       .from_statement(text('select * from get_queue_statistics('
                                            'cast (:queue_name as text),'
                                            'cast (:in_window as int),'
                                            'cast (:xqos as int))'))
                       .params(queue_name=queue_name,
                               in_window=in_window,
                               xqos=xqos)
                       .first())

    return queue_statistic


def _compute_window_time(window):
    return time.time() - window
