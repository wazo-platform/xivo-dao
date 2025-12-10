# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.exc import IntegrityError

from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.helpers.db_manager import daosession


@daosession
def find_or_create_tenant(session, tenant_uuid):
    tenant = session.get(Tenant, tenant_uuid)

    if tenant:
        return tenant

    tenant = Tenant(uuid=tenant_uuid)

    session.begin_nested()
    try:
        session.add(tenant)
        session.commit()
    except IntegrityError:
        session.rollback()
        tenant = session.get(Tenant, tenant_uuid)
    return tenant


@daosession
def find(session):
    return session.query(Tenant).first()
