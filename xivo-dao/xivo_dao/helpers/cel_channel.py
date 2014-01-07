# -*- coding: utf-8 -*-

# Copyright (C) 2009-2013 Avencall
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

import logging
from xivo_dao.helpers.cel_exception import MissingCELEventException

logger = logging.getLogger(__name__)


class CELChannel(object):
    def __init__(self, cel_events):
        self._cel_events = list(cel_events)
        self._chan_start_event = self._get_or_raise_event_by_type('CHAN_START')
        self._hangup_event = self._get_or_raise_event_by_type('HANGUP')
        self._chan_end_event = self._get_or_raise_event_by_type('CHAN_END')

    def _get_event_by_type(self, event_type):
        for cel_event in self._cel_events:
            if cel_event.eventtype == event_type:
                return cel_event
        return None

    def _get_or_raise_event_by_type(self, event_type):
        event = self._get_event_by_type(event_type)
        if event is None:
            raise MissingCELEventException('no CEL event of type %s' % event_type)
        else:
            return event

    def channel_start_time(self):
        return self._chan_start_event.eventtime

    def is_answered(self):
        return self._get_event_by_type('ANSWER') is not None

    def answer_duration(self):
        answer_event = self._get_event_by_type('ANSWER')
        if answer_event is None:
            return 0.0
        else:
            delta = self._hangup_event.eventtime - answer_event.eventtime
            return delta.total_seconds()

    def exten(self):
        chan_start_exten = self._chan_start_event.exten
        exten = chan_start_exten
        if self.is_originate():
            answer_event = self._get_event_by_type('ANSWER')
            if answer_event is None:
                exten = self._hangup_event.cid_name
            else:
                exten = answer_event.cid_name
        return exten

    def linked_id(self):
        return self._chan_start_event.linkedid

    def is_originate(self):
        return self._chan_start_event.exten == u's'

    def is_caller(self):
        return self._chan_start_event.uniqueid == self._chan_start_event.linkedid
