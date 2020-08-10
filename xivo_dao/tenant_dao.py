# -*- coding: utf-8 -*-
# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.helpers.db_manager import daosession


@daosession
def find_or_create_tenant(session, tenant_uuid):
    result = session.query(Tenant).get(tenant_uuid)
    if result:
        return result

    tenant = Tenant(uuid=tenant_uuid)
    session.add(tenant)
    session.flush()

    return tenant


@daosession
def find(session):
    return session.query(Tenant).first()
