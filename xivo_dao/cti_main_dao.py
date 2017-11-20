# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.ctimain import CtiMain
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_config(session):
    row = (session.query(CtiMain).first())
    main = {'context_separation': row.context_separation,
            'live_reload_conf': row.live_reload_conf,
            'starttls': bool(row.ctis_active)}
    if row.tlscertfile:
        main['certfile'] = row.tlscertfile
    if row.tlsprivkeyfile:
        main['keyfile'] = row.tlsprivkeyfile
    return {'main': main}
