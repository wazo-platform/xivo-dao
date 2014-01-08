# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

import time
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
                       .from_statement('select * from get_queue_statistics('
                                       'cast (:queue_name as text),'
                                       'cast (:in_window as int),'
                                       'cast (:xqos as int))')
                       .params(queue_name=queue_name,
                               in_window=in_window,
                               xqos=xqos)
                       .first())

    return queue_statistic


def _compute_window_time(window):
    return time.time() - window
