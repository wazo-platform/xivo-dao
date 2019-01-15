# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.ctimain import CtiMain


@daosession
def is_live_reload_enabled(session):
    ctimain = session.query(CtiMain).first()
    return ctimain.live_reload_conf == 1


@daosession
def set_live_reload_status(session, data):
    value = 1 if data['enabled'] else 0
    with flush_session(session):
        session.query(CtiMain).update({'live_reload_conf': value})
