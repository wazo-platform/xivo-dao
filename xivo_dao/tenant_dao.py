# -*- coding: UTF-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_or_create_tenant(session, tenant_uuid):
    result = session.query(Tenant).filter(Tenant.uuid == tenant_uuid).first()
    if result:
        return result

    tenant = Tenant(uuid=tenant_uuid)
    session.add(tenant)

    return tenant
