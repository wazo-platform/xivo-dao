# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
