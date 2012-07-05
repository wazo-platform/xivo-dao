# -*- coding: UTF-8 -*-

import logging
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.cel import CEL

logger = logging.getLogger(__name__)


def _timedelta_to_seconds(delta):
    return delta.days * 86400 + delta.seconds + delta.microseconds / 1000000.0


class CELException(Exception):
    pass


class MissingCELEventException(CELException):
    pass


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
            return _timedelta_to_seconds(delta)

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


class CELDAO(object):
    def __init__(self, session):
        self._session = session

    def caller_id_by_unique_id(self, unique_id):
        cel_events = (self._session.query(CEL.cid_name, CEL.cid_num)
                      .filter(CEL.eventtype == 'CHAN_START')
                      .filter(CEL.uniqueid == unique_id)
                      .all())
        if not cel_events:
            raise CELException('no such CEL event with uniqueid %s' % unique_id)
        else:
            cid_name, cid_num = cel_events[0]
            return '"%s" <%s>' % (cid_name, cid_num)

    def channel_by_unique_id(self, unique_id):
        cel_events = (self._session.query(CEL)
                      .filter(CEL.uniqueid == unique_id)
                      .all())
        if not cel_events:
            raise CELException('no such CEL event with uniqueid %s' % unique_id)
        else:
            return CELChannel(cel_events)

    def cels_by_linked_id(self, linked_id):
        cel_events = (self._session.query(CEL)
                      .filter(CEL.linkedid == linked_id)
                      .all())
        if not cel_events:
            raise CELException('no such CEL event with linkedid %s' % linked_id)
        else:
            return cel_events

    def _channel_pattern_from_endpoint(self, endpoint):
        return "%s-%%" % endpoint

    def answered_channels_for_endpoint(self, endpoint, limit):
        channel_pattern = self._channel_pattern_from_endpoint(endpoint)
        query = (self._session.query(CEL.uniqueid)
                 .filter(CEL.channame.like(channel_pattern))
                 .filter(CEL.eventtype == 'CHAN_START')
                 .filter(CEL.uniqueid != CEL.linkedid)
                 .order_by(CEL.eventtime.desc()))
        channels = []
        for unique_id, in query:
            try:
                channel = self.channel_by_unique_id(unique_id)
            except CELException, e:
                # this can happen in the case the channel is alive
                logger.info('could not create CEL channel %s: %s', unique_id, e)
            else:
                if channel.is_answered():
                    channels.append(channel)
                    if len(channels) >= limit:
                        break
        return channels

    def missed_channels_for_endpoint(self, endpoint, limit):
        channel_pattern = self._channel_pattern_from_endpoint(endpoint)
        query = (self._session.query(CEL.uniqueid)
                 .filter(CEL.channame.like(channel_pattern))
                 .filter(CEL.eventtype == 'CHAN_START')
                 .filter(CEL.uniqueid != CEL.linkedid)
                 .order_by(CEL.eventtime.desc()))
        channels = []
        for unique_id, in query:
            try:
                channel = self.channel_by_unique_id(unique_id)
            except CELException, e:
                # this can happen in the case the channel is alive
                logger.info('could not create CEL channel %s: %s', unique_id, e)
            else:
                if not channel.is_answered():
                    channels.append(channel)
                    if len(channels) >= limit:
                        break
        return channels

    def outgoing_channels_for_endpoint(self, endpoint, limit):
        channel_pattern = self._channel_pattern_from_endpoint(endpoint)
        query = (self._session.query(CEL.uniqueid)
                 .filter(CEL.channame.like(channel_pattern))
                 .filter(CEL.eventtype == 'CHAN_START')
                 .filter(CEL.uniqueid == CEL.linkedid)
                 .order_by(CEL.eventtime.desc())
                 .limit(limit))
        channels = []
        for unique_id, in query:
            try:
                channel = self.channel_by_unique_id(unique_id)
            except CELException, e:
                # this can happen in the case the channel is alive
                logger.info('could not create CEL channel %s: %s', unique_id, e)
            else:
                channels.append(channel)
                if len(channels) >= limit:
                    break
        return channels

    @classmethod
    def new_from_uri(cls, uri):
        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())
