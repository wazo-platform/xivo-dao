# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.alchemy.voicemail import Voicemail
from sqlalchemy.sql.expression import and_, cast
from sqlalchemy.types import Integer

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def get(incall_id):
    return _session().query(Incall).filter(Incall.id == incall_id).first()


def get_join_elements(incall_id):
    return (_session().query(Incall, Dialaction, UserFeatures, GroupFeatures, QueueFeatures, MeetmeFeatures, Voicemail)
            .join((Dialaction, Incall.id == cast(Dialaction.categoryval, Integer)))
            .outerjoin((UserFeatures, and_(UserFeatures.id == cast(Dialaction.actionarg1, Integer),
                                           Dialaction.action == u'user')))
            .outerjoin((GroupFeatures, and_(GroupFeatures.id == cast(Dialaction.actionarg1, Integer),
                                            Dialaction.action == u'group')))
            .outerjoin((QueueFeatures, and_(QueueFeatures.id == cast(Dialaction.actionarg1, Integer),
                                            Dialaction.action == u'queue')))
            .outerjoin((MeetmeFeatures, and_(MeetmeFeatures.id == cast(Dialaction.actionarg1, Integer),
                                             Dialaction.action == u'meetme')))
            .outerjoin((Voicemail, and_(Voicemail.uniqueid == cast(Dialaction.actionarg1, Integer),
                                        Dialaction.action == u'voicemail')))
            .filter(and_(Dialaction.event == u'answer',
                         Dialaction.category == u'incall',
                         Incall.id == incall_id))
            .first())


def all():
    return (_session().query(Incall, Dialaction, UserFeatures, GroupFeatures, QueueFeatures, MeetmeFeatures, Voicemail)
            .join((Dialaction, Incall.id == cast(Dialaction.categoryval, Integer)))
            .outerjoin((UserFeatures, and_(UserFeatures.id == cast(Dialaction.actionarg1, Integer),
                                           Dialaction.action == u'user')))
            .outerjoin((GroupFeatures, and_(GroupFeatures.id == cast(Dialaction.actionarg1, Integer),
                                            Dialaction.action == u'group')))
            .outerjoin((QueueFeatures, and_(QueueFeatures.id == cast(Dialaction.actionarg1, Integer),
                                            Dialaction.action == u'queue')))
            .outerjoin((MeetmeFeatures, and_(MeetmeFeatures.id == cast(Dialaction.actionarg1, Integer),
                                             Dialaction.action == u'meetme')))
            .outerjoin((Voicemail, and_(Voicemail.uniqueid == cast(Dialaction.actionarg1, Integer),
                                        Dialaction.action == u'voicemail')))
            .filter(and_(Dialaction.event == u'answer',
                         Dialaction.category == u'incall'))
            .all())
