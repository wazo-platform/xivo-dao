# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.alchemy.staticmeetme import StaticMeetme
from sqlalchemy import func
from xivo_dao.helpers.db_manager import daosession


@daosession
def all(session):
    return session.query(MeetmeFeatures).all()


@daosession
def get(session, meetme_id):
    res = session.query(MeetmeFeatures).filter(MeetmeFeatures.id == int(meetme_id)).first()
    if not res:
        raise LookupError
    return res


@daosession
def _get_by_number(session, number):
    return session.query(MeetmeFeatures).filter(MeetmeFeatures.confno == number)[0]


@daosession
def is_a_meetme(session, number):
    row = (session
           .query(func.count(MeetmeFeatures.confno).label('count'))
           .filter(MeetmeFeatures.confno == number)).first()
    return row.count != 0


@daosession
def find_by_confno(session, meetme_confno):
    res = session.query(MeetmeFeatures).filter(MeetmeFeatures.confno == meetme_confno)
    if res.count() == 0:
        raise LookupError('No such conference room: %s', meetme_confno)
    return res[0].id


def get_name(meetme_id):
    return get(meetme_id).name


@daosession
def has_pin(session, meetme_id):
    meetme = get(meetme_id)
    var_val = session.query(StaticMeetme.var_val).filter(StaticMeetme.id == meetme.meetmeid)
    return _has_pin_from_var_val(var_val[0].var_val)


def _has_pin_from_var_val(var_val):
    try:
        _, pin = var_val.split(',', 1)
    except ValueError:
        return False
    else:
        return len(pin) > 0


@daosession
def get_configs(session):
    res = (session.query(MeetmeFeatures.name, MeetmeFeatures.confno, StaticMeetme.var_val, MeetmeFeatures.context)
           .filter(MeetmeFeatures.meetmeid == StaticMeetme.id))
    return [(r.name, r.confno, _has_pin_from_var_val(r.var_val), r.context) for r in res]


@daosession
def get_config(session, meetme_id):
    res = (session.query(MeetmeFeatures.name, MeetmeFeatures.confno, StaticMeetme.var_val, MeetmeFeatures.context)
           .filter(MeetmeFeatures.meetmeid == StaticMeetme.id)
           .filter(MeetmeFeatures.id == meetme_id))[0]
    return (res.name, res.confno, _has_pin_from_var_val(res.var_val), res.context)


def muted_on_join_by_number(number):
    return _get_by_number(number).user_initiallymuted == 1
