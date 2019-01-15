# -*- coding: utf-8 -*-
# Copyright 2012-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.helpers.db_manager import daosession
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Integer


@daosession
def get_by_exten(session, incall_exten):
    query = _new_query(session)
    return (query
            .filter(Incall.exten == incall_exten)
            .first())


def _new_query(session):
    return (session
            .query(Incall.id, Dialaction.action, Dialaction.actionarg1)
            .join((Dialaction, Incall.id == cast(Dialaction.categoryval, Integer)))
            .filter(Dialaction.category == 'incall')
            .filter(Dialaction.event == 'answer'))
