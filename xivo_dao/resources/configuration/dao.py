# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.infos import Infos


@daosession
def is_live_reload_enabled(session):
    infos = session.query(Infos).first()
    return infos.live_reload_enabled


@daosession
def set_live_reload_status(session, data):
    value = data['enabled']
    with flush_session(session):
        session.query(Infos).update({'live_reload_enabled': value})
