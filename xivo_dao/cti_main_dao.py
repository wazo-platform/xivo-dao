# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
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

from xivo_dao.alchemy.ctimain import CtiMain
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_config(session):
    row = (session.query(CtiMain).first())
    main = {'incoming_tcp': {'CTI': (row.cti_ip, row.cti_port, row.cti_active),
                             'WEBI': (row.webi_ip, row.webi_port, row.webi_active),
                             'INFO': (row.info_ip, row.info_port, row.info_active)},
            'sockettimeout': row.socket_timeout,
            'logintimeout': row.login_timeout,
            'context_separation': row.context_separation,
            'live_reload_conf': row.live_reload_conf,
            'starttls': bool(row.ctis_active)}
    if row.tlscertfile:
        main['certfile'] = row.tlscertfile
    if row.tlsprivkeyfile:
        main['keyfile'] = row.tlsprivkeyfile
    return {'main': main}
