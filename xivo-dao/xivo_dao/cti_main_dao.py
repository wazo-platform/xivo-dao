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

from xivo_dao.alchemy.ctimain import CtiMain
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_config(session):
    res = {}
    row = (session.query(CtiMain).first())
    main = {}
    main['incoming_tcp'] = {}
    main['incoming_tcp']['CTI'] = (row.cti_ip, row.cti_port, row.cti_active)
    main['incoming_tcp']['CTIS'] = (row.ctis_ip, row.ctis_port, row.ctis_active)
    main['incoming_tcp']['WEBI'] = (row.webi_ip, row.webi_port, row.webi_active)
    main['incoming_tcp']['INFO'] = (row.info_ip, row.info_port, row.info_active)
    main['certfile'] = row.tlscertfile
    main['keyfile'] = row.tlsprivkeyfile
    main['sockettimeout'] = row.socket_timeout
    main['logintimeout'] = row.login_timeout
    main['context_separation'] = row.context_separation
    main['live_reload_conf'] = row.live_reload_conf
    res['main'] = main
    res['ipbx_connection'] = {}
    res['ipbx_connection']['ipaddress'] = row.ami_ip
    res['ipbx_connection']['ipport'] = row.ami_port
    res['ipbx_connection']['username'] = row.ami_login
    res['ipbx_connection']['password'] = row.ami_password
    return res
