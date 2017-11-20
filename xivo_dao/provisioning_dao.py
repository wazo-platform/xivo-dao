# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.provisioning import Provisioning
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_provd_rest_host_and_port(session):
    return session.query(Provisioning.net4_ip_rest, Provisioning.rest_port).first()
